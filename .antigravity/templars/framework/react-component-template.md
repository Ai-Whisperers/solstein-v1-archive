---
id: templar.framework.react.v1
kind: templar
version: 1.0.0
description: Structure template for React component files
implements: component.react
globs: "src/components/**/*.tsx"
governs: "src/components/**/*.tsx"
requires: ["rule.clean-code.v1", "rule.naming-conventions.v1"]
provenance: { owner: team-frontend, last_review: 2025-12-06 }
---

# {{component_name}} Component

## Overview
{{component_description}}

## Props Interface
```typescript
interface {{ComponentName}}Props {
  /** {{prop_description}} */
  {{prop_name}}: {{prop_type}};
  /** {{prop_description}} */
  {{prop_name}}: {{prop_type}};
}
```

## State Management
```typescript
const [{{state_name}}, set{{StateName}}] = useState<{{state_type}}>({{initial_value}});
```

## Component Structure
```tsx
export function {{ComponentName}}({ {{prop_list}} }: {{ComponentName}}Props) {
  // State and hooks
  const [{{state_name}}, set{{StateName}}] = useState<{{state_type}}>({{initial_value}});
  const {{ref_name}} = useRef<{{ref_type}}>(null);
  
  // Effects
  useEffect(() => {
    // Side effects
  }, [{{dependency_list}}]);
  
  // Event handlers
  const handle{{EventName}} = useCallback((event: React.MouseEvent) => {
    // Event handling logic
  }, [{{dependency_list}}]);
  
  return (
    <div className="{{component_name}}" ref={{{ref_name}}}>
      {/* Component content */}
    </div>
  );
}
```

## Testing
```typescript
// Unit tests
import { render, screen, fireEvent } from '@testing-library/react';
import { {{ComponentName}} } from './{{component_name}}';

describe('{{ComponentName}}', () => {
  it('renders correctly', () => {
    render(<{{ComponentName}} {{prop_values}} />);
    expect(screen.getByText(/{{expected_text}}/i)).toBeInTheDocument();
  });
  
  it('handles events correctly', () => {
    const handleClick = jest.fn();
    render(<{{ComponentName}} onClick={handleClick} />);
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

## Props Validation
```typescript
// PropTypes or TypeScript validation
{{ComponentName}}.propTypes = {
  {{prop_name}}: PropTypes.{{prop_type}},
};

{{ComponentName}}.defaultProps = {
  {{prop_name}}: {{default_value}},
};
```

## CSS Modules
```css
.{{component_name}} {
  /* Component styles */
}

.{{component_name}}__element {
  /* Element styles */
}

.{{component_name}}--modifier {
  /* Modifier styles */
}
```

## Accessibility
```tsx
// ARIA attributes and semantic HTML
<div
  className="{{component_name}}"
  role="{{role}}"
  aria-label="{{label}}"
  aria-describedby="{{description_id}}"
  tabIndex={0}
  onKeyDown={handleKeyDown}
>
  {/* Content */}
</div>
```

## Performance Considerations
- Use React.memo for expensive components
- Implement proper dependency arrays in hooks
- Use useCallback and useMemo for optimization
- Avoid inline functions in render

## Error Boundaries
```tsx
// Error boundary wrapper
const ErrorBoundary: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [hasError, setHasError] = useState(false);
  
  if (hasError) {
    return <div>Something went wrong</div>;
  }
  
  return <>{children}</>;
};
```

## Component Lifecycle
```tsx
// Component lifecycle methods
useEffect(() => {
  // Mount
  return () => {
    // Unmount
  };
}, []);

useEffect(() => {
  // Update when dependencies change
}, [{{dependency}}]);
```

## Integration
- Compatible with React Router
- Works with Redux/Context API
- Supports internationalization
- Follows React 18+ patterns

---
*Template created: {{timestamp}}*
{{validation_checklist}}