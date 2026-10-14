-- Movies with no ratings are retained.
SELECT m.movie_id,m.title,COUNT(r.rating_id) AS rating_count,AVG(r.score) AS average_score
FROM movies m LEFT JOIN ratings r ON r.movie_id=m.movie_id
GROUP BY m.movie_id ORDER BY average_score DESC;

-- Rank only movies with sufficient ratings.
SELECT m.movie_id,m.title,COUNT(r.rating_id) AS rating_count,AVG(r.score) AS average_score
FROM movies m JOIN ratings r ON r.movie_id=m.movie_id
GROUP BY m.movie_id HAVING COUNT(r.rating_id)>=5
ORDER BY average_score DESC,rating_count DESC,m.movie_id;

-- Ratings belong to multiple genre groups; do not sum counts across genres.
SELECT g.name,COUNT(r.rating_id) AS rating_count,AVG(r.score) AS average_score
FROM genres g JOIN movie_genres mg ON mg.genre_id=g.genre_id
JOIN ratings r ON r.movie_id=mg.movie_id
GROUP BY g.genre_id ORDER BY average_score DESC;

SELECT strftime('%Y-%m',rated_on) AS month,COUNT(*) AS rating_count
FROM ratings GROUP BY month ORDER BY month;

SELECT viewer_id,COUNT(*) AS rating_count,AVG(score) AS average_score
FROM ratings GROUP BY viewer_id;
