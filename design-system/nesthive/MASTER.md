# Design System Master File

> **LOGIC:** When building a specific page, first check `design-system/pages/[page-name].md`.
> If that file exists, its rules **override** this Master file.
> If not, strictly follow the rules below.

---

**Project:** NestHive
**Generated:** 2026-10-27 23:54:50
**Category:** Industrial operations dashboard (light)
**Design Dials:** Variance 4/10 (Balanced / Modern) | Motion 3/10 (Subtle) | Density 8/10 (Dense / Dashboard)

**Brand lock:** The generator suggested slate `#334155` + stock green `#059669` and Varela Round / Nunito Sans. Those are rejected. NestHive stays light honey / cacao / crema. Typography is the verified dashboard pairing Fira Sans + Fira Code (`professional refined dashboard sans`). Style kept: Minimalism & Swiss Style. Red is destructive only. No dark mode. No purple gradients.

---

## Global Rules

### Color Palette

| Role | Hex | CSS Variable |
|------|-----|--------------|
| Primary / text | `#5B3918` | `--nest-text` |
| On accent | `#241609` | `--nh-cocoa-deep` |
| Accent / CTA | `#F9AE08` | `--nest-accent` |
| Accent hover | `#E39D00` | `--nest-accent-hover` |
| Ink (small honey-adjacent text) | `#8A5A00` | `--nest-ink` |
| Background canvas | `#F4EFE6` | `--nest-bg` |
| Panel | `#FFFCF7` | `--nest-panel` |
| Muted text | `#674627` | `--nest-muted` |
| Border | `rgba(91, 57, 24, 0.14)` | `--nest-border` |
| Destructive | `#E4032E` | `--nest-red` |
| Success text | `#065F46` | `--nest-green` |
| Ring | `#241609` | `--nest-ring` |

**Color Notes:** Locked NestHive honey, cacao, and cream. White text on honey fails contrast (1.9:1); CTA label is cacao `#241609` on honey (9.3:1).

### Typography

- **UI font:** Fira Sans
- **Data / sim time:** Fira Code
- **Mood:** precise, technical, readable at dashboard density
- **Google Fonts:** [Fira Sans + Fira Code](https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Fira+Sans:wght@400;500;600;700&display=swap)

Loaded with `next/font` in `nestlink/frontend/app/layout.tsx`. Do not use Varela Round.

### Spacing Variables

*Density: 8/10 — Dense / Dashboard*

| Token | Value | Usage |
|-------|-------|-------|
| `--space-xs` | `2px` / `0.125rem` | Tight gaps |
| `--space-sm` | `4px` / `0.25rem` | Icon gaps, inline spacing |
| `--space-md` | `8px` / `0.5rem` | Standard padding |
| `--space-lg` | `12px` / `0.75rem` | Section padding |
| `--space-xl` | `16px` / `1rem` | Large gaps |
| `--space-2xl` | `24px` / `1.5rem` | Section margins |
| `--space-3xl` | `32px` / `2rem` | Hero padding |

### Shadow Depths

| Level | Value | Usage |
|-------|-------|-------|
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | Subtle lift |
| `--shadow-md` | `0 4px 6px rgba(0,0,0,0.1)` | Cards, buttons |
| `--shadow-lg` | `0 10px 15px rgba(0,0,0,0.1)` | Modals, dropdowns |
| `--shadow-xl` | `0 20px 25px rgba(0,0,0,0.15)` | Hero images, featured cards |

---

## Component Specs

### Buttons

```css
/* Primary — honey fill, cacao label. No translate on hover. */
.btn-primary {
  background: #F9AE08;
  color: #241609;
  padding: 6px 10px;
  border-radius: 8px;
  font-weight: 600;
  transition: background-color 180ms ease;
  cursor: pointer;
}

.btn-primary:hover {
  background: #E39D00;
}

/* Secondary */
.btn-secondary {
  background: #FFFCF7;
  color: #5B3918;
  border: 1px solid rgba(91, 57, 24, 0.18);
  padding: 6px 10px;
  border-radius: 8px;
  font-weight: 500;
  transition: background-color 180ms ease, border-color 180ms ease;
  cursor: pointer;
}
```

