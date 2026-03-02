# Frontend Ruleset

## Component Design
- Components are pure where possible. Side effects belong in hooks, not render.
- Every interactive element requires an accessibility label (`aria-label` or visible label).
- No inline styles — use CSS modules or the project's design token system.

## State & Data
- Side effects (API calls, subscriptions) live in hooks, never in render functions.
- Prefer local state; lift to context only when 3+ components share the same data.
- No direct DOM manipulation — use React refs if unavoidable.

## Testing
- Unit-test pure components with React Testing Library.
- Test user interactions, not implementation details (no testing internal state).
- Every form must have a test for invalid input handling.

## Non-Negotiables
- No `console.log` in production code.
- All user-facing strings must be internationalisation-ready (no hardcoded copy in JSX).
- Accessibility audit required before merge for any new interactive component.
