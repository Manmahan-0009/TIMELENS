---
name: responsive-mobile-first
description: Build responsive mobile-first layouts with fluid sizing, adaptive breakpoints, and accessible touch interactions.
---

# Responsive Mobile-First Skill

All TimeLens interfaces must be responsive.

## Guidelines

### 1. Mobile-First Design

Design for small screens first.

Use min-width media queries for progressively larger layouts.

Example:

@media (min-width: 768px)

### 2. Fluid Layouts

Avoid rigid fixed-width containers.

Prefer:
- width: 100%
- max-width
- flexible grid layouts
- responsive columns
- scalable spacing

### 3. Adaptive Interface

On mobile:
- Stack image upload sections vertically.
- Keep buttons full-width where appropriate.
- Avoid horizontal overflow.
- Maintain readable descriptions.

On desktop:
- Display historical and modern photographs side by side.
- Use available space effectively.
- Maintain a maximum readable content width.

### 4. Touch Accessibility

Interactive elements should provide at least
48px by 48px effective touch targets.

### 5. Image Responsiveness

- Preserve aspect ratio.
- Avoid stretching.
- Prevent image overflow.
- Support different photograph dimensions.

### 6. Streamlit Compatibility

Prefer Streamlit-native responsive components.

Use custom CSS only when necessary.

Do not rely on fragile internal Streamlit DOM selectors.

### 7. Verification

Test or inspect the UI at approximately:

- 375px mobile
- 768px tablet
- 1440px desktop

Never claim visual testing was completed unless
the interface was actually inspected.

