# CineVerse Form: Dang ky & Dang nhap truyen thong

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    username_or_email = StringField("Tên đăng nhập hoặc Email", validators=[
        DataRequired(message="Vui lòng nhập tên đăng nhập hoặc email.")
    ])
    password = PasswordField("Mật khẩu", validators=[
        DataRequired(message="Vui lòng nhập mật khẩu.")
    ])
    remember_me = BooleanField("Ghi nhớ đăng nhập")
    submit = SubmitField("Đăng nhập")


class RegisterForm(FlaskForm):
    username = StringField("Tên đăng nhập", validators=[
        DataRequired(message="Vui lòng nhập tên đăng nhập."),
        Length(min=3, max=30, message="Tên đăng nhập từ 3 đến 30 ký tự.")
    ])
    email = StringField("Email", validators=[
        DataRequired(message="Vui lòng nhập địa chỉ email."),
        Email(message="Địa chỉ email không hợp lệ.")
    ])
    bio = TextAreaField("Giới thiệu ngắn (sở thích phim ảnh)")
    password = PasswordField("Mật khẩu", validators=[
        DataRequired(message="Vui lòng nhập mật khẩu."),
        Length(min=6, message="Mật khẩu phải từ 6 ký tự trở lên.")
    ])
    confirm = PasswordField("Xác nhận mật khẩu", validators=[
        DataRequired(message="Vui lòng nhập lại mật khẩu."),
        EqualTo("password", message="Mật khẩu xác nhận không khớp.")
    ])
    submit = SubmitField("Đăng ký tài khoản")

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data.strip()).first()
        if user:
            raise ValidationError("Tên đăng nhập này đã được sử dụng. Vui lòng chọn tên khác.")

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data.strip().lower()).first()
        if user:
            raise ValidationError("Email này đã được đăng ký tài khoản.")
