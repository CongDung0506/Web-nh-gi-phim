# CineVerse: Database Seeder
# Tu dong tao database CineVerse_DB tren SQL Server hoac SQLite va nap du lieu mau chu de Dien anh

import os
from models import db, Role, User, Genre, Director, Movie, Follow, MoviePost, MovieComment
from markdown_utils import render_markdown, COMMENT_ALLOWED_TAGS

def seed_data_internal():
    """Ham seed du lieu mau chay thuan qua SQLAlchemy ORM (dung duoc cho ca SQL Server va SQLite)."""
    db.create_all()

    if Role.query.first() is None:
        Role.insert_roles()

    admin_role = Role.query.filter_by(name="Admin").first()
    critic_role = Role.query.filter_by(name="Critic").first()
    member_role = Role.query.filter_by(name="Member").first()

    if User.query.first() is None:
        # 1. Christopher Nolan (Admin & Director)
        nolan = User(
            email="nolan@cineverse.vn",
            username="christopher_nolan",
            bio="Đạo diễn & Nhà làm phim độc lập. Tác giả của Inception, Oppenheimer, The Dark Knight.",
            role=admin_role
        )
        nolan.set_password("pass123")

        # 2. Roger Ebert (Critic - Nha phe binh dien anh)
        ebert = User(
            email="ebert@cineverse.vn",
            username="roger_ebert",
            bio="Nhà phê bình phim kỳ cựu đoạt giải Pulitzer. Yêu thích các tác phẩm nghệ thuật chiều sâu.",
            role=critic_role
        )
        ebert.set_password("pass123")

        # 3. Mai Movie Fan (Member - Khan gia yeu phim)
        mai = User(
            email="mai@cineverse.vn",
            username="mai_cinephile",
            bio="Khán giả đam mê điện ảnh, mê phim tâm lý ly kỳ và phim viễn tưởng khoa học.",
            role=member_role
        )
        mai.set_password("pass123")

        db.session.add_all([nolan, ebert, mai])
        db.session.flush()

        # Follow relations
        db.session.add_all([
            Follow(follower_id=mai.id, followed_id=nolan.id),
            Follow(follower_id=mai.id, followed_id=ebert.id),
            Follow(follower_id=ebert.id, followed_id=nolan.id),
        ])

        # Genres & Directors
        g_scifi = Genre(name="Sci-Fi / Viễn Tưởng", description="Khoa học viễn tưởng, khám phá vũ trụ và công nghệ tương lai.")
        g_drama = Genre(name="Chính Kịch / Tiểu Sử", description="Câu chuyện sâu sắc về tâm lý con người và lịch sử.")
        g_animation = Genre(name="Hoạt Hình / Anime", description="Tác phẩm hoạt họa giàu cảm xúc và nghệ thuật thị giác.")
        db.session.add_all([g_scifi, g_drama, g_animation])
        db.session.flush()

        d_nolan = Director(name="Christopher Nolan", nationality="Anh / Mỹ")
        d_denis = Director(name="Denis Villeneuve", nationality="Canada")
        d_hayao = Director(name="Hayao Miyazaki", nationality="Nhật Bản")
        db.session.add_all([d_nolan, d_denis, d_hayao])
        db.session.flush()

        # Movies
        m1 = Movie(
            title="Oppenheimer",
            release_year=2023,
            duration_minutes=180,
            rating_imdb=8.9,
            summary="Câu chuyện về nhà vật lý lý thuyết J. Robert Oppenheimer và dự án Manhattan tạo ra bom nguyên tử.",
            poster_url="https://images.unsplash.com/photo-1536440136628-849c177e76a1?auto=format&fit=crop&w=400&q=80",
            genre=g_drama
        )
        m1.directors.append(d_nolan)

        m2 = Movie(
            title="Dune: Part Two",
            release_year=2024,
            duration_minutes=166,
            rating_imdb=8.6,
            summary="Paul Atreides hợp lực cùng Chani và người Fremen để trả thù những kẻ đã hủy hoại gia tộc mình.",
            poster_url="https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=400&q=80",
            genre=g_scifi
        )
        m2.directors.append(d_denis)

        m3 = Movie(
            title="Spirited Away (Vùng Đất Linh Hồn)",
            release_year=2001,
            duration_minutes=125,
            rating_imdb=8.6,
            summary="Cô bé Chihiro bước vào thế giới linh hồn kỳ ảo và phải tìm cách giải cứu cha mẹ mình.",
            poster_url="https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=400&q=80",
            genre=g_animation
        )
        m3.directors.append(d_hayao)

        db.session.add_all([m1, m2, m3])
        db.session.flush()

        # CMS Reviews
        p1_md = """## Kiệt tác điện ảnh về trách nhiệm khoa học và lịch sử

*Oppenheimer* không chỉ là một bộ phim tiểu sử thông thường, mà là một trải nghiệm thị giác và âm thanh đỉnh cao về lương tri con người.

### Điểm nhấn nghệ thuật:
- **Diễn xuất xuất thần:** Cillian Murphy đã lột tả hoàn hảo sự giằng xé nội tâm sâu sắc.
- **Âm thanh & Nhạc nền:** Ludwig Göransson tạo nên bản hòa tấu nghẹt thở từ nhịp tim đến tiếng nổ rung chuyển khán phòng.
- **Thực cảnh 100%:** Hiệu ứng nổ Trinity không dùng kỹ xảo CGI đem lại sự chân thực tuyệt đối.

> "Bây giờ tôi trở thành Thần Chết, kẻ hủy diệt thế giới." — J. Robert Oppenheimer

Một tác phẩm xứng đáng 10/10 điểm của điện ảnh thế giới."""

        p2_md = """## Dune: Part Two — Đỉnh cao sử thi viễn tưởng thế hệ mới

Denis Villeneuve đã hiện thực hóa trọn vẹn thế giới cát Arrakis với quy mô hùng vĩ chưa từng thấy.

- Cảnh cưỡi sâu cát Sandworm mang lại cảm giác choáng ngợp tại rạp IMAX.
- Mối quan hệ phức tạp giữa tôn giáo, quyền lực và đức tin được khắc họa chân thật.
- Âm nhạc của Hans Zimmer tiếp tục nâng tầm bộ phim lên chuẩn mực sử thi."""

        post1 = MoviePost(
            title="Giải mã Oppenheimer: Nỗi ám ảnh của Thần Chết và lương tri thời đại",
            movie_title="Oppenheimer",
            score=9.8,
            body_md=p1_md,
            body_html=render_markdown(p1_md),
            author_id=ebert.id
        )

        post2 = MoviePost(
            title="Dune 2: Khi khoa học viễn tưởng đạt tới tầm vóc thần thoại",
            movie_title="Dune: Part Two",
            score=9.4,
            body_md=p2_md,
            body_html=render_markdown(p2_md),
            author_id=ebert.id
        )

        db.session.add_all([post1, post2])
        db.session.flush()

        # Comments
        c1_md = "Phim quá đỉnh! Đoạn thử bom **Trinity** im lặng rồi mới vang tiếng nổ làm mình nổi da gà khắp người."
        c2_md = "Nhạc phim của Ludwig Göransson xứng đáng nhận giải Oscar, nghe rất áp lực và kịch tính!"

        com1 = MovieComment(
            movie_id=m1.id,
            author_id=mai.id,
            body_md=c1_md,
            body_html=render_markdown(c1_md, allowed_tags=COMMENT_ALLOWED_TAGS),
            rating=5
        )
        com2 = MovieComment(
            movie_id=m1.id,
            author_id=ebert.id,
            body_md=c2_md,
            body_html=render_markdown(c2_md, allowed_tags=COMMENT_ALLOWED_TAGS),
            rating=5
        )
        db.session.add_all([com1, com2])
        db.session.commit()
        print("Data seeded successfully!")

def run():
    from app import app
    with app.app_context():
        db.drop_all()
        seed_data_internal()

if __name__ == "__main__":
    run()
