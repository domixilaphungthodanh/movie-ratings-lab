CREATE TABLE movies (
 movie_id INTEGER PRIMARY KEY,
 title TEXT NOT NULL CHECK(length(trim(title))>0),
 release_year INTEGER NOT NULL CHECK(release_year BETWEEN 1888 AND 2100)
);
CREATE TABLE genres (
 genre_id INTEGER PRIMARY KEY,
 name TEXT NOT NULL UNIQUE CHECK(length(trim(name))>0)
);
CREATE TABLE movie_genres (
 movie_id INTEGER NOT NULL REFERENCES movies(movie_id),
 genre_id INTEGER NOT NULL REFERENCES genres(genre_id),
 PRIMARY KEY(movie_id,genre_id)
);
CREATE TABLE viewers (
 viewer_id INTEGER PRIMARY KEY,
 name TEXT NOT NULL CHECK(length(trim(name))>0)
);
CREATE TABLE ratings (
 rating_id INTEGER PRIMARY KEY,
 movie_id INTEGER NOT NULL REFERENCES movies(movie_id),
 viewer_id INTEGER NOT NULL REFERENCES viewers(viewer_id),
 score INTEGER NOT NULL CHECK(typeof(score)='integer' AND score BETWEEN 1 AND 10),
 review TEXT NOT NULL DEFAULT '',
 rated_on TEXT NOT NULL CHECK(rated_on GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]' AND date(rated_on,'+0 days') IS NOT NULL AND date(rated_on,'+0 days')=rated_on),
 UNIQUE(movie_id,viewer_id)
);
CREATE INDEX ratings_movie ON ratings(movie_id);
CREATE INDEX ratings_viewer ON ratings(viewer_id);
