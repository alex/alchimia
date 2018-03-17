from __future__ import absolute_import, division

import os
from binascii import hexlify

import sqlalchemy
from sqlalchemy.engine import RowProxy
from sqlalchemy.event import listens_for
from sqlalchemy.exc import StatementError
from sqlalchemy.schema import CreateTable

from twisted.trial import unittest

from alchimia import TWISTED_STRATEGY, wrap_engine
from alchimia.engine import (
    TwistedEngine, TwistedConnection, TwistedTransaction,
)

from .doubles import FakeThreadedReactor, ImmediateWorker


def create_engine(**kwargs):
    if 'TEST_DB_URL' in os.environ:
        TEST_DB_URL = os.environ['TEST_DB_URL']
    else:
        TEST_DB_URL = 'sqlite://'

    if TEST_DB_URL.startswith("sqlite:"):
        # per
        # http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html#serializable-isolation-savepoints-transactional-ddl,
        # necessary to test savepoints in SQLite.

        sub_engine = sqlalchemy.create_engine(TEST_DB_URL, **kwargs)

        @listens_for(sub_engine, "connect")
        def do_connect(dbapi_connection, connection_record):
            # disable pysqlite's emitting of the BEGIN statement entirely.
            # also stops it from emitting COMMIT before any DDL.
            dbapi_connection.isolation_level = None

        @listens_for(sub_engine, "begin")
        def do_begin(conn):
            # emit our own BEGIN
            conn.execute("BEGIN")
        return wrap_engine(FakeThreadedReactor(), sub_engine, ImmediateWorker)

    engine = sqlalchemy.create_engine(
        TEST_DB_URL, strategy=TWISTED_STRATEGY,
        reactor=FakeThreadedReactor(), create_worker=ImmediateWorker,
        **kwargs)
    if TEST_DB_URL.startswith("postgresql"):
        tmpdb_name = "testdb"+hexlify(os.urandom(16)).decode()
        tmpdb_url = '/'.join(
            TEST_DB_URL.split('/')[:-1] + [tmpdb_name])
        conn = engine.connect().result
        conn.execute("commit")
        conn.execute("CREATE DATABASE {}".format(tmpdb_name))
        conn.close()
        engine = sqlalchemy.create_engine(
            tmpdb_url, strategy=TWISTED_STRATEGY,
            reactor=FakeThreadedReactor(), create_worker=ImmediateWorker,
            **kwargs)
    return engine


class TestEngineCreation(unittest.TestCase):
    def test_simple_create_with_strategy(self):
        engine = sqlalchemy.create_engine(
            "sqlite://",
            strategy=TWISTED_STRATEGY,
            reactor=FakeThreadedReactor(),
        )
        assert isinstance(engine, TwistedEngine)

    def test_wrap_engine(self):
        sub_engine = sqlalchemy.create_engine("sqlite://")
        twisted_engine = wrap_engine(FakeThreadedReactor(), sub_engine)
        assert isinstance(twisted_engine, TwistedEngine)


class TestEngine(unittest.TestCase):
    def test_connect(self):
        engine = create_engine()
        d = engine.connect()
        connection = self.successResultOf(d)
        assert isinstance(connection, TwistedConnection)

    def test_execute(self):
        engine = create_engine()
        d = engine.execute("SELECT 42")
        result = self.successResultOf(d)
        d = result.scalar()
        assert self.successResultOf(d) == 42

    def test_table_names(self):
        engine = create_engine()
        d = engine.table_names()
        assert self.successResultOf(d) == []
        d = engine.execute("CREATE TABLE mytable (id int)")
        self.successResultOf(d)
        d = engine.table_names()
        assert self.successResultOf(d) == ['mytable']

    def test_table_names_with_connection(self):
        # There's no easy way to tell which connection was actually used, so
        # this test just provides coverage for the code path.
        engine = create_engine()
        conn = self.successResultOf(engine.connect())
        d = engine.table_names(connection=conn)
        assert self.successResultOf(d) == []
        d = conn.execute("CREATE TABLE mytable (id int)")
        self.successResultOf(d)
        d = engine.table_names(connection=conn)
        assert self.successResultOf(d) == ['mytable']

    def test_has_table(self):
        engine = create_engine()
        d = engine.has_table('mytable')
        assert self.successResultOf(d) is False
        d = engine.execute("CREATE TABLE mytable (id int)")
        self.successResultOf(d)
        d = engine.has_table('mytable')
        assert self.successResultOf(d) is True


