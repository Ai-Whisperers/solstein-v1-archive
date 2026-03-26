import { z } from "zod";

import { LinkedInAuthoritySchema, LinkedInAcquisitionMethodSchema } from "./linkedin.js";
import { EvidenceClassSchema, SearchBackendSchema } from "./search.js";

export const EvidenceEnvelopeSchema = z.object({
  source: z.string(),
  backend: SearchBackendSchema.optional(),
  evidenceClass: EvidenceClassSchema,
  authority: LinkedInAuthoritySchema.or(z.literal("not_applicable")),
  acquisitionMethod: LinkedInAcquisitionMethodSchema.or(z.literal("not_applicable")),
  confidence: z.number().min(0).max(1),
  extractedAt: z.string().datetime(),
  payload: z.record(z.unknown()),
  metadata: z.record(z.unknown()).default({}),
});

export type EvidenceEnvelope = z.infer<typeof EvidenceEnvelopeSchema>;
