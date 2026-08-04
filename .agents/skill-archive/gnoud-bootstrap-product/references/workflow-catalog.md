# Product Bootstrap Workflow Catalog

Use these templates as phase-specific instructions after the router in
`SKILL.md` selects a route. Replace bracketed placeholders with task-local
facts. Preserve the no-code, no-story, and no-CLI boundaries unless the
selected phase explicitly changes them.

## Contents

1. [Repository survey](#1-repository-survey)
2. [Product grill](#2-product-grill)
3. [Product brief](#3-product-brief)
4. [Design brief](#4-design-brief)
5. [Architecture](#5-architecture)
6. [Technology decision](#6-technology-decision)
7. [Minimal scaffold](#7-minimal-scaffold)
8. [First vertical slice](#8-first-vertical-slice)
9. [Tiny fix](#9-tiny-fix)
10. [Bounded change](#10-bounded-change)
11. [Active plan](#11-active-plan)
12. [CLI decision](#12-cli-decision)
13. [CLI story proposal](#13-cli-story-proposal)
14. [Worker execution](#14-worker-execution)
15. [Independent review](#15-independent-review)
16. [Reconciliation](#16-reconciliation)
17. [Completion audit](#17-completion-audit)
18. [Daily router](#18-daily-router)

## 1. Repository survey

Use immediately after reading `AGENTS.md` and `docs/WORKFLOW.md`:

```text
Đây là một repository mới hoặc early-stage repository.

Hãy khảo sát ở chế độ read-only và báo cáo:
1. Thành phần Harness hoặc tooling hiện có.
2. Tài liệu sản phẩm, thiết kế, kiến trúc còn thiếu.
3. Quyết định cần chốt trước khi tạo source code.
4. Cấu trúc tài liệu tối thiểu nên bổ sung.
5. Workflow nhẹ nhất cho giai đoạn hiện tại.

Không tạo story, không dùng Harness CLI, không tạo source code.
Phân biệt rõ Observed, Assumption, Decision required và Unknown.

Kết thúc bằng:
- Observed repository state
- Missing authorities
- Open decisions
- Recommended next step
```

## 2. Product grill

Use when repository evidence cannot establish product intent. Ask one question
at a time and give a recommended answer. Do not design architecture or write
code during the grill.

```text
Tôi muốn xây dựng sản phẩm sau:

[Mô tả ý tưởng ban đầu]

Hãy làm rõ:
1. Người dùng chính và vai trò.
2. Vấn đề thực tế cần giải quyết.
3. Công việc quan trọng nhất người dùng phải hoàn thành.
4. Phạm vi MVP và out of scope.
5. Loading, empty, error, disabled và permission states.
6. Nguồn dữ liệu và tích hợp.
7. Yêu cầu bảo mật và vận hành.
8. Tiêu chí thành công có thể kiểm chứng.
9. Các quyết định sản phẩm còn mở.

Không đề xuất framework, không tạo code, không tạo story.
Kết thúc bằng một Product Change Brief ngắn.
```

For a SOC dashboard, also resolve alert lifecycle, SIEM/EDR data, severity,
case closure, realtime expectations, audit needs, and demo success criteria.

## 3. Product brief

Create `docs/product/product-brief.md` only after the grill answers are
confirmed:

```text
Đọc AGENTS.md, docs/WORKFLOW.md và kết quả grill-me.

Tạo docs/product/product-brief.md gồm:
- Product objective
- Người dùng và vai trò
- Vấn đề và user goals
- MVP và out of scope
- Luồng người dùng chính
- Functional và non-functional requirements
- Permission/security constraints
- Acceptance criteria cấp sản phẩm
- Open decisions
- Assumptions

Chỉ dùng thông tin đã xác nhận. Ghi điểm chưa rõ là Decision required.
Không tạo code, story hoặc dùng Harness CLI.
```

## 4. Design brief

For a product with UI, create `docs/design/design-brief.md` before components:

```text
Đọc AGENTS.md, docs/WORKFLOW.md và docs/product/product-brief.md.

Tạo docs/design/design-brief.md gồm:
- Cấu trúc màn hình và navigation model
- Information hierarchy
- Loading, empty, error, disabled, permission denied và stale data
- Responsive behavior
- Typography, color tokens, spacing và density
- Interaction rules và accessibility
- Pattern không được sử dụng
- Acceptance criteria giao diện

Không tạo mockup hoặc source code nếu còn quyết định thiết kế quan trọng.
Liệt kê riêng Decision required. Không tạo story.
```

For a VNPT/SOC variant, preserve these user-confirmed constraints when
applicable: Vietnamese UI except specialist terms, VNPT blue as primary color,
dark gray rather than absolute black, no top navbar, no numbered navigation,
meaningful icons only, analyst-friendly density, severity conveyed by color and
text, and readable investigation over decorative effects.

## 5. Architecture

Create `docs/ARCHITECTURE.md` after product authority exists and design
authority exists when UI is in scope:

```text
Đề xuất kiến trúc tối thiểu cho MVP.

Bao gồm:
1. System context và application boundaries.
2. Frontend architecture.
3. Backend/API boundary nếu có.
4. Data ownership.
5. Authentication/authorization.
6. State management.
7. Error handling.
8. Logging/observability.
9. Testing strategy.
10. Deployment assumptions.
11. Decisions cần ghi ADR.
12. Phần cố ý chưa xây trong MVP.

Chọn giải pháp đơn giản nhất đủ đáp ứng Product Brief. Không thêm queue,
microservice hoặc state framework nếu chưa có nhu cầu. Không tạo application
code.
```

## 6. Technology decision

For a lasting technology choice, compare only plausible options and record an
ADR using the repository template:

```text
Đọc Product Brief, Design Brief (nếu có), Architecture và decision template.

Đánh giá việc sử dụng [technology] theo:
- mức phù hợp với yêu cầu
- khả năng bảo trì
- ecosystem và testing
- team skill
- deployment
- long-term complexity

Nếu lựa chọn được chấp nhận, tạo docs/decisions/[id]-[slug].md.
Không scaffold project hoặc chọn library bổ sung ở bước này.
```

## 7. Minimal scaffold

Use only after the relevant authority exists:

```text
Tạo scaffold ứng dụng tối thiểu theo Product Brief, Design Brief,
Architecture và accepted decisions.

Yêu cầu:
1. Chỉ cài dependency cần cho application shell.
2. Tổ chức theo feature.
3. Tạo shell và route cơ bản.
4. Cấu hình lint, test và build.
5. README ghi đúng lệnh chạy thực tế.
6. Không tạo feature giả ngoài MVP.
7. Không thêm state/UI library nếu chưa có nhu cầu.
8. Không tạo story hoặc dùng Harness CLI.

Trước khi sửa: liệt kê file/dependency và lý do.
Sau khi sửa: chạy install, lint, test và production build; báo từng kết quả.
```

## 8. First vertical slice

Select the smallest complete user flow, not a static screen:

```text
Xác định và triển khai vertical slice nhỏ nhất tạo ra giá trị thật.

Flow phải đi qua các lớp cần thiết:
route → page → state → service → data adapter →
loading/empty/error state → test

Trước khi sửa, nêu:
1. User goal.
2. Điểm bắt đầu và kết thúc.
3. File/surface dự kiến.
4. Acceptance criteria.
5. Validation commands.
6. Phần cố ý chưa làm.

Không tạo Harness CLI story nếu có thể hoàn thành trong một phiên.
```

For an alert dashboard example, implement opening the alert list, loading,
empty/error states, mock adapter with a clear interface, selecting one alert,
and a basic detail panel. Leave investigation graphs, realtime, and case
workflow out unless authority says otherwise.

## 9. Tiny fix

```text
Sửa lỗi: [mô tả]

Hành vi hiện tại: [evidence]
Hành vi mong muốn: [mô tả]
Phạm vi không đổi: [danh sách]

Đây là tiny fix: không grill, không active plan, không story, không Harness CLI.
Trước khi sửa: tái hiện/xác định nguyên nhân và nêu patch tối thiểu.
Sau khi sửa: chạy validation liên quan, báo root cause, file đổi và evidence.
```

## 10. Bounded change

```text
Thực hiện bounded change: [mô tả]

Acceptance criteria:
1. [...]
2. [...]

Out of scope:
- [...]

Dùng ephemeral plan trong phiên:
1. Khảo sát baseline.
2. Xác định affected surfaces.
3. Triển khai patch nhỏ nhất.
4. Cập nhật test.
5. Chạy validation.

Không tạo active plan hoặc Harness CLI. Chỉ dừng trước khi sửa nếu còn lựa
chọn sản phẩm materially different mà repository chưa có authority.
```

## 11. Active plan

Use for multi-session work, meaningful dependencies, coordination, or recovery:

```text
Initiative: [mục tiêu lớn]

Tạo đúng một file docs/plans/active/[ten-plan].md theo template.
Gồm: Outcome, Current baseline, Authority, Scope, Out of scope, milestones
có thứ tự, dependencies, risks, recovery/rollback, validation từng milestone,
Decision required, Progress log và điều kiện chuyển sang completed.

Chưa tạo CLI story và chưa sửa application code ở bước này.
```

## 12. CLI decision

```text
Đánh giá initiative có thật sự cần Harness CLI không.

Chỉ kết luận cần CLI khi có nhiều worker độc lập, dependency machine-readable,
orchestrator tự chọn task, retry, locking/CAS, lifecycle qua nhiều phiên, JSON
status hoặc audit execution trace.

Trả về:
1. core-only hay core+CLI
2. Lý do và consumer của trạng thái
3. Dữ liệu ở active plan và dữ liệu ở SQLite
4. Chi phí vận hành
5. Điều kiện loại bỏ CLI

Không tạo story ở bước này.
```

## 13. CLI story proposal

Only use after the CLI decision says it is necessary:

```text
Phân rã initiative thành story theo hành vi/output kiểm chứng được.

Mỗi story phải có ID, title, user-visible outcome, scope, out of scope,
authority, dependency, acceptance criteria, verification command, worker role,
output artifact và failure/retry considerations.

Dependency phải là blocker thật; mỗi story phải validate độc lập.
Active plan là nguồn sự thật cho con người; SQLite là trạng thái cho
orchestrator. Hiển thị proposal trước, chỉ đăng ký sau khi không còn mâu thuẫn.
```

## 14. Worker execution

```text
Đọc AGENTS.md, active plan, authority và story được giao.

Xác minh story runnable, đọc đúng dependency output, không mở rộng scope,
cập nhật trạng thái theo contract, triển khai, chạy fresh verification, ghi
evidence và chỉ complete khi validation thành công.

Nếu bị block, ghi blocker cụ thể. Không tự tạo story, sub-agent hoặc thay đổi
dependency.
```

## 15. Independent review

Review read-only and do not trust the implementer's self-assessment:

```text
Kiểm tra patch theo rubric:
1. Đúng yêu cầu và không vượt scope.
2. Kiến trúc.
3. Loading, empty, error, permission và stale data.
4. Security và maintainability.
5. Test coverage.
6. Validation có chứng minh claim không.
7. Regression risk và documentation drift.

Mỗi finding phải có severity, claim, evidence, file/line, impact, correction
cần thiết và validation cần chạy lại. Chỉ pass khi có evidence. Không sửa code.
```

## 16. Reconciliation

```text
Đọc implementation artifact và independent review artifact.

Nhóm finding trùng, loại finding không có evidence, phân loại must-fix/follow-
up, xử lý mâu thuẫn bằng authority và validation, xác định patch tối thiểu và
validation chạy lại. Không mở scope và không dùng biểu quyết số lượng agent.

Kết luận đúng một trạng thái: accepted; accepted with required fixes; blocked
by decision; hoặc rejected.
```

## 17. Completion audit

```text
Đọc Product Brief, Design Brief, Architecture, active plan và implementation.

Kiểm tra acceptance criteria, milestones, must-fix findings, lint, unit,
integration/component, E2E nếu có, production build, runtime behavior,
documentation, open decisions và known limitations.

Trả về completed, partially completed, blocked hoặc failed. Chỉ chuyển active
plan sang completed khi mọi điều kiện đóng có evidence. Story state và trace
score không thay thế test hoặc runtime proof.
```

## 18. Daily router

```text
Đọc AGENTS.md và docs/WORKFLOW.md trước.

Tác vụ: [mô tả yêu cầu]

Phân loại: read-only analysis, tiny fix, bounded change, ambiguous product
change, multi-session initiative hoặc orchestrated multi-agent work.

Chọn workflow nhẹ nhất đủ an toàn. Chỉ chạy grill khi còn quyết định sản phẩm
materially different. Chỉ tạo active plan khi có nhiều phiên/dependency/recovery.
Chỉ dùng Harness CLI khi worker/orchestrator cần trạng thái machine-readable.
Không dùng trace/score thay cho test và không tự tạo sub-agent nếu lợi ích chưa
rõ.

Trước khi làm, nêu task class, authority, artifact, validation và có cần grill,
active plan hoặc CLI hay không. Sau đó thực hiện tác vụ.
```
