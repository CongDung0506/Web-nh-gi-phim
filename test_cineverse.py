import unittest
from app import app
from models import db, User, Movie, MoviePost, MovieComment, Follow
from markdown_utils import render_markdown, COMMENT_ALLOWED_TAGS

class CineVerseTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

    def test_01_gravatar_hash(self):
        """Gravatar dua tren MD5 email."""
        with app.app_context():
            u = User.query.filter_by(username="christopher_nolan").first()
            self.assertIn("gravatar.com/avatar/", u.gravatar_url())

    def test_02_follow_and_followed_posts(self):
        """Kiem tra quan he follow va followed_posts."""
        with app.app_context():
            mai = User.query.filter_by(username="mai_cinephile").first()
            ebert = User.query.filter_by(username="roger_ebert").first()
            self.assertTrue(mai.is_following(ebert))
            posts = mai.followed_posts.all()
            self.assertGreater(len(posts), 0)

    def test_03_markdown_sanitize_xss_protection(self):
        """Test Markdown convert va chong XSS."""
        evil_input = "Phim hay! <script>alert('hack')</script> **Đoạn in đậm**"
        clean = render_markdown(evil_input, allowed_tags=COMMENT_ALLOWED_TAGS)
        self.assertNotIn("<script>", clean)
        self.assertIn("<strong>Đoạn in đậm</strong>", clean)

    def test_04_login_and_cookie_preference(self):
        """Dang nhap truyen thong va cookie show_followed."""
        # 1. Dang nhap voi form chuan
        res_login = self.client.post("/login", data={
            "username_or_email": "mai_cinephile",
            "password": "pass123",
            "remember_me": True
        }, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)
        self.assertIn("mai_cinephile".encode("utf-8"), res_login.data)

        # 2. Loc bai viet cua nguoi minh follow
        res_followed = self.client.get("/?show=followed")
        self.assertEqual(res_followed.status_code, 200)
        self.assertIn("show_followed=1", res_followed.headers.get("Set-Cookie", ""))

    def test_05_movie_comments_page(self):
        """Kiem tra xem danh sach comment cua phim."""
        with app.app_context():
            m = Movie.query.first()
            res = self.client.get(f"/movies/{m.id}/comments")
            self.assertEqual(res.status_code, 200)
            self.assertIn(m.title.encode("utf-8"), res.data)

    def test_06_register_new_user(self):
        """Dang ky thanh vien moi va dang nhap."""
        res_reg = self.client.post("/register", data={
            "username": "reviewer_newbie",
            "email": "newbie@cineverse.vn",
            "bio": "Mê phim trinh thám",
            "password": "mypassword123",
            "confirm": "mypassword123"
        }, follow_redirects=True)
        self.assertEqual(res_reg.status_code, 200)

        # Kiem tra trong DB
        with app.app_context():
            new_u = User.query.filter_by(username="reviewer_newbie").first()
            self.assertIsNotNone(new_u)
            self.assertEqual(new_u.role.name, "Member")

if __name__ == "__main__":
    unittest.main()
