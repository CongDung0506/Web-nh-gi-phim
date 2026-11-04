# Nhật ký sử dụng AI Tool — CineVerse (Movie CMS & Cinema Community)

Minh hoạ nội dung phương pháp luận phát triển web có sự hỗ trợ của AI (Prompt engineering, AI code review, ranh giới an toàn bảo mật và chuẩn hoá dữ liệu).

---

## Ví dụ 1 — Sinh route bình luận phim `add_comment` và phòng chống XSS

**Prompt gửi cho AI (Copilot / Assistant):**
> "Viết route Flask POST /movies/<id>/comments nhận Markdown cảm nhận phim từ người dùng, chuyển đổi sang HTML để lưu vào SQL Server, yêu cầu người dùng phải đăng nhập."

**Code AI đề xuất ban đầu (Chưa tối ưu bảo mật):**
```python
@app.route("/movies/<int:movie_id>/comments", methods=["POST"])
@login_required
def add_comment(movie_id):
    body_md = request.form.get("body_md")
    body_html = markdown.markdown(body_md)   # <-- AI KHÔNG sanitize
    comment = MovieComment(movie_id=movie_id, body_html=body_html)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for("movie_comments", movie_id=movie_id))
```

**Phân tích & Review bảo mật thủ công:**
- ⚠️ **Lỗ hổng nghiêm trọng:** Nếu kẻ tấn công gửi mã Markdown chứa thẻ độc hại như `<script>alert(document.cookie)</script>` hoặc link `[click](javascript:stealData())`, hàm `markdown.markdown()` giữ nguyên thẻ script. Khi hiển thị với bộ lọc `|safe` trong Jinja2, mã độc sẽ kích hoạt trên trình duyệt của người dùng khác (Stored XSS).
- ✅ **Khắc phục:** Sử dụng thư viện `bleach.clean()` với `COMMENT_ALLOWED_TAGS` nghiêm ngặt (chỉ cho phép `strong`, `em`, `code`, `a`, cấm tuyệt đối các thẻ tiêu đề `h1-h6` và `script/iframe`).
- ✅ **Kiểm tra rỗng:** Thêm `.strip()` để ngăn chặn gửi bình luận rác hoặc chuỗi khoảng trắng.

---

## Ví dụ 2 — Truy vấn các bài viết của người được theo dõi (`followed_posts`)

**Prompt gửi cho AI:**
> "Viết property `followed_posts` trong model `User` để lấy danh sách bài viết từ các nhà phê bình mà người dùng đang follow, sắp xếp bài mới nhất lên đầu."

**Code AI phản hồi & Tối ưu hoá:**
AI đề xuất sử dụng cú pháp kết hợp JOIN giữa bảng `MoviePost` và bảng liên kết `Follow`:
```python
@property
def followed_posts(self):
    return (MoviePost.query
            .join(Follow, Follow.followed_id == MoviePost.author_id)
            .filter(Follow.follower_id == self.id)
            .order_by(MoviePost.created_at.desc()))
```
- ✅ **Đánh giá:** Câu lệnh ORM thực hiện phép `JOIN` trực tiếp ở mức database (thay vì lôi toàn bộ danh sách user về xử lý bằng vòng lặp Python), đảm bảo hiệu năng cao khi số lượng bài viết và lượt follow tăng lên.

---

## Ví dụ 3 — Đảm bảo quyền riêng tư người dùng với Avatar Gravatar

Thay vì bắt người dùng tải ảnh cá nhân lên máy chủ (tiềm ẩn nguy cơ upload file độc hại qua shell script hoặc tốn tài nguyên lưu trữ), hệ thống sử dụng thuật toán băm **MD5 từ email** của người dùng để liên kết với hệ sinh thái Gravatar toàn cầu:
```python
def gravatar_url(self, size=80):
    email_hash = hashlib.md5(self.email.strip().lower().encode("utf-8")).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s={size}"
```
- ✅ **Bảo mật & Quyền riêng tư:** Email thật không bao giờ bị lộ ra mã nguồn HTML bên ngoài, chỉ có mã băm hash một chiều được truyền tải.
