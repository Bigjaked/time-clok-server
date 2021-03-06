""" This file contains our SqlAlchemy connection generator function which generates
session factories for our databases. It also has a few utility functions that get used
throughout the application. """
from datetime import datetime
from multiprocessing import Lock
from typing import Union

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from core.defines import DATE_FORMAT, DATE_TIME_FORMATS
import asyncio


class SqlAlchemyConnGenerator:
    """
    Stores configuration information for sql database connection and implements helper
    methods for the generation of a session maker, sessions and engines.
    Defaults to using the SingletonThreadPool for use in multi-threaded applications.
    """

    _lock: Lock

    def __init__(
        self,
        user=None,
        passwd=None,
        db_name=None,
        host=None,
        port=None,
        db_type=None,
        sqlite_db=None,
        pool_size=None,
        **kwargs,
    ):
        self._username = user
        self._password = passwd
        self._db_name = db_name
        self._hostname = host
        self._host_port = port
        self._database_type = db_type or "mysql+mysqlconnector"
        self._uri_string = "{0}://{1}:{2}@{3}:{4}/{5}"
        self._lock = Lock()

        self._pool_size = pool_size

        self._sqlite_db = sqlite_db
        self._pool_type = kwargs.get("pool_type", QueuePool)
        self._echo = kwargs.get("echo", False)

        self._engine = None
        self._maker = None
        self._current_session = None

    def init_app(self, config: dict):
        self._username = config.get("DATABASE_USERNAME", None)
        self._password = config.get("DATABASE_PASSWORD", None)
        self._db_name = config.get("DATABASE_NAME", None)
        self._hostname = config.get("DATABASE_HOST", None)
        self._host_port = config.get("DATABASE_PORT", 3306)
        self._database_type = config.get("DATABASE_CONNECTOR", "mysql+mysqlconnector")
        self._uri_string = "{0}://{1}:{2}@{3}:{4}/{5}"
        self._lock = Lock()

        self._pool_size = config.get("DATABASE_POOL_SIZE", None)
        if config.get("USE_SQLITE_DATABASE", False):
            self._sqlite_db = config.get
        self._sqlite_db = config.get("SQLITE_DATABASE_NAME", False) or False
        self._pool_type = config.get("DATABASE_POOL_TYPE", QueuePool)
        self._echo = config.get("DATABASE_ECHO", False)

        self._engine = None
        self._maker = None
        self._current_session = None

    @property
    def sqlite_db(self):
        return self._sqlite_db

    @sqlite_db.setter
    def sqlite_db(self, test):
        self._sqlite_db = test

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            if self._sqlite_db:
                self._engine = create_engine(self.db_uri, echo=self._echo)
            else:
                self._engine = create_engine(
                    self.db_uri,
                    poolclass=self._pool_type,
                    echo=self._echo,
                    pool_size=self._pool_size or 0,
                )
        return self._engine

    @property
    def port(self):
        return self._host_port

    @property
    def db_uri(self):
        if self._sqlite_db:
            if isinstance(self._sqlite_db, str):
                return f"sqlite:///{self._sqlite_db}"
            else:
                return "sqlite://"
        else:
            return self._uri_string.format(
                self._database_type,
                self._username,
                self._password,
                self._hostname,
                self._host_port,
                self._db_name,
            )

    def maker(self):
        if self._maker is None:
            self._maker = sessionmaker(
                bind=self.engine, autocommit=False, autoflush=False
            )
        return self._maker()

    def make_new_session(self):
        self._current_session = self.maker()

    @property
    def session(self):
        if self._current_session is None:
            self.make_new_session()
        return self._current_session

    def create_tables(self, base):
        base.metadata.create_all(self.engine)

    @property
    def locked_session(self):
        # with self._lock:
        return self.session

    @property
    def spawn_unique_session(self):
        """
        This property is used whenever we want to spawn a totally unique session
        instance. This is typically used in cases where we are doing things with threads
        or processes. We also return the lock instance for this connection generator.
        This way the threads or processes can each have their own unique session but can
        still use a shared lock to prevent integrity errors.

        :return:
        """
        class_self = self

        class SessionWrapper:
            """
            This SessionWrapper class mimics the interface of SqlAlchemyConnGenerator so
            that we can use the two interchangeably.
            """

            def __init__(self):
                self._session = None
                self._lock = class_self._lock

            @property
            def session(self):
                if self._session is None:
                    self._session = class_self.maker()
                return self._session

            @property
            def locked_session(self):
                with self._lock:
                    return self.session

        session_wrapper = SessionWrapper()

        return session_wrapper


def to_json(data):
    if isinstance(data, (str, int, float, list, tuple, bool)):
        return data
    elif isinstance(data, datetime):
        # return data.strftime("%Y/%m/%d %H:%M")
        return data.timestamp()

    return data


def run_coroutine(func: asyncio.Future):
    if asyncio.iscoroutine(func) or asyncio.iscoroutine(func):
        return asyncio.get_event_loop().run_until_complete(func)
