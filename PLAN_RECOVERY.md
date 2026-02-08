# Recovery Plan: Security, Model Switching & PII Management

**Last commit:** `838579f` (08/02/2026)  
**Commit message:** "feat: Implement task-specific model routing, PII redaction, system status checks, and Ollama daemon control."

---

## What Was Completed (Last Commit)

| Area | Status | Files Changed |
|------|--------|---------------|
| **Task-specific model routing** | ✅ Implemented | `core/router.py`, `core/config.py` |
| **Security validator** | ✅ Implemented | `core/security.py` |
| **PII redactor** | ✅ Implemented | `core/security.py`, `core/router.py` |
| **Intent classifier (LLM-based)** | ✅ Implemented | `core/intent_classifier.py`, `core/router.py` |
| **Routing config API** | ✅ Implemented | `core/main.py` – GET/POST `/api/config/routing` |
| **System status & Ollama control** | ✅ Implemented | `core/main.py`, `frontend`, `manage.sh` |
| **Settings panel routing UI** | ✅ Implemented | `frontend/src/components/settings-panel.tsx` |
| **API client** | ✅ Implemented | `frontend/src/lib/api-client.ts` |

### Current Behaviour

- **Routing config** is loaded from `data/routing_rules.json` (created on first save; directory is empty initially).
- **Meta-tasks** assignable per model: `intent_classification`, `security_judge`, `pii_redactor`.
- **Security flow:** heuristic checks → LLM judge (if configured) → answer or block.
- **PII flow:** after security check, output is redacted if `pii_redactor` is configured.
- **Frontend:** Settings → Routing tab lets you pick models for each meta-task; "Best Local (Auto)" sends `"auto"` (no override).

---

## Gaps & Incomplete Items

### 1. Streaming Bypasses Security & PII (High) ✅ FIXED

**Where:** `route_request_stream()` in `core/router.py`

**Issue:** Streaming responses were not security-checked or PII-redacted.

**Fix applied:** Buffer full response (Ollama streaming) or use non-streaming path (remote), then run security check and PII redaction before yielding. Both paths now apply security and PII.

---

### 2. No Default `data/routing_rules.json` (Medium) ✅ FIXED

**Issue:** Config only created when user saves from UI.

**Fix applied:** In `core/main.py` lifespan, create `data/routing_rules.json` with `{}` on first startup if missing. Router reloads config after models are discovered.

---

### 3. "auto" Handling in Router (Low) ✅ FIXED

**Issue:** `"auto"` is stored and passed to `_resolve_model_to_adapter("auto")`, which returns `None`. That works for intent classifier and security (reverts to defaults), but it’s implicit.

**Action:** Explicitly treat `"auto"` / empty as “use default” and skip `_resolve_model_to_adapter` for those values.

---

### 4. PII Redaction Policy (Medium) ✅ DOCUMENTED

**Considerations:**

- **Scope:** Is PII redaction always-on, or only when sending to remote?
- **Mode:** Should Private mode disable PII redaction (everything stays local)?
- **Logging:** Security rules say “Never log PII” – confirm no PII in logs from `SecurityValidator` / `PIIRedactor`.

---

### 5. No Tests for New Features (Medium) ✅ FIXED

**Fix applied:** PIIRedactor tests in `tests/security/test_security.py`; routing config tests in `tests/routing/test_routing_config.py`; API tests for `/api/config/routing` and `/api/system/status` in `tests/test_api_auth.py`.

### 6. Logging Audit (Phase 2) ✅ FIXED

**Fix applied:** Removed `logger.debug` of verdict text in `SecurityValidator`. Changed `PIIRedactor` error logging to avoid logging user content.

---

## Recommended Next Steps (Prioritised)

### Phase 1: Critical Fixes (≈1–2 hours)

1. **Streaming security**  
   Choose and implement one of the options above (buffer-then-stream, or document/restrict streaming).

2. **Default routing config**  
   Create `data/routing_rules.json` on first startup if missing (e.g. empty `{}` or minimal defaults).

### Phase 2: Clarifications & Compliance (≈1 hour)

3. **PII policy**  
   Decide scope (all vs remote-only, per-mode) and document behaviour.

4. **Logging audit**  
   Ensure `SecurityValidator` and `PIIRedactor` do not log PII or sensitive data.

### Phase 3: Cleanup & Tests (≈2–3 hours)

5. **Explicit "auto" handling**  
   In `_apply_routing_config`, skip `_resolve_model_to_adapter` when value is `"auto"` or empty.

6. **Tests**  
   Add unit tests for security and PII; add integration tests for routing and system APIs.

### Phase 4: Optional Enhancements

7. **Privacy Vault UI** (PBI-030)  
   UI to show/manage local-only sensitive data.

8. **MCP Server config** (PBI-027)  
   Backend API and settings UI for MCP discovery.

---

## Quick Verification Checklist

Before coding further, verify:

- [ ] Backend: `./manage.sh start` and `GET /api/system/status` returns Ollama/backend/frontend status.
- [ ] Frontend: Settings → Routing tab shows Intent Classification, Security Judge, PII Redactor.
- [ ] Changing a meta-task model and saving updates `data/routing_rules.json`.
- [ ] Non-streaming `/query` goes through security and PII redaction when configured.
- [x] Streaming `/query/stream` now applies security and PII (buffers then processes).

---

## File Reference

| File | Purpose |
|------|---------|
| `core/router.py` | Model routing, task assignment, security/PII hooks |
| `core/security.py` | `SecurityValidator`, `PIIRedactor` |
| `core/intent_classifier.py` | Intent classification (semantic + optional LLM) |
| `core/config.py` | `routing_config_path` |
| `core/main.py` | Routing config API, system status, Ollama start/stop |
| `frontend/src/components/settings-panel.tsx` | Routing UI |
| `frontend/src/lib/api-client.ts` | `getRoutingConfig`, `updateRoutingConfig`, `getSystemStatus`, `startOllama`, `stopOllama` |
| `data/routing_rules.json` | Task-specific model assignments (created on first save) |

---

## Related Documentation

- **[docs/CONFIG_UI_DESIGN.md](docs/CONFIG_UI_DESIGN.md)** – Design guidelines for adding feature configuration to the Settings panel (domain structure, progressive disclosure, checklist).

---

*Last updated: 08/02/2026*
