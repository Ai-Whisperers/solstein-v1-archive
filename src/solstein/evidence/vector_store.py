"""
Qdrant Vector Store - Semantic search for claims and documents.

This module provides vector search capabilities for EPIC-042.

FREE tools used:
- Qdrant (open source, local)
- sentence-transformers (local embeddings)
"""

from __future__ import annotations

import logging

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from .models import Claim

logger = logging.getLogger(__name__)


class EvidenceVectorStore:
    """
    Vector store for semantic search of claims and documents.

    Uses Qdrant (open source) with local embeddings.
    """

    COLLECTION_NAME = "evidence_claims"
    VECTOR_SIZE = 384  # all-MiniLM-L6-v2 embedding size

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        embedding_model: str | None = None,
    ):
        self.host = host
        self.port = port
        self.client: QdrantClient | None = None
        self._embedding_model = embedding_model
        self._embedder = None

    def connect(self) -> None:
        """Connect to Qdrant."""
        self.client = QdrantClient(host=self.host, port=self.port)
        logger.info(f"Connected to Qdrant at {self.host}:{self.port}")

    def init_collection(self) -> None:
        """Initialize the evidence claims collection."""
        if self.client is None:
            raise RuntimeError("Not connected to Qdrant. Call connect() first.")
        # Check if collection exists
        collections = self.client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if self.COLLECTION_NAME not in collection_names:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(f"Created collection: {self.COLLECTION_NAME}")
        else:
            logger.info(f"Collection {self.COLLECTION_NAME} already exists")

    def _get_embedder(self):
        """Lazy load the embedding model."""
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer

                model_name = self._embedding_model or "all-MiniLM-L6-v2"
                self._embedder = SentenceTransformer(model_name)
                logger.info(f"Loaded embedding model: {model_name}")
            except ImportError:
                logger.error("sentence-transformers not installed. Run: pip install sentence-transformers")
                raise
        return self._embedder

    def _embed(self, text: str) -> list[float]:
        """Generate embedding for text."""
        embedder = self._get_embedder()
        embedding = embedder.encode(text).tolist()
        return embedding

    def index_claim(self, claim: Claim) -> None:
        """Index a claim for semantic search."""
        # Create searchable text from claim
        searchable_text = f"""
        Entity: {claim.entity_id}
        Field: {claim.field}
        Value: {claim.value}
        Snippet: {claim.snippet}
        Source: {claim.source_url}
        """.strip()

        # Generate embedding
        vector = self._embed(searchable_text)

        # Create point
        point = PointStruct(
            id=str(claim.id),
            vector=vector,
            payload={
                "claim_id": str(claim.id),
                "entity_id": claim.entity_id,
                "entity_type": claim.entity_type,
                "field": claim.field,
                "value": str(claim.value),
                "unit": claim.unit,
                "snippet": claim.snippet,
                "source_url": claim.source_url,
                "source_type": claim.source_type.value,
                "confidence": claim.overall_confidence,
                "status": claim.status.value,
                "extracted_at": claim.extracted_at.isoformat(),
            },
        )

        # Upsert to Qdrant
        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[point],
        )

        logger.info(f"Indexed claim: {claim.id}")

    def search_similar_claims(
        self,
        query: str,
        entity_id: str | None = None,
        field: str | None = None,
        min_confidence: float = 0.0,
        limit: int = 10,
    ) -> list[dict]:
        """Search for claims similar to the query."""
        # Generate query embedding
        query_vector = self._embed(query)

        # Build filter
        must_conditions = []

        if entity_id:
            must_conditions.append(
                FieldCondition(
                    key="entity_id",
                    match=MatchValue(value=entity_id),
                )
            )

        if field:
            must_conditions.append(
                FieldCondition(
                    key="field",
                    match=MatchValue(value=field),
                )
            )

        # Search

        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_vector,
            query_filter=Filter(must=must_conditions) if must_conditions else None,
            limit=limit,
            score_threshold=min_confidence,
        ).points

        return [
            {
                "claim_id": r.payload["claim_id"],
                "entity_id": r.payload["entity_id"],
                "field": r.payload["field"],
                "value": r.payload["value"],
                "snippet": r.payload["snippet"],
                "source_url": r.payload["source_url"],
                "confidence": r.payload["confidence"],
                "similarity_score": r.score,
            }
            for r in results
        ]

    def find_contradictory_claims(
        self,
        claim: Claim,
        similarity_threshold: float = 0.85,
    ) -> list[dict]:
        """
        Find claims that might contradict the given claim.

        Uses semantic similarity to find claims about the same topic
        with potentially conflicting values.
        """
        # Search for similar claims
        similar = self.search_similar_claims(
            query=claim.snippet,
            entity_id=claim.entity_id,
            field=claim.field,
            limit=20,
        )

        # Filter out the claim itself and find potential contradictions
        # (different values for same field)
        contradictory = [
            s
            for s in similar
            if s["claim_id"] != str(claim.id)
            and s["value"] != str(claim.value)
            and s["similarity_score"] >= similarity_threshold
        ]

        return contradictory

    def delete_claim(self, claim_id: str) -> None:
        """Remove a claim from the vector store."""
        self.client.delete(
            collection_name=self.COLLECTION_NAME,
            points_selector=[claim_id],
        )
        logger.info(f"Deleted claim from vector store: {claim_id}")

    def get_stats(self) -> dict:
        """Get collection statistics."""
        collection_info = self.client.get_collection(self.COLLECTION_NAME)
        return {
            "vectors_count": collection_info.vectors_count,
            "indexed_vectors_count": collection_info.indexed_vectors_count,
            "points_count": collection_info.points_count,
            "status": collection_info.status,
        }


if __name__ == "__main__":
    # Test the vector store
    store = EvidenceVectorStore()
    store.connect()
    store.init_collection()

    # Test indexing
    from .models import SourceType, create_claim

    claim = create_claim(
        entity_id="test-company-002",
        field="headquarters",
        value="San Francisco, CA",
        source_url="https://example.com/careers",
        snippet="Join our team in San Francisco",
        source_type=SourceType.WEBSITE,
    )
    claim.overall_confidence = 0.9

    try:
        store.index_claim(claim)

        # Test search
        results = store.search_similar_claims(
            query="company location San Francisco",
            entity_id="test-company-002",
        )
        print(f"Found {len(results)} similar claims")

        # Test stats
        stats = store.get_stats()
        print(f"Collection stats: {stats}")

        print("✅ Vector store test passed!")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise
