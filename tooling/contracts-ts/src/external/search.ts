import { z } from "zod";

export const SearchBackendSchema = z.enum([
  "exa",
  "searxng",
  "duckduckgo",
  "google_search_package",
  "website_scrape",
  "unknown",
]);

export const EvidenceClassSchema = z.enum([
  "authoritative_api",
  "structured_search",
  "metasearch",
  "heuristic_search",
  "website_scrape",
]);

export const SearchResultSchema = z.object({
  title: z.string(),
  url: z.string().url(),
  snippet: z.string(),
  source: z.string(),
  backend: SearchBackendSchema,
  evidenceClass: EvidenceClassSchema,
  date: z.string().datetime().nullable().optional(),
});

export type SearchBackend = z.infer<typeof SearchBackendSchema>;
export type EvidenceClass = z.infer<typeof EvidenceClassSchema>;
export type SearchResult = z.infer<typeof SearchResultSchema>;
