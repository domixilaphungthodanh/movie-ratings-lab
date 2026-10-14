from pathlib import Path
from contextlib import contextmanager
from datetime import date, datetime, timezone, timedelta
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / 'database/movies.db'

def today():
    return datetime.now(timezone(timedelta(hours=7))).date()

def text(value, label):
    value = value.strip()
    if not value:
        raise ValueError(f'{label} không được rỗng.')
    return value

def day(value=None):
    value = value if value is not None else today().isoformat()
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError('Ngày phải hợp lệ, dạng YYYY-MM-DD.') from None
    if parsed.isoformat() != value or parsed > today():
        raise ValueError('Ngày phải dạng YYYY-MM-DD và không ở tương lai.')
    return value

@contextmanager
def connect(db=DEFAULT_DB, readonly=False):
    path = Path(db).resolve()
    if not path.is_file():
        raise ValueError('Database chưa có. Chạy python -m movie_lab.init_db --sample trước.')
    conn = sqlite3.connect(f"{path.as_uri()}?mode={'ro' if readonly else 'rw'}", uri=True, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    try:
        yield conn
    finally:
        conn.close()
