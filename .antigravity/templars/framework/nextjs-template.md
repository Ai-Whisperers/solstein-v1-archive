---
id: templar.framework.nextjs.v1
kind: templar
version: 1.0.0
description: Structure template for Next.js pages and components
implements: component.nextjs
globs: "pages/**/*.tsx", "components/**/*.tsx"
governs: "pages/**/*.tsx", "components/**/*.tsx"
requires: ["rule.clean-code.v1", "rule.naming-conventions.v1"]
provenance: { owner: team-frontend, last_review: 2025-12-06 }
---

## Next.js Page Structure

```tsx
// pages/{{page_name}}.tsx
import { NextPage } from 'next';
import { useRouter, useQuery } from 'next/navigation';
import { serverClient } from '@/lib/supabase';
import { Metadata } from 'next';

interface {{PageName}}PageProps {
  /** {{prop_description}} */
  {{prop_name}}?: {{prop_type}};
}

export const metadata: Metadata = {
  title: '{{PageTitle}}',
  description: '{{PageDescription}}',
  openGraph: {
    title: '{{PageTitle}}',
    description: '{{PageDescription}}',
  },
  twitter: {
    card: 'summary_large_image',
    title: '{{PageTitle}}',
    description: '{{PageDescription}}',
  },
};

export const revalidate = 60; // Seconds

const {{PageName}}Page: NextPage<{{PageName}}PageProps> = ({ {{prop_name}} }) => {
  // Hooks
  const router = useRouter();
  const { data: {{data_name}}, error: {{error_name}}, isLoading } = useQuery({
    queryKey: ['{{query_key}}'],
    queryFn: async () => {
      const { data, error } = await serverClient
        .from('{{table_name}}')
        .select();
      
      if (error) {
        throw error;
      }
      
      return data;
    },
  });
  
  // State
  const [{{state_name}}, set{{StateName}}] = useState<{{state_type}}>({{initial_value}});
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // Effects
  useEffect(() => {
    // Page mount logic
    if (!{{data_name}} && !isLoading && !{{error_name}}) {
      // Handle empty state
    }
  }, [{{data_name}}, isLoading, {{error_name}}]);
  
  // Event handlers
  const handle{{EventName}} = useCallback((event: React.MouseEvent) => {
    event.preventDefault();
    // Event handling logic
    router.push('/{{route_path}}');
  }, [router]);
  
  const handleFormSubmit = async (formData: {{form_type}}) => {
    try {
      const response = await fetch('/api/{{api_endpoint}}', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      if (!response.ok) {
        throw new Error('Form submission failed');
      }
      
      const result = await response.json();
      // Handle success
      setIsModalOpen(false);
    } catch (error) {
      // Handle error
      console.error('Form submission error:', error);
    }
  };
  
  // Render
  if (isLoading) {
    return <div>Loading...</div>;
  }
  
  if ({{error_name}}) {
    return (
      <div>
        <p>Error: {{{error_name}}.message}</p>
        <button onClick={() => router.reload()}>Retry</button>
      </div>
    );
  }
  
  return (
    <div className="{{page_name}}">
      {/* SEO and metadata */}
      <Head>
        <title>{{PageTitle}}</title>
        <meta name="description" content="{{PageDescription}}" />
      </Head>
      
      {/* Navigation */}
      <Navbar />
      
      {/* Main content */}
      <main className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">{{PageTitle}}</h1>
        
        {/* Breadcrumbs */}
        <nav className="mb-4" aria-label="Breadcrumb">
          <ol className="flex items-center space-x-2 text-sm">
            <li>
              <a href="/" className="text-gray-500 hover:text-gray-700">Home</a>
            </li>
            <li aria-current="page">{{PageTitle}}</li>
          </ol>
        </nav>
        
        {/* Page content */}
        <div className="space-y-6">
          {/* Data display */}
          {{{data_name}} && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Data Overview</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {{{data_name}}.map((item) => (
                  <div key={item.id} className="bg-gray-50 p-4 rounded">
                    <h3 className="font-medium">{{item.title}}</h3>
                    <p className="text-gray-600">{{item.description}}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Form section */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Submit Data</h2>
            <FormComponent 
              onSubmit={handleFormSubmit}
              isLoading={isLoading}
            />
          </div>
          
          {/* Actions */}
          <div className="flex justify-end space-x-4">
            <button 
              onClick={handle{{EventName}}} 
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              {{ButtonLabel}}
            </button>
            <button 
              onClick={() => setIsModalOpen(true)}
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
            >
              Open Modal
            </button>
          </div>
        </div>
      </main>
      
      {/* Footer */}
      <Footer />
      
      {/* Modal */}
      {isModalOpen && (
        <Modal 
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="{{ModalTitle}}"
        >
          <ModalContent>
            <p>{{ModalDescription}}</p>
            <div className="flex justify-end space-x-4 pt-4">
              <button 
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
              >
                Cancel
              </button>
              <button 
                onClick={handleModalConfirm}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Confirm
              </button>
            </div>
          </ModalContent>
        </Modal>
      )}
    </div>
  );
};

export default {{PageName}}Page;
```

