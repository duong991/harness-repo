---
tags: [skill-creator]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Test slugify đang fail (gộp khoảng trắng liên tiếp, bỏ gạch ở đầu/cuối — xem docs/product/slugs.md). Giao việc sửa src/slugify.py cho dsh worker làm giúp mình nhé, chỉ được sửa src/slugify.py và tests/.

(Môi trường test: dùng DSH giả — chạy mọi lệnh với `export DSH_BIN=$PWD/.dsh-test/fake-dsh DSH_WORKTREE_ROOT=$PWD/../dsh-worktrees`.)
