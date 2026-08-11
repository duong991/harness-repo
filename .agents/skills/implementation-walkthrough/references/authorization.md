# Authorization Review Reference

Load this reference only when a change materially crosses authentication,
authorization, tenant/resource scope, policy evaluation, or authorization
cache boundaries. It supplies architecture questions for a walkthrough; it
does not create findings or decide whether a policy is correct.

## Questions

- Where is the authentication context established?
- Where is the authorization decision made, and is the default fail-open or
  fail-closed?
- Which route, service, repository, or storage boundary enforces the decision?
- Can direct service invocation bypass route-level enforcement?
- Where is tenant, resource, or location scope applied?
- What privileged, bypass, skip, or super-admin paths exist?
- Are denial responses and side effects consistent across paths?
- How is cached authorization invalidated after policy, role, or membership
  changes?
- What happens for missing user context, missing resource, wrong scope, and
  stale policy state?
- Which tests exercise the decision boundary, and which dependencies are fully
  mocked?

## Critical path template

```text
Request
→ Authentication
→ User Context
→ Ability/Policy Construction
→ Route Authorization
→ Resource/Scope Authorization
→ Scoped Query or Sensitive Operation
→ Response and Side Effects
```

Trace the primary allowed path plus denied, wrong-scope, missing-resource, and
privileged-bypass cases when the implementation exposes them. Treat a search
hit such as `allow`, `bypass`, or `return true` as a Risk Probe result until
the surrounding call path and authority are inspected.

## Invariants to consider

- Every sensitive operation has an enforcement boundary reachable outside the
  UI or caller.
- A denied or wrong-scope request cannot perform the protected side effect.
- Tenant/resource scope is preserved through query, cache, and response paths.
- Role, policy, or membership changes invalidate relevant authorization state.
- Direct service calls cannot silently bypass the intended policy boundary.

Record which invariant is observed, partially observed, supplied as existing
evidence, or not independently verified. Do not claim coverage or compliance
from this reference alone.
