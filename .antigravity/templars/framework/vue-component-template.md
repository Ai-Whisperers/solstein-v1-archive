---
id: templar.framework.vue.v1
kind: templar
version: 1.0.0
description: Structure template for Vue 3 component files
implements: component.vue
globs: "src/components/**/*.vue"
governs: "src/components/**/*.vue"
requires: ["rule.clean-code.v1", "rule.naming-conventions.v1"]
provenance: { owner: team-frontend, last_review: 2025-12-06 }
---

<template>
  <!-- Component template -->
  <div id="{{component_name}}" class="{{component_name}}">
    <!-- Component content -->
    <slot name="default" />
  </div>
</template>

<script setup lang="ts">
// Component script with Composition API

// Props definition
interface {{ComponentName}}Props {
  /** {{prop_description}} */
  {{prop_name}}: {{prop_type}};
  /** {{prop_description}} */
  {{prop_name}}: {{prop_type}};
}

// Define props
const props = withDefaults(defineProps<{{ComponentName}}Props>(), {
  {{prop_name}}: {{default_value}},
});

// Reactive state
const {{state_name}} = ref<{{state_type}}>({{initial_value}});

// Computed properties
const {{computed_name}} = computed(() => {
  return {{computation_logic}};
});

// Watchers
watch({{state_name}}, (newValue, oldValue) => {
  // Watch logic
});

// Lifecycle hooks
onMounted(() => {
  // Component mounted
});

onUnmounted(() => {
  // Component unmounted
});

// Event handlers
const handle{{EventName}} = () => {
  // Event handling logic
  emit('{{event_name}}', {{payload}});
};

// Custom methods
const {{method_name}} = () => {
  // Method logic
};

// Define emits
const emit = defineEmits({
  // Validate event payload
  '{{event_name}}': (payload: {{payload_type}}) => {
    return payload && typeof payload === 'object';
  },
});

// Provide/inject
provide('{{provide_name}}', {
  // Provide data
});

// Type-safe refs
const {{ref_name}} = ref<{{ref_type}}>(null);

// Async operations
const {{async_name}} = async () => {
  try {
    const result = await {{async_operation}};
    return result;
  } catch (error) {
    console.error('Error in {{async_name}}:', error);
    throw error;
  }
};

// Validation
const {{validation_name}} = () => {
  if (!{{condition}}) {
    return {
      valid: false,
      message: '{{validation_message}}',
    };
  }
  return { valid: true };
};
</script>

<style scoped>
/* Component scoped styles */
.{{component_name}} {
  /* Component styles */
}

.{{component_name}}__element {
  /* Element styles */
}

.{{component_name}}--modifier {
  /* Modifier styles */
}

@media (min-width: 768px) {
  .{{component_name}} {
    /* Responsive styles */
  }
}
</style>

## Component Structure
1. **Template**: HTML structure with slots and directives
2. **Script**: TypeScript logic with Composition API
3. **Style**: Scoped CSS with responsive design

## Props Interface
```typescript
interface {{ComponentName}}Props {
  /** {{prop_description}} */
  {{prop_name}}: {{prop_type}};
  /** {{prop_description}} */
  {{prop_name}}: {{prop_type}};
}
```

## Events
```typescript
// Define emitted events
const emit = defineEmits({
  '{{event_name}}': (payload: {{payload_type}}) => true,
  '{{event_name}}': null,
});
```

## Slots
```vue
<!-- Default slot -->
<{{component_name}}>
  Default content
</{{component_name}}>

<!-- Named slot -->
<{{component_name}}>
  <template #header>
    Header content
  </template>
</{{component_name}}>

<!-- Scoped slot -->
<{{component_name}}>
  <template #item="{ item }">
    {{ item.name }}
  </template>
</{{component_name}}>
```

## Testing
```typescript
// Unit tests with Vitest
import { mount } from '@vue/test-utils';
import { {{ComponentName}} } from './{{component_name}}.vue';

describe('{{ComponentName}}', () => {
  it('renders correctly', () => {
    const wrapper = mount({{ComponentName}}, {
      props: {
        {{prop_name}}: {{prop_value}},
      },
    });
    expect(wrapper.text()).toContain('{{expected_text}}');
  });
  
  it('emits events correctly', async () => {
    const wrapper = mount({{ComponentName}});
    await wrapper.trigger('click');
    expect(wrapper.emitted('{{event_name}}')).toBeTruthy();
  });
});
```

## Integration
- Compatible with Vue Router
- Works with Pinia state management
- Supports internationalization
- Follows Vue 3 Composition API patterns

## Performance Considerations
- Use `v-memo` for expensive template parts
- Implement proper reactivity with `computed`
- Use `watch` wisely to avoid infinite loops
- Lazy load components when needed

## Accessibility
```vue
<!-- Semantic HTML and ARIA attributes -->
<button
  @click="handle{{EventName}}"
  :disabled="{{disabled_state}}"
  aria-label="{{aria_label}}"
  role="{{role}}"
>
  {{button_text}}
</button>
```

## Error Handling
```typescript
// Error boundaries in Vue 3
const {{error_boundary_name}} = onErrorCaptured((error, instance, info) => {
  console.error('Captured error:', error, info);
  // Handle error
  return false; // Allow error to propagate
});
```

---
*Template created: {{timestamp}}*
{{validation_checklist}}