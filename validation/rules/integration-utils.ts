import { apiEndpointSchema, databaseQuerySchema, externalServiceSchema, messageQueueSchema, cacheSchema, fileUploadSchema, websocketSchema, thirdPartyApiSchema } from './integration';

// Integration validation utilities
export class IntegrationValidator {
  static validateApiEndpoint(data: unknown): { success: true; data: z.infer<typeof apiEndpointSchema> } | { success: false; error: string } {
    const result = apiEndpointSchema.safeParse(data);
    return result.success
      ? { success: true, data: result.data }
      : { success: false, error: result.error.message };
  }

  static validateDatabaseQuery(data: unknown): { success: true; data: z.infer<typeof databaseQuerySchema> } | { success: false; error: string } {
    const result = databaseQuerySchema.safeParse(data);
    return result.success
      ? { success: true, data: result.data }
      : { success: false, error: result.error.message };
  }

  static validateExternalService(data: unknown): { success: true; data: z.infer<typeof externalServiceSchema> } | { success: false; error: string } {
    const result = externalServiceSchema.safeParse(data);
    return result.success
      ? { success: true, data: result.data }
      : { success: false, error: result.error.message };
  }

  static validateMessageQueue(data: unknown): { success: true; data: z.infer<typeof messageQueueSchema> } | { success: false; error: string } {
    const result = messageQueueSchema.safeParse(data);
    return result.success
      ? { success: true, data: result.data }
      : { success: false, error: result.error.message };
  }

  static validateCache(data: unknown): { success: true; data: z.infer<typeof cacheSchema> } | { success: false; error: string } {
    const result = cacheSchema.safeParse(data);
    return result.success
      ? { success: true, data: result.data }
      : { success: false, error: result.error.message };
  }

  static validateFileUpload(data: unknown): { success: true; data: z.infer<typeof fileUploadSchema> } | { success: false; error: string } {
    const result = fileUploadSchema.safeParse(data);
    return result.success
      ? { success: true, data: result.data }
      : { success: false, error: result.error.message };
  }

  static validateWebSocket(data: unknown): { success: true; data: z.infer<typeof websocketSchema> } | { success: false; error: string } {
    const result = websocketSchema.safeParse(data);
    return result.success
      ? { success: true, data: result.data }
      : { success: false, error: result.error.message };
  }

  static validateThirdPartyApi(data: unknown): { success: true; data: z.infer<typeof thirdPartyApiSchema> } | { success: false; error: string } {
    const result = thirdPartyApiSchema.safeParse(data);
    return result.success
      ? { success: true, data: result.data }
      : { success: false, error: result.error.message };
  }
}

// Integration middleware
export const integrationMiddleware = (schema: z.ZodSchema) => {
  return (data: unknown) => {
    const result = schema.safeParse(data);
    if (!result.success) {
      throw new Error(`Integration validation failed: ${result.error.message}`);
    }
    return result.data;
  };
};

// Integration configuration validator
export const validateIntegrationConfig = (config: unknown) => {
  const schema = z.object({
    services: z.array(externalServiceSchema),
    queues: z.array(messageQueueSchema),
    caches: z.array(cacheSchema),
    endpoints: z.array(apiEndpointSchema),
  });

  const result = schema.safeParse(config);
  return result.success ? { success: true, data: result.data } : { success: false, error: result.error.message };
};

// Integration health checker
export const checkIntegrationHealth = async (integration: z.infer<typeof externalServiceSchema>) => {
  try {
    const response = await fetch(integration.url, {
      method: integration.method,
      headers: integration.authentication?.credentials || {},
      timeout: integration.timeout,
    });

    return {
      success: response.ok,
      status: response.status,
      responseTime: Date.now(),
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
};

// Integration rate limiter
export const createRateLimiter = (limit: number, window: number) => {
  const requests: number[] = [];

  return () => {
    const now = Date.now();
    const windowStart = now - window * 1000;
    
    // Remove requests outside the window
    while (requests.length > 0 && requests[0] < windowStart) {
      requests.shift();
    }

    if (requests.length < limit) {
      requests.push(now);
      return true;
    }
    
    return false;
  };
};

// Integration retry mechanism
export const createRetryMechanism = (maxRetries: number, delay: number) => {
  return async (operation: () => Promise>any>) => {
    let lastError: Error;
    
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        if (error instanceof Error) {
          lastError = error;
        }
        
        if (attempt < maxRetries) {
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }
    
    throw lastError || new Error('Operation failed after maximum retries');
  };
};