### Cards

```css
.card {
  background: #FFFCF7;
  border: 1px solid rgba(91, 57, 24, 0.14);
  border-radius: 12px;
  padding: 12px;
  box-shadow: 0 1px 2px rgba(36, 22, 9, 0.06);
  transition: border-color 180ms ease;
}

.card:hover {
  border-color: rgba(91, 57, 24, 0.28);
}
```

### Inputs

```css
.input {
  padding: 6px 12px;
  border: 1px solid rgba(91, 57, 24, 0.22);
  border-radius: 8px;
  background: #FFFCF7;
  color: #5B3918;
  font-size: 14px;
  transition: border-color 180ms ease;
}

.input:focus-visible {
  outline: 2px solid #241609;
  outline-offset: 2px;
}
```

### Modals

```css
.modal-overlay {
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

.modal {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: var(--shadow-xl);
  max-width: 500px;
  width: 90%;
}
```

---

## Style Guidelines

**Style:** Minimalism & Swiss Style

**Keywords:** Clean, simple, spacious, functional, white space, high contrast, geometric, sans-serif, grid-based, essential

**Best For:** Enterprise apps, dashboards, documentation sites, SaaS platforms, professional tools

**Key Effects:** Subtle hover (200-250ms), smooth transitions, sharp shadows if any, clear type hierarchy, fast loading

### Page Pattern

**Pattern Name:** Hero + Features + CTA

- **Conversion Strategy:** Deep CTA placement. For CTA label text, verify at least 4.5:1 against the button fill; use 7:1 only when the product explicitly targets AAA normal-text contrast. Keep focus and component boundaries independently visible. Disable hero parallax under reduced motion and render its static final state.
- **CTA Placement:** Hero (sticky) + Bottom
- **Section Order:** Hero with headline/image > Value prop > Key features (3-5) > CTA section > Footer

---

## Motion

**Scroll Reveal** (Subtle) — Trigger: scroll (viewport enter) | Duration: 300-400ms | Easing: `power1.out`

```js
gsap.from(el, { opacity: 0, y: 12, duration: 0.35, ease: 'power1.out', scrollTrigger: { trigger: el, start: 'top 90%', toggleActions: 'play none none reverse' } });
```

**Framework notes:** Requires the ScrollTrigger plugin registered once via gsap.registerPlugin(ScrollTrigger); Use matchMedia('(prefers-reduced-motion: reduce)') to skip non-essential motion and render the final state immediately

- ✅ Keep the y offset small (8-16px) so it reads as a fade, not a slide
- ❌ Don't reveal below-the-fold content needed for SEO/crawlers as invisible-by-default without a no-JS fallback
- ⚡ toggleActions 'play none none reverse' avoids re-triggering on every scroll direction change

---

## Anti-Patterns (Do NOT Use)


### Additional Forbidden Patterns

- ❌ **Emojis as icons** — Use SVG icons (Heroicons, Lucide, Simple Icons)
- ❌ **Missing cursor:pointer** — All clickable elements must have cursor:pointer
- ❌ **Layout-shifting hovers** — Avoid scale transforms that shift layout
- ❌ **Low contrast text** — Maintain 4.5:1 minimum contrast ratio
- ❌ **Instant state changes** — Always use transitions (150-300ms)
- ❌ **Invisible focus states** — Focus states must be visible for a11y

---

## Pre-Delivery Checklist

Before delivering any UI code, verify:

- [ ] No emojis used as icons (use SVG instead)
- [ ] All icons from consistent icon set (Heroicons/Lucide)
- [ ] `cursor-pointer` on all clickable elements
- [ ] Hover states with smooth transitions (150-300ms)
- [ ] Light mode: text contrast 4.5:1 minimum
- [ ] Focus states visible for keyboard navigation
- [ ] `prefers-reduced-motion` respected
- [ ] Responsive: 375px, 768px, 1024px, 1440px
- [ ] No content hidden behind fixed navbars
- [ ] No horizontal scroll on mobile
