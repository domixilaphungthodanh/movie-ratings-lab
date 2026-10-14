import sqlite3
from .db import DEFAULT_DB, connect, text, day

def add_movie(title, year, genres, db=DEFAULT_DB):
    title = text(title, 'Tên phim')
    if type(year) is not int or not 1888 <= year <= 2100:
        raise ValueError('Năm phát hành phải là số nguyên từ 1888 đến 2100.')
    genres = list(dict.fromkeys(text(g, 'Thể loại').casefold() for g in genres))
    if not genres:
        raise ValueError('Phim cần ít nhất một thể loại.')
    with connect(db) as conn, conn:
        movie_id = conn.execute('INSERT INTO movies(title,release_year) VALUES (?,?)', (title,year)).lastrowid
        for genre in genres:
            conn.execute('INSERT INTO genres(name) VALUES (?) ON CONFLICT(name) DO NOTHING', (genre,))
            genre_id = conn.execute('SELECT genre_id FROM genres WHERE name=?', (genre,)).fetchone()[0]
            conn.execute('INSERT INTO movie_genres VALUES (?,?)', (movie_id,genre_id))
        return movie_id

def add_viewer(name, db=DEFAULT_DB):
    with connect(db) as conn, conn:
        return conn.execute('INSERT INTO viewers(name) VALUES (?)', (text(name,'Tên người xem'),)).lastrowid

def rate_movie(movie_id, viewer_id, score, review='', rated_on=None, db=DEFAULT_DB, update=False):
    if type(score) is not int or not 1 <= score <= 10:
        raise ValueError('Điểm phải là số nguyên từ 1 đến 10.')
    date_value = day(rated_on)
    with connect(db) as conn:
        conn.execute('BEGIN IMMEDIATE')
        with conn:
            if not conn.execute('SELECT 1 FROM movies WHERE movie_id=?',(movie_id,)).fetchone():
                raise ValueError('Phim không tồn tại.')
            if not conn.execute('SELECT 1 FROM viewers WHERE viewer_id=?',(viewer_id,)).fetchone():
                raise ValueError('Người xem không tồn tại.')
            existing = conn.execute('SELECT rating_id FROM ratings WHERE movie_id=? AND viewer_id=?',(movie_id,viewer_id)).fetchone()
            if update:
                if existing is None:
                    raise ValueError('Chưa có đánh giá để sửa. Dùng chức năng thêm đánh giá.')
                conn.execute('UPDATE ratings SET score=?,review=?,rated_on=? WHERE rating_id=?',(score,review.strip(),date_value,existing[0]))
                return existing[0]
            if existing is not None:
                raise ValueError('Người này đã đánh giá phim. Dùng chức năng sửa đánh giá.')
            return conn.execute('INSERT INTO ratings(movie_id,viewer_id,score,review,rated_on) VALUES (?,?,?,?,?)',(movie_id,viewer_id,score,review.strip(),date_value)).lastrowid

def list_movies(keyword='', db=DEFAULT_DB):
    term = keyword.strip().replace('\\','\\\\').replace('%','\\%').replace('_','\\_')
    query = """SELECT m.movie_id,m.title,m.release_year,
    (SELECT group_concat(g.name, ', ') FROM movie_genres mg JOIN genres g ON g.genre_id=mg.genre_id WHERE mg.movie_id=m.movie_id) AS genres,
    COUNT(r.rating_id) AS rating_count, ROUND(AVG(r.score),2) AS average_score
    FROM movies m LEFT JOIN ratings r ON r.movie_id=m.movie_id
    WHERE m.title LIKE ? ESCAPE '\\'
    GROUP BY m.movie_id ORDER BY m.movie_id"""
    with connect(db,True) as conn:
        return [dict(r) for r in conn.execute(query,(f'%{term}%',))]

def list_viewers(db=DEFAULT_DB):
    with connect(db,True) as conn:
        return [dict(r) for r in conn.execute('SELECT * FROM viewers ORDER BY viewer_id')]

def list_ratings(movie_id=None, db=DEFAULT_DB):
    query = 'SELECT r.*,m.title,v.name FROM ratings r JOIN movies m ON m.movie_id=r.movie_id JOIN viewers v ON v.viewer_id=r.viewer_id'
    params = ()
    if movie_id is not None:
        query += ' WHERE r.movie_id=?'
        params = (movie_id,)
    with connect(db,True) as conn:
        return [dict(r) for r in conn.execute(query+' ORDER BY r.rating_id',params)]
