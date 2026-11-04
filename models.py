# CineVerse CMS: Models
# Chu de: Dien anh & Phim anh (CineVerse — Movie Community & Review CMS)

import hashlib
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Permission:
    FOLLOW = 1        # 0b001 - Theo doi nguoi dung khac
    COMMENT = 2       # 0b010 - Binh luan / danh gia phim
    WRITE = 4         # 0b100 - Viet bai review phim (CMS Post)
    MODERATE = 8      # 0b1000 - Kiem duyet review/comment
    ADMIN = 16        # 0b10000 - Quan tri vien he thong


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(50), unique=True, nullable=False)
    permissions = db.Column(db.Integer, default=0)

    users = db.relationship("User", back_populates="role", lazy="select")

    def has_permission(self, perm):
        return (self.permissions & perm) == perm

    @staticmethod
    def insert_roles():
        roles = {
            "Member": Permission.FOLLOW | Permission.COMMENT,
            "Critic": Permission.FOLLOW | Permission.COMMENT | Permission.WRITE,
            "Admin": Permission.FOLLOW | Permission.COMMENT | Permission.WRITE | Permission.MODERATE | Permission.ADMIN,
        }
        for name, perms in roles.items():
            role = Role.query.filter_by(name=name).first()
            if role is None:
                role = Role(name=name)
            role.permissions = perms
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return f"<Role {self.name}>"


# The loai phim
class Genre(db.Model):
    __tablename__ = "genres"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(80), unique=True, nullable=False, index=True)
    description = db.Column(db.Unicode(255), nullable=True)

    movies = db.relationship("Movie", back_populates="genre", lazy="select")

    def __repr__(self):
        return f"<Genre {self.name}>"


# Bang lien ket Dao dien & Phim (Many-to-Many)
movie_directors = db.Table(
    "movie_directors",
    db.Column("movie_id", db.Integer, db.ForeignKey("movies.id"), primary_key=True),
    db.Column("director_id", db.Integer, db.ForeignKey("directors.id"), primary_key=True),
)


class Director(db.Model):
    __tablename__ = "directors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(120), nullable=False, index=True)
    nationality = db.Column(db.Unicode(80), nullable=True)

    movies = db.relationship("Movie", secondary=movie_directors, back_populates="directors")

    def __repr__(self):
        return f"<Director {self.name}>"


# Phim (Movie)
class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(200), nullable=False, index=True)
    release_year = db.Column(db.Integer, nullable=False, default=2024)
    duration_minutes = db.Column(db.Integer, nullable=False, default=120)
    rating_imdb = db.Column(db.Float, nullable=False, default=8.0)
    summary = db.Column(db.UnicodeText, nullable=True)
    poster_url = db.Column(db.Unicode(500), nullable=True)

    genre_id = db.Column(db.Integer, db.ForeignKey("genres.id"), nullable=False)
    genre = db.relationship("Genre", back_populates="movies")

    directors = db.relationship("Director", secondary=movie_directors, back_populates="movies")
    comments = db.relationship("MovieComment", back_populates="movie", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Movie {self.title} ({self.release_year})>"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Unicode(120), unique=True, nullable=False, index=True)
    username = db.Column(db.Unicode(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.Unicode(255), nullable=False)
    bio = db.Column(db.Unicode(255), nullable=True)
    is_verified = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    role = db.relationship("Role", back_populates="users")

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_admin(self):
        return self.can(Permission.ADMIN)

    def gravatar_url(self, size=80):
        # Gravatar: hash MD5 tu email de tranh tiet lo thong tin ca nhan (privacy-first)
        email_hash = hashlib.md5(self.email.strip().lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s={size}"

    # Quan he Follow (self-referential many-to-many)
    def follow(self, user):
        if not self.is_following(user) and user.id != self.id:
            db.session.add(Follow(follower_id=self.id, followed_id=user.id))

    def unfollow(self, user):
        f = Follow.query.filter_by(follower_id=self.id, followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return Follow.query.filter_by(follower_id=self.id, followed_id=user.id).first() is not None

    @property
    def followed_posts(self):
        # JOIN Follow + MoviePost: lay bai viet review cua nhung nguoi minh follow
        return (MoviePost.query
                .join(Follow, Follow.followed_id == MoviePost.author_id)
                .filter(Follow.follower_id == self.id)
                .order_by(MoviePost.created_at.desc()))

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self):
        return f"<User {self.username}>"


class Follow(db.Model):
    """Bang lien ket self-referential many-to-many tren User (A follow B)."""
    __tablename__ = "follows"

    follower_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MoviePost(db.Model):
    """CMS: Bai viet chuyen sau / Review phim cua doi ngu CineVerse — ho tro Markdown + phan trang."""
    __tablename__ = "movie_posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(200), nullable=False)
    movie_title = db.Column(db.Unicode(150), nullable=True)     # Ten phim duoc review
    score = db.Column(db.Float, nullable=False, default=9.0)     # Diem danh gia (1-10)
    body_md = db.Column(db.UnicodeText, nullable=False)          # Markdown goc
    body_html = db.Column(db.UnicodeText, nullable=False)        # HTML sau khi sanitize chong XSS
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    author = db.relationship("User", foreign_keys=[author_id])

    def __repr__(self):
        return f"<MoviePost {self.title}>"


class MovieComment(db.Model):
    """Binh luan / Phan hoi gan voi 1 bo phim — Markdown gioi han + sanitize chong XSS."""
    __tablename__ = "movie_comments"

    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    body_md = db.Column(db.UnicodeText, nullable=False)
    body_html = db.Column(db.UnicodeText, nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=5)   # So sao (1-5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    movie = db.relationship("Movie", back_populates="comments")
    author = db.relationship("User", foreign_keys=[author_id])

    def __repr__(self):
        return f"<MovieComment on Movie#{self.movie_id} by User#{self.author_id}>"
