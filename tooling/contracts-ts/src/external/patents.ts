import { z } from "zod";

export const PatentBackendSchema = z.enum([
  "uspto_peds",
  "google_patents",
  "duckduckgo",
  "none",
]);

export const PatentSearchResultSchema = z.object({
  totalPatents: z.number().int().nonnegative(),
  recentPatents: z.array(z.record(z.unknown())).default([]),
  aiRelatedPatents: z.number().int().nonnegative(),
  topCategories: z.array(z.string()).default([]),
  source: PatentBackendSchema,
});

export const PatentPortfolioFactValueSchema = z.object({
  total_patents: z.number().int().nonnegative(),
  recent_patents: z.array(z.record(z.unknown())).default([]),
  ai_related_patents: z.number().int().nonnegative(),
  top_categories: z.array(z.string()).default([]),
  source_backend: PatentBackendSchema,
});

export type PatentBackend = z.infer<typeof PatentBackendSchema>;
export type PatentSearchResult = z.infer<typeof PatentSearchResultSchema>;
export type PatentPortfolioFactValue = z.infer<typeof PatentPortfolioFactValueSchema>;
