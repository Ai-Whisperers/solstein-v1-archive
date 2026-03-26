import { z } from "zod";

const ConnectorFactBaseSchema = z.object({
  company_id: z.string().min(1),
  fact_type: z.string().min(1).optional(),
  type: z.string().min(1).optional(),
  value: z.unknown().nullable().optional(),
  confidence: z.number().min(0).max(1).default(0.5),
  extracted_at: z.string().datetime().nullable().optional(),
  metadata: z.record(z.unknown()).nullable().optional(),
  _hash: z.string().min(1).optional(),
}).passthrough();

export const ConnectorFactInputSchema = ConnectorFactBaseSchema.superRefine((payload, ctx) => {
  if (!payload.fact_type && !payload.type) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: "fact_type or legacy type is required",
      path: ["fact_type"],
    });
  }
}).transform((payload) => ({
  ...payload,
  fact_type: payload.fact_type ?? payload.type!,
  metadata: payload.metadata ?? {},
}));

export const ConnectorFactSchema = z.object({
  company_id: z.string().min(1),
  fact_type: z.string().min(1),
  value: z.unknown().nullable().optional(),
  confidence: z.number().min(0).max(1).default(0.5),
  extracted_at: z.string().datetime().nullable().optional(),
  metadata: z.record(z.unknown()).default({}),
  _hash: z.string().min(1).optional(),
}).passthrough();

export type ConnectorFactInput = z.input<typeof ConnectorFactInputSchema>;
export type ConnectorFact = z.infer<typeof ConnectorFactSchema>;
