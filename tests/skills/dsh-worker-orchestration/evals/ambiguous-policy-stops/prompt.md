---
tags: [skill-creator]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Giao cho dsh làm cho slugify hỗ trợ tiêu đề tiếng Việt có dấu, ví dụ "Xin chào Việt Nam".

(Môi trường test: dùng DSH giả — chạy mọi lệnh với `export DSH_BIN=$PWD/.dsh-test/fake-dsh DSH_WORKTREE_ROOT=$PWD/../dsh-worktrees`.)
