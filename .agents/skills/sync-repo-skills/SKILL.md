---
name: sync-repo-skills
description: "Quét và đồng bộ kỹ năng (agent skills) từ repository chuẩn sang các repository khác. Phân tích hiện trạng, lập bảng so sánh thay đổi, hỏi xác nhận người dùng và thực thi đồng bộ an toàn."
---

# Sync Repo Skills

Quét và đồng bộ các kỹ năng (Agent Skills) giữa repository chuẩn hiện tại (Source of Trust) và một consumer repository đích bất kỳ.

> **Nguyên tắc cốt lõi (theo tinh thần Matt Pocock)**:
> Đây là một **prompt-driven skill** có sự tham gia của Agent và người dùng, không phải một script chạy ngầm tự ý ghi đè mù quáng. Script chỉ là công cụ bổ trợ thu thập dữ liệu; Agent khám phá, tổng hợp thành bảng trực quan, đề xuất phương án và chỉ thực thi khi người dùng đã duyệt (accept).

---

## Quy trình 5 bước

### 1. Khám phá (Explore)
Khi người dùng yêu cầu đồng bộ skill sang một repository đích (ví dụ: `~/dev/workInVNPT/<repo>`):
1. Xác định đường dẫn tuyệt đối của repo đích (`target_path`).
2. Chạy script bổ trợ ở chế độ scan structured:
   ```bash
   python3 scripts/sync-skills.py --target <target_path> --json
   ```
3. Đọc dữ liệu JSON trả về để nắm bắt:
   - Danh sách kỹ năng mới ở chuẩn chưa có ở target (`source_only`).
   - Danh sách kỹ năng có khác biệt nội dung (`diverged`).
   - Danh sách kỹ năng riêng của target (`target_only`).
   - Trạng thái liên kết symlink trong `.claude/skills/`.

---

### 2. Trình bày hiện trạng (Present Findings)
Lập bảng so sánh có cấu trúc trực quan để người dùng nắm rõ toàn bộ thay đổi trước khi quyết định:

| Nhóm | Tên kỹ năng | Trạng thái | Chi tiết / Mô tả | Khuyến nghị của Agent |
| :--- | :--- | :--- | :--- | :--- |
| **Mới (New)** | `skill-name` | Chưa có ở target | Tóm tắt mục đích kỹ năng | Thêm mới từ chuẩn |
| **Cập nhật (Diverged)** | `skill-name` | Nội dung khác biệt | Danh sách file thay đổi | Cập nhật theo chuẩn |
| **Riêng biệt (Target-only)** | `skill-name` | Chỉ có ở target | Kỹ năng nghiệp vụ/dự án | Giữ nguyên (bảo toàn) |
| **Lỗi thời (Obsolete)** | `skill-name` | Đã gỡ ở chuẩn | Kỹ năng cũ không còn dùng | Hỏi ý kiến dọn dẹp |

Đồng thời báo cáo tình trạng liên kết `.claude/skills/` (hợp lệ hay cần chuẩn hoá).

---

### 3. Phỏng vấn & Chốt yêu cầu (Interview & Confirm)
- Đưa ra phương án khuyến nghị rõ ràng nhất (thường là: thêm kỹ năng mới + cập nhật kỹ năng khác biệt + giữ nguyên kỹ năng riêng của target).
- Hỏi người dùng chốt phương án qua câu hỏi ngắn gọn (hoặc qua `ask_user_question` khi cần lựa chọn nhiều nhánh).
- **Tuyệt đối không tự ý ghi đè hay xoá skill khi người dùng chưa đồng ý**.

---

### 4. Thực thi đồng bộ (Apply)
Sau khi người dùng đã xác nhận phạm vi:
- Nếu đồng bộ toàn bộ (thêm mới + cập nhật):
  ```bash
  python3 scripts/sync-skills.py --target <target_path> --apply --sync-all
  ```
- Nếu chỉ đồng bộ một số skill cụ thể:
  ```bash
  python3 scripts/sync-skills.py --target <target_path> --apply --sync <skill1,skill2,...>
  ```
- Nếu người dùng đồng ý dọn dẹp các skill lỗi thời đã gỡ ở chuẩn:
  ```bash
  python3 scripts/sync-skills.py --target <target_path> --apply --prune <old_skill1,old_skill2,...>
  ```

*Script sẽ tự động tạo thư mục backup trong `.harness-core/source-sync-backups/` và tự động chạy `scripts/link-claude-skills.py` trên target để map lại các symlink `.claude/skills`.*

---

### 5. Kiểm định & Bàn giao (Verification & Handoff)
1. Chạy lệnh kiểm tra tính hợp lệ của link Claude trên target:
   ```bash
   python3 <target_path>/scripts/link-claude-skills.py --check
   ```
2. Nếu target có bộ kiểm thử Harness SDLC:
   ```bash
   cd <target_path> && ./scripts/test-harness-skills
   ```
3. Báo cáo bản ghi kiểm định (Verification Record):
   - Danh sách skill đã thêm mới.
   - Danh sách skill đã cập nhật.
   - Danh sách skill đã dọn dẹp.
   - Đường dẫn thư mục backup.
   - Nhắc nhở người dùng: Toàn bộ file chỉ mới nằm ở working directory, chưa bị staged hoặc commit vào Git để người dùng tự review `git diff`.