class TestConnection(unittest.TestCase):
    def get_connection(self):
        engine = create_engine()
        return self.successResultOf(engine.connect())

    def execute_fetchall(self, conn, query_obj):
        result = self.successResultOf(conn.execute(query_obj))
        return self.successResultOf(result.fetchall())

    def test_execute(self):
        conn = self.get_connection()
        d = conn.execute("SELECT 42")
        result = self.successResultOf(d)
        d = result.scalar()
        assert self.successResultOf(d) == 42

    def test_close(self):
        conn = self.get_connection()
        assert not conn.closed
        result = self.successResultOf(conn.execute("SELECT 42"))
        assert self.successResultOf(result.scalar()) == 42

        self.successResultOf(conn.close())
        assert conn.closed
        failure = self.failureResultOf(
            conn.execute("SELECT 42"), StatementError)
        assert "This Connection is closed" in str(failure)

    def test_in_transaction(self):
        conn = self.get_connection()
        assert not conn.in_transaction()

        transaction = self.successResultOf(conn.begin())
        assert isinstance(transaction, TwistedTransaction)
        assert conn.in_transaction()

        self.successResultOf(transaction.close())
        assert not conn.in_transaction()

    def test_repeated_begin(self):
        conn = self.get_connection()
        assert not conn.in_transaction()

        trx1 = self.successResultOf(conn.begin())
        assert conn.in_transaction()
        trx2 = self.successResultOf(conn.begin())
        assert conn.in_transaction()

        self.successResultOf(trx2.close())
        assert conn.in_transaction()
        self.successResultOf(trx1.close())
        assert not conn.in_transaction()

    def test_savepoints(self):
        conn = self.get_connection()
        assert not conn.in_transaction()
        self.successResultOf(conn.execute(
            "create table effects (which integer)"
        ))
        txn = self.successResultOf(conn.begin())
        self.successResultOf(conn.execute("insert into effects values (1)"))
        save = self.successResultOf(conn.begin_nested())
        self.successResultOf(conn.execute("insert into effects values (2)"))
        self.successResultOf(save.rollback())
        self.assertEqual(
            [(1,)],
            self.successResultOf(
                self.successResultOf(conn.execute("select * from effects"))
                .fetchall()
            )
        )
        self.successResultOf(txn.commit())

    def test_transaction_commit(self):
        metadata = sqlalchemy.MetaData()
        tbl = sqlalchemy.Table(
            'mytable', metadata,
            sqlalchemy.Column("id", sqlalchemy.Integer(), primary_key=True),
            sqlalchemy.Column("num", sqlalchemy.Integer()),
        )

        conn = self.get_connection()
        self.successResultOf(conn.execute(CreateTable(tbl)))
        trx = self.successResultOf(conn.begin())
        self.successResultOf(conn.execute(tbl.insert().values(num=42)))
        rows = self.execute_fetchall(conn, tbl.select())
        assert len(rows) == 1

        self.successResultOf(trx.commit())
        rows = self.execute_fetchall(conn, tbl.select())
        assert len(rows) == 1

    def test_transaction_rollback(self):
        metadata = sqlalchemy.MetaData()
        tbl = sqlalchemy.Table(
            'mytable', metadata,
            sqlalchemy.Column("id", sqlalchemy.Integer(), primary_key=True),
            sqlalchemy.Column("num", sqlalchemy.Integer()),
        )

        conn = self.get_connection()
        self.successResultOf(conn.execute(CreateTable(tbl)))
        trx = self.successResultOf(conn.begin())
        self.successResultOf(conn.execute(tbl.insert().values(num=42)))
        rows = self.execute_fetchall(conn, tbl.select())
        assert len(rows) == 1

        self.successResultOf(trx.rollback())
        rows = self.execute_fetchall(conn, tbl.select())
        assert len(rows) == 0


