import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from .db import DEFAULT_DB, ROOT, connect

def load_tables(db=DEFAULT_DB):
    with connect(db,True) as conn:
        ratings = pd.read_sql_query('SELECT * FROM ratings',conn)
        movies = pd.read_sql_query('SELECT m.movie_id,m.title,COUNT(r.rating_id) AS rating_count,AVG(r.score) AS average_score FROM movies m LEFT JOIN ratings r ON r.movie_id=m.movie_id GROUP BY m.movie_id ORDER BY average_score DESC,rating_count DESC,m.movie_id',conn)
        genres = pd.read_sql_query('SELECT g.name,COUNT(r.rating_id) AS rating_count,COUNT(DISTINCT mg.movie_id) AS movie_count,AVG(r.score) AS average_score FROM genres g LEFT JOIN movie_genres mg ON mg.genre_id=g.genre_id LEFT JOIN ratings r ON r.movie_id=mg.movie_id GROUP BY g.genre_id ORDER BY g.genre_id',conn)
        viewers = pd.read_sql_query('SELECT v.viewer_id,v.name,COUNT(r.rating_id) AS rating_count,AVG(r.score) AS average_score FROM viewers v LEFT JOIN ratings r ON r.viewer_id=v.viewer_id GROUP BY v.viewer_id ORDER BY v.viewer_id',conn)
    assert movies.rating_count.sum() == viewers.rating_count.sum() == len(ratings)
    return dict(ratings=ratings,movies=movies,genres=genres,viewers=viewers)

def analyze(db=DEFAULT_DB, output=None, min_ratings=5):
    if type(min_ratings) is not int or min_ratings<1:
        raise ValueError('Ngưỡng số đánh giá phải là số nguyên dương.')
    out = Path(output) if output else ROOT/'outputs'
    frames = load_tables(db)
    top = frames['movies'].loc[frames['movies'].rating_count>=min_ratings].head(10)
    for folder in ['figures','tables']:
        (out/folder).mkdir(parents=True,exist_ok=True)
    for name,frame in frames.items():
        frame.to_csv(out/'tables'/f'{name}.csv',index=False)
    sns.set_theme(style='whitegrid',font='DejaVu Sans')
    configs = [('01_score_distribution',frames['ratings'],'score','Phân phối điểm đánh giá'),('02_top_movies',top,'title',f'Top phim có ít nhất {min_ratings} đánh giá'),('03_genre_scores',frames['genres'].dropna(subset=['average_score']),'name','Điểm trung bình theo thể loại'),('04_viewer_scores',frames['viewers'].dropna(subset=['average_score']),'viewer_id','Khác biệt điểm giữa người xem')]
    for name,frame,key,title in configs:
        fig,ax=plt.subplots(figsize=(10,5))
        if frame.empty:
            ax.text(.5,.5,'Chưa đủ dữ liệu',ha='center',transform=ax.transAxes)
            ax.set_axis_off()
        elif key=='score':
            sns.histplot(data=frame,x='score',discrete=True,ax=ax)
            ax.set(xlabel='Điểm (1–10)',ylabel='Số đánh giá',xticks=range(1,11))
        elif key=='title':
            sns.barplot(data=frame,x='average_score',y='title',color='#3282b8',ax=ax)
            ax.set(xlabel='Điểm trung bình',ylabel='Phim',xlim=(0,10))
        elif key=='name':
            sns.barplot(data=frame,x='average_score',y='name',color='#3282b8',ax=ax)
            ax.set(xlabel='Điểm trung bình',ylabel='Thể loại',xlim=(0,10))
        else:
            sns.scatterplot(data=frame,x='rating_count',y='average_score',ax=ax)
            ax.set(xlabel='Số đánh giá của người xem',ylabel='Điểm trung bình người xem cho',ylim=(0,10))
        ax.set_title(title)
        fig.tight_layout()
        fig.savefig(out/'figures'/f'{name}.png',dpi=160)
        plt.close(fig)
    ratings=frames['ratings']
    findings=[f'1. Có {len(ratings)} đánh giá, từ {ratings.viewer_id.nunique()} người xem; điểm trung bình toàn bộ là {ratings.score.mean():.2f}.' if len(ratings) else '1. Chưa có đánh giá.',f'2. Có {len(frames["movies"])} phim; {(frames["movies"].rating_count==0).sum()} phim chưa có đánh giá.',f'3. Có {(frames["movies"].rating_count>=min_ratings).sum()} phim đạt ngưỡng {min_ratings} đánh giá để xếp hạng.']
    report='# Báo cáo phim và đánh giá\n\n'+'\n\n'.join(findings)+'\n\n## Giới hạn\n\nMẫu --sample là GIẢ LẬP seed 42, không phải điểm đánh giá phim thật. Khi nhập dữ liệu thật, cập nhật mô tả nguồn trước khi chia sẻ.\n\nMột phim có nhiều thể loại nên cùng đánh giá xuất hiện ở nhiều nhóm thể loại; không cộng số đánh giá các thể loại để tính tổng. Điểm thể loại là trung bình các đánh giá thuộc nhóm, không phải trung bình các điểm phim.\n\nPhim chưa được đánh giá có điểm NULL, không phải 0. Ngưỡng xếp hạng không chứng minh chất lượng phim; số người đánh giá nhỏ và sở thích cá nhân ảnh hưởng kết quả. Mỗi người chỉ có một đánh giá hiện tại cho mỗi phim; sửa sẽ thay điểm/nhận xét/ngày, không lưu lịch sử sửa.\n'
    (out/'report.md').write_text(report,encoding='utf-8')
    print('Đã xuất 4 biểu đồ, 4 bảng và báo cáo:',out)
    return frames

def main():
    p=argparse.ArgumentParser(description='Phân tích bằng pandas và Seaborn')
    p.add_argument('--db',type=Path,default=DEFAULT_DB)
    p.add_argument('--output',type=Path)
    p.add_argument('--min-ratings',type=int,default=5)
    a=p.parse_args()
    try:
        analyze(a.db,a.output,a.min_ratings)
    except (ValueError,OSError) as exc:
        p.exit(1,f'Lỗi: {exc}\n')

if __name__=='__main__':
    main()
