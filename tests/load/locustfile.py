import random

from locust import HttpUser, between, task


class SolsteinUser(HttpUser):
    """Simulates user behavior on Solstein API."""

    wait_time = between(1, 5)

    def on_start(self):
        """Login or setup before starting tasks."""
        # Add authentication if needed
        pass

    @task(10)
    def get_health(self):
        """Check health endpoint."""
        self.client.get("/health")

    @task(5)
    def list_companies(self):
        """List companies endpoint."""
        self.client.get("/api/v1/companies", params={"limit": 20, "offset": 0})

    @task(3)
    def get_company(self):
        """Get specific company."""
        company_id = random.randint(1, 1000)
        self.client.get(f"/api/v1/companies/{company_id}")

    @task(2)
    def search_companies(self):
        """Search companies."""
        search_terms = ["tech", "ai", "software", "fintech", "health"]
        term = random.choice(search_terms)
        self.client.get("/api/v1/companies/search", params={"q": term})

    @task(1)
    def create_analysis(self):
        """Create competitive analysis."""
        payload = {
            "company_id": random.randint(1, 1000),
            "analysis_type": random.choice(["competitive", "market", "financial"]),
        }
        self.client.post("/api/v1/analysis", json=payload)
