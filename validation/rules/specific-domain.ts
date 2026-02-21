import { z } from 'zod';

// User validation schema
export const userSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1).max(100),
  email: z.string().email(),
  age: z.number().int().min(0).max(150),
  isActive: z.boolean(),
  role: z.enum([
    'admin',
    'user',
    'moderator',
    'guest'
  ]),
  preferences: z.object({
    theme: z.enum(['light', 'dark', 'auto']),
    notifications: z.boolean(),
    language: z.string().min(2).max(5),
  }).optional(),
});

// Product validation schema
export const productSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1).max(200),
  description: z.string().min(1).max(1000).optional(),
  price: z.number().positive(),
  currency: z.string().length(3),
  stock: z.number().int().min(0),
  category: z.string().min(1).max(50),
  tags: z.array(z.string().min(1).max(50)).optional(),
  metadata: z.record(z.any()).optional(),
});

// Order validation schema
export const orderSchema = z.object({
  id: z.string().uuid(),
  userId: z.string().uuid(),
  items: z.array(
    z.object({
      productId: z.string().uuid(),
      quantity: z.number().int().min(1),
      price: z.number().positive(),
      currency: z.string().length(3),
    })
  ),
  total: z.number().positive(),
  status: z.enum([
    'pending',
    'processing',
    'shipped',
    'delivered',
    'cancelled',
    'refunded'
  ]),
  shippingAddress: z.object({
    street: z.string().min(1).max(200),
    city: z.string().min(1).max(100),
    state: z.string().min(1).max(100).optional(),
    country: z.string().min(2).max(100),
    postalCode: z.string().min(1).max(20),
  }),
  createdAt: z.date(),
  updatedAt: z.date().optional(),
});

// API response validation schema
export const apiResponseSchema = z.object({
  success: z.boolean(),
  data: z.any(),
  message: z.string().optional(),
  error: z.object({
    code: z.string().optional(),
    message: z.string(),
    details: z.any().optional(),
  }).optional(),
  timestamp: z.date(),
});

// Configuration validation schema
export const configSchema = z.object({
  apiUrl: z.string().url(),
  apiKey: z.string().min(1),
  timeout: z.number().int().min(100).max(60000),
  retries: z.number().int().min(0).max(10),
  environment: z.enum(['development', 'staging', 'production']),
  features: z.record(z.boolean()).optional(),
});

// Form validation schemas
export const loginFormSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8).max(100),
});

export const registrationFormSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8).max(100),
  confirmPassword: z.string().min(8).max(100),
  name: z.string().min(1).max(100),
});

export const contactFormSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  subject: z.string().min(1).max(200),
  message: z.string().min(10).max(1000),
});