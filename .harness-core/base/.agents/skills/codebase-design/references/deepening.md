# Deepening

Classify dependencies before changing a module shape:

1. **In-process:** merge behavior and test the resulting interface directly.
2. **Local-substitutable:** use the real local stand-in in focused tests; keep
   the seam internal unless callers need it.
3. **Remote but owned:** define a port only when production and test adapters
   are real variations; inject the transport adapter.
4. **True external:** inject a narrow external port and use a mock adapter in
   focused tests.

One adapter is a hypothetical seam; two justified adapters make it real. Do
not expose internal test seams through the external interface. When replacing
shallow modules with a deeper module, replace implementation-coupled tests with
behavioral tests at the new interface rather than layering both suites.
