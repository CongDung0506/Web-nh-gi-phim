# CineVerse CMS: Main Application
# Chu de: Dien anh & Phim anh (Movie Review & Cinema Community CMS)

import os
import tempfile
import urllib.parse
from flask import Flask, render_template, redirect, url_for, request, flash, make_response, abort
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_required, current_user, login_user, logout_user

from models import db, User, Role, Movie, Genre, Director, Follow, MoviePost, MovieComment, Permission
from markdown_utils import render_markdown, COMMENT_ALLOWED_TAGS
from decorators import admin_required, critic_or_admin_required
from forms import LoginForm, RegisterForm

app = Flask(__name__)
Bootstrap(app)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "cineverse-secret-key-pwd301-2026")

# Database configuration linh hoat cho ca Localhost va Cloud (Vercel / Render)
if os.environ.get("VERCEL"):
    # Vercel serverless Lambda su dung thu muc ghi /tmp
    db_path = os.path.join(tempfile.gettempdir(), "cineverse.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
elif os.environ.get("DATABASE_URL"):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
else:
    # Localhost: Thu ket noi SQL Server, neu khong duoc se dung SQLite cuc bo
    try:
        import pyodbc
        DB_SERVER = os.environ.get("DB_SERVER", ".")
        DB_NAME = os.environ.get("DB_NAME", "CineVerse_DB")
        DB_DRIVER = os.environ.get("DB_DRIVER", "ODBC Driver 17 for SQL Server")

        params = urllib.parse.quote_plus(
            f"DRIVER={{{DB_DRIVER}}};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_NAME};"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
        app.config["SQLALCHEMY_DATABASE_URI"] = f"mssql+pyodbc:///?odbc_connect={params}"
    except Exception:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cineverse.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = "Vui lòng đăng nhập để thực hiện thao tác này."
login_manager.login_message_category = "info"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# Tu dong tao bang va nap du lieu mau neu database rong (Dac biet tren Vercel)
@app.before_request
def auto_init_database():
    if not getattr(app, "_db_initialized", False):
        try:
            db.create_all()
            if User.query.first() is None or Movie.query.count() < 15:
                from seed_cinema import seed_data_internal
                seed_data_internal()
            app._db_initialized = True
        except Exception as e:
            print(f"Notice DB init: {e}")


# --- Dang ky & Dang nhap truyen thong ---------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        ident = form.username_or_email.data.strip()
        user = User.query.filter(
            (User.username == ident) | (User.email == ident.lower())
        ).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(f"Chào mừng bạn trở lại, {user.username}!")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("home"))
        else:
            flash("Tên đăng nhập hoặc mật khẩu không chính xác.")
    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegisterForm()
    if form.validate_on_submit():
        member_role = Role.query.filter_by(name="Member").first()
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            bio=form.bio.data.strip() if form.bio.data else None,
            role=member_role
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Đăng ký tài khoản thành công! Bạn có thể đăng nhập ngay bây giờ.")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Bạn đã đăng xuất an toàn.")
    return redirect(url_for("home"))


# --- Trang chu ca nhan hoa (Cookies: show_followed) -------------------------
@app.route("/")
def home():
    """Trang chu ca nhan hoa: dung cookie 'show_followed' de quyet dinh hien thi bai review nao."""
    show_param = request.args.get("show")
    if show_param in ("followed", "all"):
        show_followed = (show_param == "followed")
    else:
        show_followed = request.cookies.get("show_followed", "0") == "1"

    if current_user.is_authenticated and show_followed:
        posts = current_user.followed_posts.all()
    else:
        posts = MoviePost.query.order_by(MoviePost.created_at.desc()).all()

    featured_movies = Movie.query.order_by(Movie.rating_imdb.desc()).limit(4).all()

    resp = make_response(render_template(
        "home.html",
        posts=posts,
        show_followed=show_followed,
        featured_movies=featured_movies
    ))

    if show_param in ("followed", "all"):
        resp.set_cookie("show_followed", "1" if show_followed else "0", max_age=30 * 24 * 3600)
    return resp


# --- User Profile & Follow System -------------------------------------------
@app.route("/users/<username>")
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    is_following = current_user.is_authenticated and current_user.is_following(user)
    followers_count = Follow.query.filter_by(followed_id=user.id).count()
    following_count = Follow.query.filter_by(follower_id=user.id).count()
    user_posts = MoviePost.query.filter_by(author_id=user.id).order_by(MoviePost.created_at.desc()).all()
    return render_template(
        "profile.html",
        user=user,
        is_following=is_following,
        followers_count=followers_count,
        following_count=following_count,
        posts=user_posts
    )


