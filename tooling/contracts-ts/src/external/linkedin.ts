import { z } from "zod";

export const LinkedInAcquisitionMethodSchema = z.enum([
  "official_linkedin_api",
  "proxycurl",
  "news_heuristic",
]);

export const LinkedInAuthoritySchema = z.enum([
  "authoritative",
  "proxy",
  "heuristic",
]);

export const LinkedInHeuristicDataSchema = z.object({
  companyName: z.string(),
  employeeCount: z.number().int().nonnegative().nullable(),
  employeeGrowthPct: z.number().nullable(),
  openPositions: z.number().int().nonnegative().nullable(),
  aiRelatedPositions: z.number().int().nonnegative().nullable(),
  recentHires: z.array(z.record(z.unknown())).default([]),
  companySize: z.string().nullable().optional(),
  acquisitionMethod: LinkedInAcquisitionMethodSchema,
  authority: LinkedInAuthoritySchema,
});

export type LinkedInHeuristicData = z.infer<typeof LinkedInHeuristicDataSchema>;
