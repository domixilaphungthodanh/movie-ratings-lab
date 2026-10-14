import argparse
import sqlite3
from pathlib import Path
from .db import DEFAULT_DB, connect
from . import service

def number(prompt):
    try:
        return int(input(prompt))
    except ValueError:
        raise ValueError('Vui lòng nhập số nguyên.') from None

def show(rows):
    if not rows:
        print('Không có kết quả.')
    for row in rows:
        print(' | '.join(f'{k}: {v if v is not None else "Chưa có"}' for k,v in row.items()))

def main():
    parser = argparse.ArgumentParser(description='Theo dõi phim và đánh giá')
    parser.add_argument('--db',type=Path,default=DEFAULT_DB)
    args = parser.parse_args()
    try:
        with connect(args.db,True) as conn:
            conn.execute('SELECT 1 FROM movies')
    except (ValueError,sqlite3.Error) as exc:
        parser.exit(1,f'Lỗi: {exc}\n')
    while True:
        try:
            print('\nPHIM VÀ ĐÁNH GIÁ\n1. Thêm phim\n2. Tìm / xem phim\n3. Thêm người xem\n4. Xem người xem\n5. Thêm đánh giá\n6. Sửa đánh giá\n7. Xem đánh giá\n0. Thoát')
            choice = input('Chọn: ').strip()
            if choice == '0':
                return
            if choice == '1':
                title = input('Tên phim: ')
                year = number('Năm phát hành: ')
                genres = input('Thể loại, ngăn bằng dấu phẩy: ').split(',')
                print('Mã phim:',service.add_movie(title,year,genres,args.db))
            elif choice == '2':
                show(service.list_movies(input('Tên phim (Enter = tất cả): '),args.db))
            elif choice == '3':
                print('Mã người xem:',service.add_viewer(input('Tên: '),args.db))
            elif choice == '4':
                show(service.list_viewers(args.db))
            elif choice in ('5','6'):
                result = service.rate_movie(number('Mã phim: '),number('Mã người xem: '),number('Điểm 1–10: '),input('Nhận xét (tùy chọn): '),input('Ngày YYYY-MM-DD (Enter = hôm nay): ').strip() or None, args.db,update=choice=='6')
                print('Đã lưu đánh giá #',result)
            elif choice == '7':
                show(service.list_ratings(db=args.db))
            else:
                print('Lựa chọn không hợp lệ.')
        except (EOFError,KeyboardInterrupt):
            print('\nĐã thoát.')
            return
        except (ValueError,sqlite3.Error,OSError) as exc:
            print('Lỗi:',exc)

if __name__ == '__main__':
    main()
