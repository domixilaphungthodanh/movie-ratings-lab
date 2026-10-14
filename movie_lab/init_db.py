import argparse
import sqlite3
import random
from pathlib import Path
from datetime import date, timedelta
from .db import DEFAULT_DB, ROOT

def initialize(db=DEFAULT_DB, sample=False):
    path = Path(db).resolve()
    path.parent.mkdir(parents=True,exist_ok=True)
    try:
        with path.open('xb'):
            pass
    except FileExistsError:
        raise ValueError('Database đã tồn tại; dùng --db với đường dẫn khác.') from None
    conn = None
    try:
        conn = sqlite3.connect(path)
        conn.execute('PRAGMA foreign_keys=ON')
        conn.executescript((ROOT/'sql/schema.sql').read_text(encoding='utf-8'))
        with conn:
            if sample:
                rng = random.Random(42)
                genres = ['hành động','hài','tâm lý','khoa học viễn tưởng','hoạt hình']
                conn.executemany('INSERT INTO genres VALUES (?,?)',enumerate(genres,1))
                for i in range(1,31):
                    conn.execute('INSERT INTO movies VALUES (?,?,?)',(i,f'Phim giả lập {i:02d}',rng.randint(2000,2025)))
                    for genre_id in rng.sample(range(1,6),rng.randint(1,3)):
                        conn.execute('INSERT INTO movie_genres VALUES (?,?)',(i,genre_id))
                conn.executemany('INSERT INTO viewers VALUES (?,?)',[(i,f'Người xem {i:02d}') for i in range(1,21)])
                pairs = rng.sample([(m,v) for m in range(1,30) for v in range(1,21)],200)
                for m,v in pairs:
                    when = date(2025,1,1)+timedelta(days=rng.randrange(365))
                    conn.execute('INSERT INTO ratings(movie_id,viewer_id,score,review,rated_on) VALUES (?,?,?,?,?)',(m,v,rng.randint(1,10),'Nhận xét giả lập',when.isoformat()))
            assert not conn.execute('PRAGMA foreign_key_check').fetchall()
    except Exception:
        if conn:
            conn.close()
            conn = None
        path.unlink(missing_ok=True)
        raise
    finally:
        if conn:
            conn.close()
    return path

def main():
    parser = argparse.ArgumentParser(description='Tạo database mới, không ghi đè dữ liệu')
    parser.add_argument('--db',type=Path,default=DEFAULT_DB)
    parser.add_argument('--sample',action='store_true')
    args = parser.parse_args()
    try:
        print('Đã tạo:',initialize(args.db,args.sample))
    except (ValueError, OSError, sqlite3.Error) as exc:
        parser.exit(1,f'Lỗi: {exc}\n')
    if args.sample:
        print('GIẢ LẬP seed 42: 30 phim, 5 thể loại, 20 người xem, 200 đánh giá; phim 30 chưa có đánh giá.')

if __name__ == '__main__':
    main()
