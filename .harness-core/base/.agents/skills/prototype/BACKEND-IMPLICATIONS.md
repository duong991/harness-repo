# Backend Implications

Use this reference only after a validated prototype reveals backend-relevant
behavior. It records implementation-relevant questions without turning UI or a
throwaway model into backend authority.

Capture only what the validated behavior makes observable:

1. Capabilities the system needs to provide.
2. Data and query needs.
3. Commands and their visible results.
4. Authorization boundaries.
5. State transitions and lifecycle constraints.
6. Failure, retry, stale-data, concurrency, and auditability expectations when
   they are exposed by the behavior.
7. Open backend questions and their deciding authority.

Example: “A user can bulk assign devices” implies a bulk-assignment capability.
It does not choose `POST /devices/bulk-assign`, a resource shape, a DTO, or a
controller/service/repository architecture. Send durable terms to
`domain-modeling` and interface/module choices to `codebase-design`.
