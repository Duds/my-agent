# UI Scaffold Integration Strategy

This document outlines the strategy for integrating the Vercel V0 UI scaffold from `.temp/scaffold_unzipped/` into the frontend.

## Prerequisites

1. Install scaffold dependencies (add to `frontend/package.json`):
   - `lucide-react`, `class-variance-authority`, `clsx`, `tailwind-merge`
   - `@radix-ui/*` components (accordion, dialog, dropdown, etc.)
   - `next-themes`, `cmdk`, `sonner`, `vaul`, `react-resizable-panels`
   - See `.temp/scaffold_unzipped/package.json` for full list

2. Create directory structure:
   - `frontend/src/components/` - Main components
   - `frontend/src/components/ui/` - shadcn/ui components
   - `frontend/src/lib/` - Utilities and store
   - `frontend/src/hooks/` - Custom hooks

## Integration Phases

### Phase 1: Component Migration
1. Copy `lib/utils.ts` to `frontend/src/lib/utils.ts`
2. Copy `lib/store.ts` to `frontend/src/lib/store.ts` (adapt for API later)
3. Copy `components/ui/*` to `frontend/src/components/ui/`
4. Copy `components/theme-provider.tsx`, `theme-toggle.tsx`
5. Copy `components/app-sidebar.tsx`, `chat-interface.tsx`, etc.
6. Copy `hooks/` to `frontend/src/hooks/`
7. Update all `@/` imports to match `tsconfig.json` paths

### Phase 2: Layout Integration
1. Merge scaffold `layout.tsx` with existing - add ThemeProvider, AppSidebar
2. Update `globals.css` with scaffold styles if needed
3. Add sidebar state (collapsed, active conversation)

### Phase 3: Data Integration
1. Replace mock data in `store.ts` with API calls to backend
2. Create API client in `frontend/src/lib/api-client.ts`
3. Connect PersonaSelector and ModelSelector to backend
4. Implement real conversation loading

### Phase 4: Feature Connection
1. Connect StatusBar to backend `/health` or process endpoint
2. Connect ChatInterface to `/query` endpoint
3. Connect SettingsPanel to configuration API

### Phase 5: Verification
- `npm run lint`
- `npm run build`
- Manual testing of all sidebars and features

## Verification Checklist

- [ ] All components compile without TypeScript errors
- [ ] All sidebars (Processes, Automations, Cron Jobs) render
- [ ] Persona selector updates UI state
- [ ] Model selector updates UI state
- [ ] Theme switching works (dark/light)
- [ ] Chat interface connects to backend `/query` endpoint
- [ ] Port mismatch resolved (8000 vs 8001)
- [ ] TypeScript interfaces defined for all API responses
