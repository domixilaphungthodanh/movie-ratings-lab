import tempfile
import unittest
import sqlite3
from pathlib import Path
from movie_lab.init_db import initialize
from movie_lab import service
from movie_lab.db import connect
from movie_lab.analyze import analyze,load_tables

class MovieTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/'test.db'
        initialize(self.db)
        self.movie=service.add_movie('Test',2020,['Hài','hài','Tâm lý'],self.db)
        self.viewer=service.add_viewer('A',self.db)

    def test_many_to_many_and_unrated(self):
        row=service.list_movies(db=self.db)[0]
        self.assertEqual(row['rating_count'],0)
        self.assertIsNone(row['average_score'])
        with connect(self.db) as c:
            self.assertEqual(c.execute('SELECT COUNT(*) FROM movie_genres').fetchone()[0],2)

    def test_add_duplicate_update(self):
        rid=service.rate_movie(self.movie,self.viewer,7,db=self.db)
        with self.assertRaises(ValueError):
            service.rate_movie(self.movie,self.viewer,8,db=self.db)
        self.assertEqual(service.rate_movie(self.movie,self.viewer,9,db=self.db,update=True),rid)
        rows=service.list_ratings(db=self.db)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['score'],9)

    def test_bad_scores_dates_ids(self):
        for score in [0,11,4.5,True]:
            with self.assertRaises(ValueError):
                service.rate_movie(self.movie,self.viewer,score,db=self.db)
        for day in ['2025-02-30','20250101','2099-01-01']:
            with self.assertRaises(ValueError):
                service.rate_movie(self.movie,self.viewer,7,rated_on=day,db=self.db)
        for m,v in [(999,self.viewer),(self.movie,999)]:
            with self.assertRaises(ValueError):
                service.rate_movie(m,v,7,db=self.db)
        with self.assertRaises(ValueError):
            service.rate_movie(self.movie,self.viewer,7,db=self.db,update=True)
        self.assertEqual(service.list_ratings(db=self.db),[])

    def test_validation_and_search(self):
        for title,year,genres in [(' ',2020,['a']),('A',1700,['a']),('A',2020,[]),('A',2020,[' '])]:
            with self.assertRaises(ValueError):
                service.add_movie(title,year,genres,self.db)
        with self.assertRaises(ValueError):
            service.add_viewer(' ',self.db)
        self.assertEqual(service.list_movies("' OR 1=1 --",self.db),[])
        self.assertEqual(service.list_movies('%',self.db),[])

    def test_db_constraints(self):
        with connect(self.db) as c:
            self.assertEqual(c.execute('PRAGMA foreign_keys').fetchone()[0],1)
            for values in [(999,self.viewer,7,'2025-01-01'),(self.movie,self.viewer,0,'2025-01-01'),(self.movie,self.viewer,4.5,'2025-01-01'),(self.movie,self.viewer,7,'2025-02-30')]:
                with self.assertRaises(sqlite3.IntegrityError),c:
                    c.execute('INSERT INTO ratings(movie_id,viewer_id,score,rated_on) VALUES (?,?,?,?)',values)

    def test_no_overwrite(self):
        before=self.db.read_bytes()
        with self.assertRaises(ValueError):
            initialize(self.db,True)
        self.assertEqual(before,self.db.read_bytes())

    def test_sample_counts_and_reproducibility(self):
        a,b=Path(self.tmp.name)/'a.db',Path(self.tmp.name)/'b.db'
        initialize(a,True)
        initialize(b,True)
        with connect(a) as x,connect(b) as y:
            for table,count in [('movies',30),('genres',5),('viewers',20),('ratings',200)]:
                first=[tuple(r) for r in x.execute(f'SELECT * FROM {table} ORDER BY 1')]
                self.assertEqual(len(first),count)
                self.assertEqual(first,[tuple(r) for r in y.execute(f'SELECT * FROM {table} ORDER BY 1')])
            self.assertEqual(x.execute('PRAGMA foreign_key_check').fetchall(),[])
        frames=load_tables(a)
        self.assertEqual(frames['movies'].rating_count.sum(),200)
        self.assertEqual(frames['viewers'].rating_count.sum(),200)
        self.assertGreater(frames['genres'].rating_count.sum(),200)
        analyze(a,Path(self.tmp.name)/'out')
        self.assertEqual(len(list((Path(self.tmp.name)/'out/figures').glob('*.png'))),4)

    def test_empty_analysis(self):
        analyze(self.db,Path(self.tmp.name)/'empty')
        self.assertEqual(len(list((Path(self.tmp.name)/'empty/figures').glob('*.png'))),4)

if __name__=='__main__':
    unittest.main()
