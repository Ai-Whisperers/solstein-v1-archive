import { z } from "zod";

export const NewsSignalTypeSchema = z.enum([
  "funding",
  "partnership",
  "key_hire",
]);

export const NewsSignalSchema = z.object({
  companyName: z.string(),
  signalType: NewsSignalTypeSchema,
  description: z.string(),
  source: z.string(),
  confidence: z.number().min(0).max(1),
  detectedAt: z.string().datetime().nullable().optional(),
  rawData: z.record(z.unknown()).default({}),
});

export const MarketSignalFactValueSchema = z.object({
  signal_type: z.string(),
  title: z.string().nullable().optional(),
  description: z.string(),
  source: z.string(),
  url: z.string().url().nullable().optional(),
  published_at: z.string().nullable().optional(),
  signal_date: z.string().nullable().optional(),
});

export type NewsSignalType = z.infer<typeof NewsSignalTypeSchema>;
export type NewsSignal = z.infer<typeof NewsSignalSchema>;
export type MarketSignalFactValue = z.infer<typeof MarketSignalFactValueSchema>;
