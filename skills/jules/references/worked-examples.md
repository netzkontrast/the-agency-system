This file contains worked examples of Jules interactions. Load this to see concrete examples of user requests and the corresponding API sequence, especially for creating and managing sessions.


**Create:**
```
User: /jules create refactor the auth middleware to use JWT and cover it with integration tests
Skill:
  Detected repo:   netzkontrast/the-agency-system → sources/<resolved-id>
  Detected branch: claude/create-jules-skill-x8QHA
  Plan approval:   REQUIRED (default)

  Created. ID: 7f3a91c2-…  State: QUEUED
  Session URL: https://jules.google.com/session/7f3a91c2-…
  → Polled once: state is now PLANNING.
  Run "/jules status 7f3a91c2-…" in a minute to check progress.
```

**Mandatory:** every time a new session is created (single or via fan-out),
print the **direct session URL** in the form
`https://jules.google.com/session/<sessionId>` on its own line. The URL is
returned in `jules_create`'s response as the `url` field. This is the link
the user clicks to open the session in the Jules web UI for inspection,
manual approval, or PR creation. Never omit it — even in compact bulk-create
output, render `id + url` together. For fan-out:

```
Created 3 sessions:
  - auth-fix         (7f3a91c2-…)  https://jules.google.com/session/7f3a91c2-…
  - tests-gen        (a8b4d219-…)  https://jules.google.com/session/a8b4d219-…
  - refactor-api     (c2e6f905-…)  https://jules.google.com/session/c2e6f905-…
```

**Status with plan ready:**
```
User: /jules status 7f3a91c2-…
Skill:
  State: AWAITING_PLAN_APPROVAL

  Jules has drafted this plan:
    1. Replace cookie-session middleware with jsonwebtoken in src/auth/
    2. Add JWT secret env var (JWT_SECRET) with dotenv fallback
    3. Add tests/integration/auth.spec.ts covering login + refresh
    4. Update README env-var section

  Approve, request changes, or cancel?
```

**Agent asks a question:**
```
User: /jules status 7f3a91c2-…
Skill:
  State: AWAITING_USER_FEEDBACK
  Jules asks: "The auth module currently has no mock interface. Should I
  add one in tests/mocks/, or wire the integration tests directly against
  the real middleware?"
  Reply with: /jules message 7f3a91c2-… <your answer>
```

**Completed:**
```
User: /jules status 7f3a91c2-…
Skill:
  State: COMPLETED
  Jules opened a pull request:
    https://github.com/netzkontrast/the-agency-system/pull/42
```

---
