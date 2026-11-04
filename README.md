# CineVerse — Movie Review & Cinema Community CMS

Hệ thống CMS chuyên ngành **Điện ảnh & Phim ảnh** được xây dựng dựa trên kiến trúc Web và tính năng cộng đồng (Chapter 8 - PWD301).

---

## 1. Tính năng cốt lõi (Theo yêu cầu Demo)

1. **Avatar bảo mật qua Gravatar**: 
   - Không lưu file ảnh trực tiếp trên máy chủ nhằm bảo vệ quyền riêng tư người dùng.
   - Sử dụng thuật toán băm **MD5 từ email** để đồng bộ với Gravatar toàn cầu.

2. **Hệ thống Theo dõi (Follow System)**:
   - Mô hình quan hệ tự tham chiếu Nhiều - Nhiều (`self-referential many-to-many`) trên bảng `users`.
   - Thuộc tính `followed_posts` thực hiện truy vấn `JOIN` tối ưu trực tiếp từ database để lấy bài viết của các nhà phê bình được theo dõi.

3. **Trang chủ Cá nhân hoá (Personalized Feed qua Cookie)**:
   - Cho phép khán giả chuyển đổi giữa: **"Tất cả bài viết"** và **"Chỉ xem người tôi follow"**.
   - Lưu trữ trạng thái lựa chọn qua cookie `show_followed` trong 30 ngày.

4. **Hệ thống Đánh giá & Bình luận Phim (Movie Review & Comments)**:
   - Hỗ trợ định dạng **Markdown** (in đậm, in nghiêng, trích dẫn, danh sách).
   - Cơ chế bảo mật kép: Sử dụng thư viện `bleach.clean()` với `COMMENT_ALLOWED_TAGS` loại bỏ triệt để mã độc `<script>` hoặc liên kết nguy hiểm (chống Stored XSS tuyệt đối).

5. **Phân trang (Pagination) cho CMS**:
   - Tối ưu tải trang danh sách bài đánh giá với phương thức `paginate(page=page, per_page=3)`.

6. **Nhật ký Ứng dụng AI (`ai_demo/copilot_log.md`)**:
   - Ghi lại quá trình ứng dụng Copilot / AI Assistant trong việc sinh mã nguồn, rà soát lỗ hổng bảo mật XSS và tối ưu câu lệnh truy vấn ORM.

---

## 2. Hướng dẫn Cài đặt & Khởi chạy

### Bước 1: Kích hoạt môi trường ảo
```powershell
.\..\thuchanh\.venv\Scripts\Activate.ps1
```

### Bước 2: Cài đặt thư viện (nếu cần)
```powershell
pip install -r requirements.txt
```

### Bước 3: Nạp dữ liệu mẫu vào SQL Server
```powershell
python seed_cinema.py
```
*(Lệnh sẽ tự động tạo cơ sở dữ liệu `CineVerse_DB` trên Microsoft SQL Server và nạp các bộ phim, người dùng, bài review mẫu).*

### Bước 4: Khởi chạy ứng dụng Web
```powershell
python app.py
```
Truy cập trình duyệt: **`http://127.0.0.1:5000`**

---

## 3. Tài khoản Demo có sẵn (Đăng nhập nhanh 1-Click)

| Vai trò (Role) | Username | Mô tả |
| :--- | :--- | :--- |
| **Admin** | `christopher_nolan` | Đạo diễn & Quản trị viên (có toàn quyền, viết bài review) |
| **Critic** | `roger_ebert` | Nhà phê bình điện ảnh (có quyền xuất bản bài Review CMS) |
| **Member** | `mai_cinephile` | Khán giả yêu phim (theo dõi tác giả, gửi bình luận/đánh giá) |

---

## 4. Kịch bản Demo thực nghiệm trên lớp

1. **Trang chủ cá nhân hoá**: Đăng nhập nhanh với `mai_cinephile`, bấm **"Chỉ xem người tôi follow"** ➔ Trang web lọc chỉ hiển thị bài của `roger_ebert` và `christopher_nolan`. Tải lại trang để kiểm chứng lựa chọn được lưu qua Cookie.
2. **Hồ sơ & Follow**: Truy cập `/users/roger_ebert`, xem avatar Gravatar, số lượng người theo dõi, bấm nút **Bỏ theo dõi / Theo dõi**.
3. **Kho phim & Bình luận chống XSS**: Vào `/movies/1/comments`, thử nhập bình luận có chứa mã script `<script>alert('hack')</script> **Phim rất hay**` ➔ Hệ thống tự động triệt tiêu thẻ script và chỉ hiển thị chữ in đậm.
4. **Viết bài Review (CMS)**: Đăng nhập tài khoản Critic `roger_ebert`, truy cập `/reviews/new` để viết bài đánh giá phim bằng Markdown và xuất bản.
5. **Nhật ký AI**: Mở menu **Nhật ký AI** (`/ai-log`) để thuyết trình về ứng dụng AI trong quy trình phát triển web an toàn.
