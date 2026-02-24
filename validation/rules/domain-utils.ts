import { userSchema, productSchema, orderSchema, apiResponseSchema, configSchema } from './specific-domain';

// Validation utilities
export class DomainValidator {
  static validateUser(data: unknown): { success: true; data: z.infer<typeof userSchema> } | { success: false; error: string } {
    const result = userSchema.safeParse(data);
    return result.success
      ? { success: true, data: result.data }
      : { success: false, error: result.error.message };
  }

  static validateProduct(data: unknown): { success: true; data: z.infer<typeof productSchema> } | { success: false; error: string } {
    const result = productSchema.safeParse(data);
    return result.success
      ? { success: true, data: result.data }
      : { success: false, error: result.error.message };
  }

  static validateOrder(data: unknown): { success: true; data: z.infer<typeof orderSchema> } | { success: false; error: string } {
    const result = orderSchema.safeParse(data);
    return result.success
      ? { success: true, data: result.data }
      : { success: false, error: result.error.message };
  }

  static validateApiResponse(data: unknown): { success: true; data: z.infer<typeof apiResponseSchema> } | { success: false; error: string } {
    const result = apiResponseSchema.safeParse(data);
    return result.success
      ? { success: true, data: result.data }
      : { success: false, error: result.error.message };
  }

  static validateConfig(data: unknown): { success: true; data: z.infer<typeof configSchema> } | { success: false; error: string } {
    const result = configSchema.safeParse(data);
    return result.success
      ? { success: true, data: result.data }
      : { success: false, error: result.error.message };
  }
}

// Type guards
export const isUser = (data: unknown): data is z.infer<typeof userSchema> =>
  userSchema.safeParse(data).success;

export const isProduct = (data: unknown): data is z.infer<typeof productSchema> =>
  productSchema.safeParse(data).success;

export const isOrder = (data: unknown): data is z.infer<typeof orderSchema> =>
  orderSchema.safeParse(data).success;

export const isApiResponse = (data: unknown): data is z.infer<typeof apiResponseSchema> =>
  apiResponseSchema.safeParse(data).success;

// Helper functions
export const sanitizeUserData = (data: z.infer<typeof userSchema>) => {
  const { password, ...sanitized } = data;
  return sanitized;
};

export const calculateOrderTotal = (items: z.infer<typeof orderSchema>['items']) => {
  return items.reduce((total, item) => total + item.price * item.quantity, 0);
};

export const formatPrice = (amount: number, currency: string) => {
  const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  });
  return formatter.format(amount);
};

// Data transformation utilities
export const transformApiResponse = (response: z.infer<typeof apiResponseSchema>) => {
  if (!response.success && response.error) {
    return {
      type: 'error' as const,
      code: response.error.code,
      message: response.error.message,
      details: response.error.details,
    };
  }
  
  return {
    type: 'success' as const,
    data: response.data,
    message: response.message,
  };
};

// Validation middleware
export const validationMiddleware = (schema: z.ZodSchema) => {
  return (data: unknown) => {
    const result = schema.safeParse(data);
    if (!result.success) {
      throw new Error(`Validation failed: ${result.error.message}`);
    }
    return result.data;
  };
};

// Batch validation
export const validateBatch = <T>(
  items: unknown[],
  validator: (item: unknown) => item is T
): { valid: T[]; invalid: { item: unknown; error: string }[] } => {
  const valid: T[] = [];
  const invalid: { item: unknown; error: string }[] = [];

  for (const item of items) {
    if (validator(item)) {
      valid.push(item);
    } else {
      try {
        validator(item);
      } catch (error) {
        invalid.push({
          item,
          error: error instanceof Error ? error.message : 'Unknown validation error',
        });
      }
    }
  }

  return { valid, invalid };
};