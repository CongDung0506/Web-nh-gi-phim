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

    # 1. Khoi tao nguoi dung mau
    nolan = User.query.filter_by(username="christopher_nolan").first()
    if nolan is None:
        nolan = User(
            email="nolan@cineverse.vn",
            username="christopher_nolan",
            bio="Đạo diễn & Nhà làm phim độc lập. Tác giả của Inception, Oppenheimer, The Dark Knight.",
            role=admin_role
        )
        nolan.set_password("pass123")
        db.session.add(nolan)

    ebert = User.query.filter_by(username="roger_ebert").first()
    if ebert is None:
        ebert = User(
            email="ebert@cineverse.vn",
            username="roger_ebert",
            bio="Nhà phê bình phim kỳ cựu đoạt giải Pulitzer. Yêu thích các tác phẩm nghệ thuật có chiều sâu.",
            role=critic_role
        )
        ebert.set_password("pass123")
        db.session.add(ebert)

    mai = User.query.filter_by(username="mai_cinephile").first()
    if mai is None:
        mai = User(
            email="mai@cineverse.vn",
            username="mai_cinephile",
            bio="Khán giả đam mê điện ảnh, mê phim tình cảm lãng mạn, kinh dị bí ẩn và viễn tưởng.",
            role=member_role
        )
        mai.set_password("pass123")
        db.session.add(mai)

    db.session.flush()

    # Quan he Follow
    if Follow.query.first() is None:
        db.session.add_all([
            Follow(follower_id=mai.id, followed_id=nolan.id),
            Follow(follower_id=mai.id, followed_id=ebert.id),
            Follow(follower_id=ebert.id, followed_id=nolan.id),
        ])
        db.session.flush()

    # 2. Danh muc The loai phim phong phu (Genres)
    genres_def = [
        ("Tình Cảm / Lãng Mạn", "Những câu chuyện tình yêu say đắm, xúc cảm thăng hoa và rung động trái tim."),
        ("Kinh Dị / Bí Ẩn", "Cảm giác rùng rợn nghẹt thở, những lời nguyền tâm linh và bí ẩn ám ảnh."),
        ("Sci-Fi / Viễn Tưởng", "Khoa học viễn tưởng, du hành vũ trụ, công nghệ tương lai và đa vũ trụ."),
        ("Hành Động / Phiêu Lưu", "Những pha rượt đuổi kịch tính, giao đấu mãn nhãn và tinh thần quả cảm."),
        ("Hoạt Hình / Anime", "Kỳ quan hoạt họa đột phá thị giác, giàu cảm xúc và nghệ thuật đỉnh cao."),
        ("Chính Kịch / Tâm Lý", "Chiếu rọi vào chiều sâu tâm lý con người, số phận và hiện thực xã hội."),
    ]

    genres_map = {}
    for name, desc in genres_def:
        g = Genre.query.filter_by(name=name).first()
        if g is None:
            g = Genre(name=name, description=desc)
            db.session.add(g)
            db.session.flush()
        genres_map[name] = g

    # 3. Dao dien hang dau the gioi (Directors)
    directors_def = [
        ("Christopher Nolan", "Anh / Mỹ"),
        ("Denis Villeneuve", "Canada"),
        ("James Cameron", "Canada"),
        ("Hayao Miyazaki", "Nhật Bản"),
        ("Makoto Shinkai", "Nhật Bản"),
        ("Bong Joon-ho", "Hàn Quốc"),
        ("James Wan", "Úc / Malaysia"),
        ("Jang Jae-hyun", "Hàn Quốc"),
        ("Ari Aster", "Mỹ"),
        ("John Krasinski", "Mỹ"),
        ("Damien Chazelle", "Mỹ"),
        ("Celine Song", "Canada / Hàn Quốc"),
        ("Richard Curtis", "Anh"),
        ("Chad Stahelski", "Mỹ"),
        ("Frank Darabont", "Mỹ"),
    ]

    directors_map = {}
    for name, nat in directors_def:
        d = Director.query.filter_by(name=name).first()
        if d is None:
            d = Director(name=name, nationality=nat)
            db.session.add(d)
            db.session.flush()
        directors_map[name] = d

    # 4. Kho 20 Phim voi Poster chinh thuc 100% tu TMDB CDN (Chuan dien anh the gioi)
    movies_data = [
        # --- THE LOAI: TINH CAM / LANG MAN ---
        {
            "title": "Titanic",
            "release_year": 1997,
            "duration_minutes": 194,
            "rating_imdb": 7.9,
            "summary": "Bản tình ca bất hủ vượt giai cấp giữa chàng họa sĩ nghèo Jack Dawson và tiểu thư Rose DeWitt Bukater trên chuyến tàu định mệnh chấn động thế giới.",
            "poster_url": "https://image.tmdb.org/t/p/w500/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg",
            "genre": genres_map["Tình Cảm / Lãng Mạn"],
            "directors": [directors_map["James Cameron"]]
        },
        {
            "title": "La La Land (Những Kẻ Khờ Mộng Mơ)",
            "release_year": 2016,
            "duration_minutes": 128,
            "rating_imdb": 8.0,
            "summary": "Một nghệ sĩ dương cầm jazz đầy hoài bão và một nữ diễn viên trẻ đem lòng yêu nhau tại thành phố Los Angeles hoa lệ, nơi họ phải chọn lựa giữa tình yêu và ước mơ nghệ thuật.",
            "poster_url": "https://image.tmdb.org/t/p/w500/uDO8zWDhfWwoFdKS4fzkUJt0Rf0.jpg",
            "genre": genres_map["Tình Cảm / Lãng Mạn"],
            "directors": [directors_map["Damien Chazelle"]]
        },
        {
            "title": "Past Lives (Muôn Kiếp Nhân Duyên)",
            "release_year": 2023,
            "duration_minutes": 106,
            "rating_imdb": 7.9,
            "summary": "Nora và Hae Sung - hai người bạn thời thơ ấu tại Hàn Quốc - hội ngộ tại New York sau hai thập kỷ xa cách, đối diện với khái niệm 'In-Yun' (nhân duyên tiền kiếp) và sự trớ trêu của thời gian.",
            "poster_url": "https://image.tmdb.org/t/p/w500/k3waqVXSnvCZWfJYNtdamTgTtTA.jpg",
            "genre": genres_map["Tình Cảm / Lãng Mạn"],
            "directors": [directors_map["Celine Song"]]
        },
        {
            "title": "About Time (Đã Đến Lúc)",
            "release_year": 2013,
            "duration_minutes": 123,
            "rating_imdb": 7.8,
            "summary": "Tim Lake phát hiện khả năng du hành thời gian của gia đình và dùng nó để tìm kiếm tình yêu đích thực của đời mình, nhận ra bài học sâu sắc về việc trân trọng từng phút giây hiện tại.",
            "poster_url": "https://image.tmdb.org/t/p/w500/ls6zswrOZVhCXQBh96DlbnLBajM.jpg",
            "genre": genres_map["Tình Cảm / Lãng Mạn"],
            "directors": [directors_map["Richard Curtis"]]
        },

        # --- THE LOAI: KINH DI / BI AN ---
        {
            "title": "The Conjuring (Ám Ảnh Kinh Hoàng)",
            "release_year": 2013,
            "duration_minutes": 112,
            "rating_imdb": 7.5,
            "summary": "Cặp vợ chồng nhà trừ tà ngoại cảm Ed và Lorraine Warren tới điều tra ngôi nhà trang trại hẻo lánh của gia đình Perron tại Rhode Island, nơi bị một thực thể tà ác hắc ám ngự trị.",
            "poster_url": "https://image.tmdb.org/t/p/w500/wVYREutTvI2tmxr6ujrHT704wGF.jpg",
            "genre": genres_map["Kinh Dị / Bí Ẩn"],
            "directors": [directors_map["James Wan"]]
        },
        {
            "title": "Exhuma (Quật Mộ Trùng Ma)",
            "release_year": 2024,
            "duration_minutes": 134,
            "rating_imdb": 7.1,
            "summary": "Một nhóm gồm hai pháp sư trẻ, một thầy phong thủy và chuyên gia mai táng nhận lời khai quật ngôi mộ tổ bí ẩn của một gia tộc giàu có, vô tình giải phóng ác linh kinh hoàng chôn sâu dưới lòng đất.",
            "poster_url": "https://image.tmdb.org/t/p/w500/pPElE8npavUirQWmscJUGZyPiP6.jpg",
            "genre": genres_map["Kinh Dị / Bí Ẩn"],
            "directors": [directors_map["Jang Jae-hyun"]]
        },
        {
            "title": "A Quiet Place (Vùng Đất Câm Lặng)",
            "release_year": 2018,
            "duration_minutes": 90,
            "rating_imdb": 7.5,
            "summary": "Trong một thế giới hậu tận thế bị xâm lăng bởi loài quái vật mù săn mồi bằng thính giác siêu nhạy, một gia đình phải sống trong sự im lặng tuyệt đối để giữ mạng sống cho con cái.",
            "poster_url": "https://image.tmdb.org/t/p/w500/nAU74GmpUk7t5iklEp3bufwDq4n.jpg",
            "genre": genres_map["Kinh Dị / Bí Ẩn"],
            "directors": [directors_map["John Krasinski"]]
        },
        {
            "title": "Hereditary (Dòng Máu Quỷ Dữ)",
            "release_year": 2018,
            "duration_minutes": 127,
            "rating_imdb": 7.3,
            "summary": "Sau cái chết của người bà bí ẩn, gia đình Graham bắt đầu khám phá ra những bí mật đen tối rùng rợn được truyền qua nhiều thế hệ gắn liền với giáo phái tôn thờ quỷ Paimon.",
            "poster_url": "https://image.tmdb.org/t/p/w500/wq3vuQzQgbS83zX3malAFWMsSwX.jpg",
            "genre": genres_map["Kinh Dị / Bí Ẩn"],
            "directors": [directors_map["Ari Aster"]]
        },

        # --- THE LOAI: SCI-FI / VIEN TUONG ---
        {
            "title": "Interstellar (Hố Đen Tử Thần)",
            "release_year": 2014,
            "duration_minutes": 169,
            "rating_imdb": 8.7,
            "summary": "Một nhóm nhà khoa học và phi hành gia du hành qua lỗ sâu gần sao Thổ để tìm kiếm hành tinh sống mới, khám phá các chiều không gian và sức mạnh của tình yêu thương.",
            "poster_url": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
            "genre": genres_map["Sci-Fi / Viễn Tưởng"],
            "directors": [directors_map["Christopher Nolan"]]
        },
        {
            "title": "Dune: Part Two (Hành Tinh Cát 2)",
            "release_year": 2024,
            "duration_minutes": 166,
            "rating_imdb": 8.6,
            "summary": "Paul Atreides hợp lực cùng Chani và tộc người Fremen trên sa mạc cằn cỗi Arrakis, dấn thân vào cuộc thánh chiến báo thù những kẻ đã tàn sát gia tộc mình.",
            "poster_url": "https://image.tmdb.org/t/p/w500/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg",
            "genre": genres_map["Sci-Fi / Viễn Tưởng"],
            "directors": [directors_map["Denis Villeneuve"]]
        },
        {
            "title": "Avatar: The Way of Water",
            "release_year": 2022,
            "duration_minutes": 192,
            "rating_imdb": 7.6,
            "summary": "Jake Sully và Neytiri đưa gia đình rời khỏi khu rừng để nương náu tại bộ tộc biển Metkayina, bảo vệ kỳ quan sinh thái Pandora trước cuộc xâm lăng của loài người.",
            "poster_url": "https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg",
            "genre": genres_map["Sci-Fi / Viễn Tưởng"],
            "directors": [directors_map["James Cameron"]]
        },

        # --- THE LOAI: HANH DONG / PHIEU LUU ---
        {
            "title": "The Dark Knight (Kỵ Sĩ Bóng Đêm)",
            "release_year": 2008,
            "duration_minutes": 152,
            "rating_imdb": 9.0,
            "summary": "Khi tên tội phạm điên loạn Joker gieo rắc hỗn loạn khắp Gotham, Batman phải đứng lên bảo vệ công lý và đương đầu với phép thử tàn khốc về đạo đức và nhân tính.",
            "poster_url": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
            "genre": genres_map["Hành Động / Phiêu Lưu"],
            "directors": [directors_map["Christopher Nolan"]]
        },
        {
            "title": "John Wick: Chapter 4",
            "release_year": 2023,
            "duration_minutes": 169,
            "rating_imdb": 7.7,
            "summary": "Sát thủ huyền thoại John Wick tìm con đường đánh bại Hội Đồng Tối Cao High Table, trải qua những cuộc thư hùng nảy lửa từ sa mạc Morocco, Osaka đến bảo tàng Louvre và Khải Hoàn Môn Paris.",
            "poster_url": "https://image.tmdb.org/t/p/w500/vZloFAK7NmvMGKE7VkF5UHaz0I.jpg",
            "genre": genres_map["Hành Động / Phiêu Lưu"],
            "directors": [directors_map["Chad Stahelski"]]
        },
        {
            "title": "Inception (Kẻ Đánh Cắp Giấc Mơ)",
            "release_year": 2010,
            "duration_minutes": 148,
            "rating_imdb": 8.8,
            "summary": "Một đạo chích chuyên thâm nhập tiềm thức nhận phi vụ đảo ngược: cấy ghép một ý tưởng vào sâu trong giấc mơ của người thừa kế tập đoàn quyền lực nhất.",
            "poster_url": "https://image.tmdb.org/t/p/w500/edv5CZvWj09upOsy2Y6IwDhK8bt.jpg",
            "genre": genres_map["Hành Động / Phiêu Lưu"],
            "directors": [directors_map["Christopher Nolan"]]
        },

        # --- THE LOAI: HOAT HINH / ANIME ---
        {
            "title": "Spirited Away (Vùng Đất Linh Hồn)",
            "release_year": 2001,
            "duration_minutes": 125,
            "rating_imdb": 8.6,
            "summary": "Cô bé Chihiro 10 tuổi vô tình bước vào thế giới thần bí của các linh hồn, nơi cha mẹ bị biến thành heo và cô phải làm việc tại nhà tắm công cộng của mụ phù thủy Yubaba.",
            "poster_url": "https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg",
            "genre": genres_map["Hoạt Hình / Anime"],
            "directors": [directors_map["Hayao Miyazaki"]]
        },
        {
            "title": "Your Name (Kimi no Na wa)",
            "release_year": 2016,
            "duration_minutes": 106,
            "rating_imdb": 8.4,
            "summary": "Mitsuha - nữ sinh vùng quê hẻo lánh và Taki - nam sinh trung học tại Tokyo hoa lệ hoán đổi thân xác cho nhau qua những giấc mơ, chạy đua với thiên tai để cứu lấy nhau.",
            "poster_url": "https://image.tmdb.org/t/p/w500/q719jXXEzOoYaps6babgKnONONX.jpg",
            "genre": genres_map["Hoạt Hình / Anime"],
            "directors": [directors_map["Makoto Shinkai"]]
        },
        {
            "title": "Spider-Man: Across the Spider-Verse",
            "release_year": 2023,
            "duration_minutes": 140,
            "rating_imdb": 8.7,
            "summary": "Miles Morales du hành qua đa vũ trụ nhện, đối đầu với Spider-Society do Miguel O'Hara dẫn đầu để định nghĩa lại ý nghĩa thực sự của việc làm một người anh hùng.",
            "poster_url": "https://image.tmdb.org/t/p/w500/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg",
            "genre": genres_map["Hoạt Hình / Anime"],
            "directors": [directors_map["Christopher Nolan"]]
        },

        # --- THE LOAI: CHINH KICH / TAM LY ---
        {
            "title": "Oppenheimer",
            "release_year": 2023,
            "duration_minutes": 180,
            "rating_imdb": 8.9,
            "summary": "Bộ phim đoạt 7 giải Oscar thuật lại cuộc đời đầy giằng xé của nhà vật lý lý thuyết J. Robert Oppenheimer - người đứng đầu Dự án Manhattan tạo ra bom nguyên tử.",
            "poster_url": "https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
            "genre": genres_map["Chính Kịch / Tâm Lý"],
            "directors": [directors_map["Christopher Nolan"]]
        },
        {
            "title": "Parasite (Ký Sinh Trùng)",
            "release_year": 2019,
            "duration_minutes": 132,
            "rating_imdb": 8.5,
            "summary": "Gia đình họ Kim thất nghiệp lập mưu trà trộn vào làm việc cho gia đình tài phiệt họ Park, mở ra một chuỗi bi kịch nghẹt thở và châm biếm sâu cay về phân hóa xã hội.",
            "poster_url": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
            "genre": genres_map["Chính Kịch / Tâm Lý"],
            "directors": [directors_map["Bong Joon-ho"]]
        },
        {
            "title": "The Shawshank Redemption (Nhà Tù Shawshank)",
            "release_year": 1994,
            "duration_minutes": 142,
            "rating_imdb": 9.3,
            "summary": "Andy Dufresne bị kết án tù chung thân oan uổng tại nhà tù khắc nghiệt Shawshank. Suốt 19 năm kiên trì và hy vọng, anh đã thực hiện cuộc vượt ngục kỳ tích nhất lịch sử điện ảnh.",
            "poster_url": "https://image.tmdb.org/t/p/w500/lyQBXzOQSuE59IsHyhrp0qIiPAz.jpg",
            "genre": genres_map["Chính Kịch / Tâm Lý"],
            "directors": [directors_map["Frank Darabont"]]
        }
    ]

    saved_movies = []
    for m_data in movies_data:
        m = Movie.query.filter_by(title=m_data["title"]).first()
        if m is None:
            m = Movie(
                title=m_data["title"],
                release_year=m_data["release_year"],
                duration_minutes=m_data["duration_minutes"],
                rating_imdb=m_data["rating_imdb"],
                summary=m_data["summary"],
                poster_url=m_data["poster_url"],
                genre=m_data["genre"]
            )
            for d in m_data["directors"]:
                if d not in m.directors:
                    m.directors.append(d)
            db.session.add(m)
        else:
            m.release_year = m_data["release_year"]
            m.duration_minutes = m_data["duration_minutes"]
            m.rating_imdb = m_data["rating_imdb"]
            m.summary = m_data["summary"]
            m.poster_url = m_data["poster_url"]
            m.genre = m_data["genre"]
            for d in m_data["directors"]:
                if d not in m.directors:
                    m.directors.append(d)
        saved_movies.append(m)

    db.session.flush()

    # 5. CMS Reviews (Bai viet chuyen sau cua Nha phe binh)
    if MoviePost.query.first() is None:
        p1_md = """## Kiệt tác điện ảnh về trách nhiệm khoa học và lương tri lịch sử

*Oppenheimer* không chỉ là một bộ phim tiểu sử thông thường, mà là một trải nghiệm thị giác và âm thanh đỉnh cao về lương tri con người trước ngưỡng cửa hủy diệt.

### Điểm nhấn nghệ thuật:
- **Diễn xuất xuất thần:** Cillian Murphy đã lột tả hoàn hảo sự giằng xé nội tâm sâu sắc của 'Cha đẻ bom nguyên tử'.
- **Âm thanh & Nhạc nền:** Ludwig Göransson tạo nên bản hòa tấu nghẹt thở từ tiếng đập chân rung chuyển đến sự im lặng kinh hoàng của khoảnh khắc nổ Trinity.
- **Thực cảnh 100%:** Christopher Nolan kiên quyết không dùng kỹ xảo CGI đem lại sự chân thực tuyệt đối.

> "Bây giờ tôi trở thành Thần Chết, kẻ hủy diệt thế giới." — J. Robert Oppenheimer

Một tác phẩm xứng đáng 10/10 điểm của điện ảnh đương đại."""

        p2_md = """## Dune: Part Two — Đỉnh cao sử thi viễn tưởng của thế kỷ 21

Denis Villeneuve đã hiện thực hóa trọn vẹn thế giới sa mạc Arrakis với quy mô hùng vĩ và triết lý tôn giáo - chính trị sâu sắc.

- Cảnh cưỡi sâu cát khổng lồ Sandworm mang lại cảm giác choáng ngợp tột cùng tại rạp IMAX.
- Mối quan hệ phức tạp giữa Paul Atreides và Chani được khắc họa bi tráng giữa vòng xoáy số phận.
- Âm nhạc của Hans Zimmer tiếp tục nâng tầm bộ phim lên chuẩn mực sử thi bất hủ."""

        p3_md = """## Tái khám phá Inception: Nghệ thuật đan cài đa tầng giấc mơ

14 năm sau ngày ra mắt, cấu trúc giấc mơ trong giấc mơ của *Inception* vẫn là một trong những kịch bản nguyên bản thông minh và chặt chẽ nhất từng được Hollywood sản xuất.

Cảnh hành lang xoay không trọng lực của Joseph Gordon-Levitt vẫn là tượng đài kỹ xảo thực tế cho tới tận ngày nay."""

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

        post3 = MoviePost(
            title="Góc nhìn đạo diễn: Khai phá giấc mơ và cấu trúc thời gian trong Inception",
            movie_title="Inception & Interstellar",
            score=9.6,
            body_md=p3_md,
            body_html=render_markdown(p3_md),
            author_id=nolan.id
        )

        db.session.add_all([post1, post2, post3])
        db.session.flush()

    # 6. Binh luan mau (Movie Comments)
    if MovieComment.query.first() is None:
        c1_md = "Phim quá đỉnh! Đoạn thử bom **Trinity** im lặng tuyệt đối rồi mới vang tiếng nổ làm cả rạp nín thở."
        c2_md = "Nhạc phim của Ludwig Göransson xứng đáng 10 điểm không có nhưng, dồn dập và nghẹt thở!"
        c3_md = "Hình ảnh sa mạc cát trong Dune 2 đẹp đến ngỡ ngàng, xem rạp IMAX đúng là trải nghiệm nhớ đời."

        oppenheimer = Movie.query.filter_by(title="Oppenheimer").first()
        dune = Movie.query.filter_by(title="Dune: Part Two (Hành Tinh Cát 2)").first()

        if oppenheimer:
            db.session.add(MovieComment(
                movie_id=oppenheimer.id,
                author_id=mai.id,
                body_md=c1_md,
                body_html=render_markdown(c1_md, allowed_tags=COMMENT_ALLOWED_TAGS),
                rating=5
            ))
            db.session.add(MovieComment(
                movie_id=oppenheimer.id,
                author_id=ebert.id,
                body_md=c2_md,
                body_html=render_markdown(c2_md, allowed_tags=COMMENT_ALLOWED_TAGS),
                rating=5
            ))
        if dune:
            db.session.add(MovieComment(
                movie_id=dune.id,
                author_id=mai.id,
                body_md=c3_md,
                body_html=render_markdown(c3_md, allowed_tags=COMMENT_ALLOWED_TAGS),
                rating=5
            ))

    db.session.commit()
    print(f"Data seeded successfully! Total movies in database: {Movie.query.count()}, Genres: {Genre.query.count()}")

def run():
    from app import app
    with app.app_context():
        seed_data_internal()

if __name__ == "__main__":
    run()
