import { z } from 'zod';

// API endpoint validation schemas
export const apiEndpointSchema = z.object({
  method: z.enum(['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']),
  path: z.string().regex(/^\/[a-zA-Z0-9\-_\/]+$/),
  description: z.string().optional(),
  parameters: z.record(z.any()).optional(),
  headers: z.record(z.string()).optional(),
  body: z.any().optional(),
  response: z.object({
    status: z.number().int().min(100).max(599),
    contentType: z.string().regex(/^application\/(json|xml|javascript|x-www-form-urlencoded)$/),
    schema: z.any().optional(),
  }).optional(),
});

// Database query validation schemas
export const databaseQuerySchema = z.object({
  query: z.string().min(1),
  parameters: z.array(z.any()).optional(),
  timeout: z.number().int().min(100).max(60000),
  connection: z.object({
    host: z.string().url(),
    port: z.number().int().min(1).max(65535),
    database: z.string().min(1),
    user: z.string().min(1),
    password: z.string().optional(),
  }).optional(),
});

// External service integration schemas
export const externalServiceSchema = z.object({
  name: z.string().min(1),
  url: z.string().url(),
  method: z.enum(['GET', 'POST', 'PUT', 'PATCH', 'DELETE']),
  authentication: z.object({
    type: z.enum(['apiKey', 'oauth2', 'jwt', 'basic']),
    credentials: z.record(z.string()).optional(),
  }).optional(),
  timeout: z.number().int().min(100).max(300000),
  retries: z.number().int().min(0).max(5),
  rateLimit: z.object({
    requests: z.number().int().min(1),
    window: z.number().int().min(1).max(3600),
  }).optional(),
});

// Message queue integration schemas
export const messageQueueSchema = z.object({
  queueName: z.string().min(1),
  type: z.enum(['rabbitmq', 'kafka', 'sqs', 'redis']),
  connection: z.object({
    host: z.string().url(),
    port: z.number().int().min(1).max(65535),
    username: z.string().optional(),
    password: z.string().optional(),
    virtualHost: z.string().optional(),
  }).optional(),
  options: z.object({
    durable: z.boolean().optional(),
    exclusive: z.boolean().optional(),
    autoDelete: z.boolean().optional(),
    arguments: z.record(z.any()).optional(),
  }).optional(),
});

// Cache integration schemas
export const cacheSchema = z.object({
  key: z.string().min(1),
  value: z.any(),
  ttl: z.number().int().min(0).max(86400),
  type: z.enum(['memory', 'redis', 'memcached', 'file']),
  options: z.object({
    compression: z.boolean().optional(),
    encryption: z.boolean().optional(),
    namespace: z.string().optional(),
  }).optional(),
});

// File upload validation schemas
export const fileUploadSchema = z.object({
  filename: z.string().min(1),
  size: z.number().int().min(0),
  type: z.string().regex(/^\w+\/\w+$/),
  encoding: z.string().optional(),
  metadata: z.record(z.string()).optional(),
  maxFileSize: z.number().int().min(0),
  allowedTypes: z.array(z.string().regex(/^\w+\/\w+$/)).optional(),
});

// WebSocket connection validation schemas
export const websocketSchema = z.object({
  url: z.string().url(),
  protocols: z.array(z.string()).optional(),
  headers: z.record(z.string()).optional(),
  timeout: z.number().int().min(1000).max(300000),
  reconnection: z.object({
    enabled: z.boolean(),
    attempts: z.number().int().min(0).max(10),
    delay: z.number().int().min(100).max(60000),
  }).optional(),
});

// Third-party API integration schemas
export const thirdPartyApiSchema = z.object({
  provider: z.string().min(1),
  endpoint: z.string().url(),
  method: z.enum(['GET', 'POST', 'PUT', 'PATCH', 'DELETE']),
  authentication: z.object({
    type: z.enum(['apiKey', 'oauth2', 'jwt', 'basic']),
    credentials: z.record(z.string()).optional(),
    scopes: z.array(z.string()).optional(),
  }).optional(),
  rateLimit: z.object({
    requests: z.number().int().min(1),
    window: z.number().int().min(1).max(3600),
  }).optional(),
  pagination: z.object({
    enabled: z.boolean(),
    limit: z.number().int().min(1).max(1000),
    offset: z.number().int().min(0),
  }).optional(),
});