class TestResultProxy(unittest.TestCase):
    def create_default_table(self):
        engine = create_engine()
        d = engine.execute("CREATE TABLE testtable (id int)")
        self.successResultOf(d)
        return engine

    def test_fetchone(self):
        engine = create_engine()
        d = engine.execute("SELECT 42")
        result = self.successResultOf(d)
        d = result.fetchone()
        row = self.successResultOf(d)
        assert isinstance(row, RowProxy)
        assert row[0] == 42

    def test_fetchall(self):
        engine = create_engine()
        d = engine.execute("SELECT 10")
        result = self.successResultOf(d)
        d = result.fetchall()
        rows = self.successResultOf(d)
        assert len(rows) == 1
        assert rows[0][0] == 10

    def test_first(self):
        engine = self.create_default_table()
        d = engine.execute("INSERT INTO testtable (id) VALUES (2)")
        self.successResultOf(d)
        d = engine.execute("INSERT INTO testtable (id) VALUES (3)")
        self.successResultOf(d)
        d = engine.execute("SELECT * FROM testtable ORDER BY id ASC")
        result = self.successResultOf(d)
        d = result.first()
        row = self.successResultOf(d)
        assert len(row) == 1
        assert row[0] == 2

    def test_keys(self):
        engine = create_engine()
        d = engine.execute("CREATE TABLE testtable (id int, name varchar)")
        self.successResultOf(d)
        d = engine.execute("SELECT * FROM testtable")
        result = self.successResultOf(d)
        d = result.keys()
        keys = self.successResultOf(d)
        assert len(keys) == 2
        assert 'id' in keys
        assert 'name' in keys

    def test_returns_rows(self):
        engine = self.create_default_table()
        d = engine.execute("INSERT INTO testtable values (2)")
        result = self.successResultOf(d)
        assert not result.returns_rows
        d = engine.execute("SELECT * FROM testtable")
        result = self.successResultOf(d)
        assert result.returns_rows

    def test_rowcount(self):
        engine = self.create_default_table()
        d = engine.execute("INSERT INTO testtable VALUES (1)")
        self.successResultOf(d)
        d = engine.execute("INSERT INTO testtable VALUES (2)")
        self.successResultOf(d)
        d = engine.execute("INSERT INTO testtable VALUES (3)")
        self.successResultOf(d)
        d = engine.execute("UPDATE testtable SET id = 7 WHERE id < 3")
        result = self.successResultOf(d)
        assert result.rowcount == 2
        d = engine.execute("DELETE from testtable")
        result = self.successResultOf(d)
        assert result.rowcount == 3

    def test_inserted_primary_key(self):
        metadata = sqlalchemy.MetaData()
        tbl = sqlalchemy.Table(
            'testtable', metadata,
            sqlalchemy.Column("id", sqlalchemy.Integer(), primary_key=True),
        )
        engine = create_engine()
        d = engine.execute(CreateTable(tbl))
        self.successResultOf(d)
        d = engine.execute(tbl.insert().values())
        result = self.successResultOf(d)
        assert result.inserted_primary_key == [1]

    def test_close(self):
        engine = self.create_default_table()
        d = engine.execute("INSERT INTO testtable VALUES (1)")
        self.successResultOf(d)
        d = engine.execute("INSERT INTO testtable VALUES (2)")
        self.successResultOf(d)
        d = engine.execute("SELECT * FROM testtable")
        result = self.successResultOf(d)
        self.successResultOf(result.close())