## Next.js API Route Structure

```typescript
// pages/api/{{api_endpoint}}.ts
import { NextApiRequest, NextApiResponse } from 'next';
import { serverClient } from '@/lib/supabase';
import { z } from 'zod';

const {{api_endpoint}}Schema = z.object({
  /** {{field_description}} */
  {{field_name}}: z.string().min(1, 'Field is required'),
  /** {{field_description}} */
  {{field_name}}: z.string().email('Invalid email address'),
  /** {{field_description}} */
  {{field_name}}: z.number().min(0, 'Must be positive'),
});

type {{api_endpoint}}SchemaType = z.infer<typeof {{api_endpoint}}Schema>;

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  try {
    if (req.method !== 'POST') {
      res.setHeader('Allow', ['POST']);
      return res.status(405).end('Method Not Allowed');
    }

    // Validate request body
    const parsedBody = req.body;
    const parsed = {{api_endpoint}}Schema.safeParse(parsedBody);
    
    if (!parsed.success) {
      return res.status(400).json({
        error: 'Validation failed',
        details: parsed.error.format(),
      });
    }

    const formData: {{api_endpoint}}SchemaType = parsed.data;

    // Process data
    const { data, error } = await serverClient
      .from('{{table_name}}')
      .insert(formData)
      .select();

    if (error) {
      return res.status(500).json({
        error: 'Database error',
        details: error.message,
      });
    }

    return res.status(200).json({
      success: true,
      data: data[0],
    });

  } catch (error) {
    console.error('API error:', error);
    return res.status(500).json({
      error: 'Internal server error',
      details: error instanceof Error ? error.message : 'Unknown error',
    });
  }
}
```

## Next.js Component Structure

```tsx
// components/{{component_name}}.tsx
import { ReactNode, MouseEvent } from 'react';
import Link from 'next/link';

interface {{ComponentName}}Props {
  /** {{prop_description}} */
  {{prop_name}}: {{prop_type}};
  /** {{prop_description}} */
  children?: ReactNode;
  /** {{prop_description}} */
  className?: string;
  /** {{prop_description}} */
  onClick?: (event: MouseEvent) => void;
}

export const {{ComponentName}}: React.FC<{{ComponentName}}Props> = ({
  {{prop_name}},
  children,
  className = '',
  onClick,
}) => {
  return (
    <div 
      className={`{{component_name}} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
};
```

## Tailwind CSS Configuration

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};

export default config;
```

## ESLint Configuration

```json
{
  "extends": [
    "next/core-web-vitals",
    "plugin:@typescript-eslint/recommended",
    "prettier"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "react/react-in-jsx-scope": "off",
    "jsx-a11y/anchor-is-valid": [
      "error",
      {
        "components": ["Link"],
        "specialLink": ["hrefLeft", "hrefRight"],
        "aspects": ["invalidHref", "preferButton"]
      }
    ]
  },
  "ignorePatterns": [
    ".next/",
    "!.eslintrc.cjs"
  ]
}
```

## Testing Structure

```typescript
// __tests__/{{component_name}}.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { {{ComponentName}} } from '@/components/{{component_name}}';

describe('{{ComponentName}}', () => {
  it('renders correctly', () => {
    render(
      <{{ComponentName}} {{prop_name}}="{{prop_value}}">
        Test content
      </{{ComponentName}}>
    );
    
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });
  
  it('handles click events', () => {
    const handleClick = jest.fn();
    render(
      <{{ComponentName}} onClick={handleClick}>
        Click me
      </{{ComponentName}}>
    );
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

## Integration with Supabase

```typescript
// lib/supabase.ts
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const serverClient = createClient(supabaseUrl, supabaseAnonKey);

export const authClient = createClient(
  supabaseUrl,
  supabaseAnonKey,
  {
    auth: {
      autoRefreshToken: true,
      persistSession: true,
    },
  }
);
```

## Environment Variables

```env
# Next.js Environment Variables
NEXT_PUBLIC_SITE_NAME=Your Site Name
NEXT_PUBLIC_SITE_URL=http://localhost:3000
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Server-side only
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
DATABASE_URL=your_database_url
```

## Performance Optimization
- Use React.memo for expensive components
- Implement proper dependency arrays in hooks
- Use useCallback and useMemo for optimization
- Implement dynamic imports for code splitting
- Use Next.js Image component for optimized images

## Accessibility
```tsx
// Accessible components
export const Button: React.FC<ButtonProps> = ({
  children,
  className = '',
  disabled = false,
  type = 'button',
  ...props
}) => {
  return (
    <button
      type={type}
      disabled={disabled}
      className={`btn ${className}`}
      aria-disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};
```

---
*Template created: {{timestamp}}*
{{validation_checklist}}