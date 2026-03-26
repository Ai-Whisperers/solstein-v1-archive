import { z } from "zod";

export const BatchEnrichmentOutcomeStatusSchema = z.enum([
  "success",
  "partial",
  "failure",
]);

export const BatchEnrichmentOutcomeSchema = z.object({
  companyId: z.string().min(1),
  companyName: z.string().min(1).nullable().optional(),
  status: BatchEnrichmentOutcomeStatusSchema,
  errors: z.array(z.string()).default([]),
  fromCache: z.boolean().default(false),
});

export type BatchEnrichmentOutcomeStatus = z.infer<typeof BatchEnrichmentOutcomeStatusSchema>;
export type BatchEnrichmentOutcome = z.infer<typeof BatchEnrichmentOutcomeSchema>;
