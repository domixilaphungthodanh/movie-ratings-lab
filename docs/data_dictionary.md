# Từ điển dữ liệu

| Bảng | Cột | Ý nghĩa |
|---|---|---|
| movies | movie_id, title, release_year | Mã phim, tên, năm phát hành 1888–2100 |
| genres | genre_id, name | Mã và tên thể loại duy nhất |
| movie_genres | movie_id, genre_id | Hai khóa ngoại; khóa chính ghép ngăn liên kết trùng |
| viewers | viewer_id, name | Mã người xem và tên; tên có thể trùng |
| ratings | rating_id, movie_id, viewer_id | Mã đánh giá và hai khóa ngoại |
| ratings | score, review, rated_on | Điểm nguyên 1–10, nhận xét, ngày ISO |

UNIQUE(movie_id,viewer_id) ngăn một người có hai đánh giá hiện tại cho phim. Foreign key ngăn liên kết không tồn tại. NULL ở AVG nghĩa là chưa có đánh giá. Transaction giúp thêm phim và thể loại thành công toàn bộ hoặc rollback.
