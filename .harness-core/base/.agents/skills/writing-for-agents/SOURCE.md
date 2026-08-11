# Source

- Origin: Adapted upstream skill
- Upstream repository: https://github.com/mattpocock/skills
- Source path: `skills/productivity/writing-for-agents/`
- Commit: `84fdeffd12f2ee307994d1eb6feb48173b6e0502`
- License: MIT
- Copied: 2026-08-11
- Owner: gnoud
- Activation: Model-invoked; `allow_implicit_invocation: true`
- Local modifications: replaces upstream frontmatter mechanics with the Harness
  `SKILL.md` description plus `agents/openai.yaml` policy; requires repository
  authority and preserves the single-router model.
- Update method: compare a newer immutable upstream commit, retain Harness
  authority and activation rules, snapshot the revised tree atomically, and run
  the Harness skill validator.

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
