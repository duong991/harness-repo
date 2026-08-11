# Source

- Origin: Adapted upstream skill
- Upstream repository: https://github.com/mattpocock/skills
- Source path: `skills/engineering/prototype/`
- Commit: `84fdeffd12f2ee307994d1eb6feb48173b6e0502`
- License: MIT
- Copied: 2026-08-11
- Owner: gnoud
- Activation: Model-invoked; `allow_implicit_invocation: true`
- Local modifications: splits generic UI and logic exploration from optional
  backend implications; removes upstream assumptions about HTML artifacts,
  throwaway branches, and automatic production-adjacent placement; adds Harness
  routing, authority, capability-scope, promote/remove, and no-UI-to-API rules.
- Update method: compare a newer immutable upstream commit, retain local
  authority and non-orchestration rules, snapshot atomically, and run the
  Harness skill validator.

## MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