@app.route("/users/<username>/follow", methods=["POST"])
@login_required
def toggle_follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    next_url = request.args.get("next") or request.referrer or url_for("profile", username=username)
    if user.id == current_user.id:
        flash("Bạn không thể tự theo dõi chính mình.")
        return redirect(next_url)
    if current_user.is_following(user):
        current_user.unfollow(user)
        flash(f"Đã bỏ theo dõi: {username}.")
    else:
        current_user.follow(user)
        flash(f"Đã theo dõi: {username}.")
    db.session.commit()
    return redirect(next_url)


# --- Movie CMS (Blog / Review chuyen sau) ------------------------------------
@app.route("/reviews")
def review_list():
    page = request.args.get("page", 1, type=int)
    posts = MoviePost.query.order_by(MoviePost.created_at.desc()).paginate(page=page, per_page=3, error_out=False)
    return render_template("review_list.html", posts=posts)


@app.route("/reviews/<int:post_id>")
def review_detail(post_id):
    post = MoviePost.query.get_or_404(post_id)
    return render_template("review_detail.html", post=post)


@app.route("/reviews/new", methods=["GET", "POST"])
@login_required
@critic_or_admin_required
def review_new():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        movie_title = request.form.get("movie_title", "").strip()
        score_val = float(request.form.get("score", 9.0))
        body_md = request.form.get("body_md", "").strip()

        if not title or not body_md:
            flash("Vui lòng nhập đầy đủ tiêu đề và nội dung bài viết.")
            return redirect(url_for("review_new"))

        body_html = render_markdown(body_md)
        post = MoviePost(
            title=title,
            movie_title=movie_title,
            score=score_val,
            body_md=body_md,
            body_html=body_html,
            author_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        flash("Đã xuất bản bài đánh giá phim mới thành công!")
        return redirect(url_for("review_detail", post_id=post.id))

    movies = Movie.query.all()
    return render_template("review_new.html", movies=movies)


# --- Movies & Comments (Markdown gioi han + Sanitize) ------------------------
@app.route("/movies")
def movie_list():
    genre_id = request.args.get("genre", type=int)
    search_q = request.args.get("q", "").strip()

    query = Movie.query
    if genre_id:
        query = query.filter_by(genre_id=genre_id)
    if search_q:
        query = query.filter(Movie.title.ilike(f"%{search_q}%"))

    movies = query.order_by(Movie.rating_imdb.desc(), Movie.release_year.desc()).all()
    genres = Genre.query.order_by(Genre.id).all()
    return render_template(
        "movie_list.html",
        movies=movies,
        genres=genres,
        active_genre=genre_id,
        search_q=search_q
    )


@app.route("/movies/<int:movie_id>/comments")
def movie_comments(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    comments = MovieComment.query.filter_by(movie_id=movie_id).order_by(MovieComment.created_at.desc()).all()
    return render_template("movie_comments.html", movie=movie, comments=comments)


@app.route("/movies/<int:movie_id>/comments", methods=["POST"])
@login_required
def add_comment(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    body_md = request.form.get("body_md", "").strip()
    rating = int(request.form.get("rating", 5))

    if not body_md:
        flash("Nội dung đánh giá không được để trống.")
        return redirect(url_for("movie_comments", movie_id=movie_id))

    body_html = render_markdown(body_md, allowed_tags=COMMENT_ALLOWED_TAGS)
    comment = MovieComment(
        movie_id=movie_id,
        author_id=current_user.id,
        body_md=body_md,
        body_html=body_html,
        rating=rating
    )
    db.session.add(comment)
    db.session.commit()
    flash("Cảm ơn bạn đã gửi cảm nhận về bộ phim!")
    return redirect(url_for("movie_comments", movie_id=movie_id))


# --- AI Log (Copilot / Assistant Log demo) -----------------------------------
@app.route("/ai-log")
def ai_log():
    import markdown
    path = os.path.join(os.path.dirname(__file__), "ai_demo", "copilot_log.md")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            html = markdown.markdown(f.read(), extensions=["fenced_code"])
    else:
        html = "<p>Chưa có file nhật ký AI.</p>"
    return render_template("ai_log.html", content=html)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
