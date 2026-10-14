# Lời giải tham khảo

1. Mẫu có 30 phim, 5 thể loại, 20 người xem, 200 đánh giá.
2. movies JOIN movie_genres JOIN genres. Bảng liên kết biểu diễn nhiều–nhiều và dùng khóa chính ghép.
3. LEFT JOIN giữ phim chưa có đánh giá. Phim 30 có COUNT(r.rating_id)=0 và AVG(score)=NULL. COUNT(*) sẽ đếm dòng giữ lại, nên không phù hợp.
4. Xem sql/analysis.sql: HAVING COUNT(r.rating_id)>=5. Không coi một đánh giá 10 điểm là bằng chứng phim hay nhất.
5. Sửa UPDATE nên số dòng giữ nguyên. Thêm INSERT trùng cặp phim/người bị từ chối.
6. Xem tests/test_movie_lab.py. Các thao tác thất bại phải giữ nguyên dữ liệu.
7. Phim nhiều thể loại khiến đánh giá góp vào nhiều nhóm; các nhóm không độc lập. Tổng thật đếm trực tiếp ratings.
8. AVG(score) và COUNT(*) GROUP BY viewer_id. Điểm khác nhau còn do phim họ chọn xem; chưa đủ kết luận tính cách.
9. Tổng ratings bằng tổng rating_count theo phim và người xem, không bằng tổng theo thể loại. load_tables kiểm tra điều này.
10. python -m movie_lab.analyze --min-ratings 10 --output outputs/threshold10. Ngưỡng cao hơn loại phim ít đánh giá; cần xem cả số mẫu và điểm.
