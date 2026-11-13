import os
from contextlib import contextmanager

import pymysql
from pymysql.constants import CLIENT
from pymysql.cursors import DictCursor

from .errors import NotFoundError, translate_mysql_error


def _connect():
    try:
        return pymysql.connect(
            host=os.getenv("MYSQL_HOST", "127.0.0.1"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DATABASE", "tower_running"),
            unix_socket=os.getenv("MYSQL_UNIX_SOCKET") or None,
            charset="utf8mb4",
            autocommit=False,
            # Rows come back as {column: value} dicts
            cursorclass=DictCursor,
            # rowcount of UPDATE = rows matched, not rows changed, so an
            # update that sets the same values is not reported as "not found"
            client_flag=CLIENT.FOUND_ROWS,
        )
    except pymysql.err.MySQLError as exc:
        raise translate_mysql_error(exc) from exc


class _Database:
    def __init__(self, connection):
        self._connection = connection

    def execute(self, sql, params=None):
        cursor = self._connection.cursor()
        try:
            if params is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, params)
        except pymysql.err.MySQLError as exc:
            raise translate_mysql_error(exc) from exc
        return cursor

    def fetch_one(self, sql, params, not_found: str):
        """Run a SELECT and return its single row, or raise NotFoundError."""
        row = self.execute(sql, params).fetchone()
        if row is None:
            raise NotFoundError(not_found)
        return row

    def fetch_all(self, sql, params=None):
        return self.execute(sql, params).fetchall()

    def modify(self, sql, params, not_found: str):
        """Run an UPDATE/DELETE that must hit at least one row."""
        cursor = self.execute(sql, params)
        if cursor.rowcount == 0:
            raise NotFoundError(not_found)
        return cursor

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        self._connection.close()


@contextmanager
def get_db():
    db = _Database(_connect())
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
