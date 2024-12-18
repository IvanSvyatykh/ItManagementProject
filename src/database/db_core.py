from sqlalchemy import Connection, Engine, create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from database.repository import MonitoringEventsRepository, StatRepository

from database.repository import AuthRepository
from config import (
    AUTH_DB_USER,
    AUTH_DB_PASSWORD,
    AUTH_DB_DOMAIN,
    AUTH_DB_PORT,
    AUTH_DB_NAME,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DOMAIN,
    POSTGRES_DB_NAME,
    POSTGRES_PORT,
)


class PostgresConfig:

    def __init__(
        self,
        user_name: str,
        password: str,
        domain: str,
        port: str,
        db_name: str,
    ):
        self.__url = f"postgresql+psycopg2://{user_name}:{password}@{domain}:{port}/{db_name}"

    def create_engine(self) -> None:
        self.__engine = create_engine(
            self.__url, echo=True, pool_size=1, max_overflow=0
        )

    @property
    def engine(self) -> Engine:
        return self.__engine


class AuthDBUnitOfWork:
    session_factory = None

    def __init__(self):

        if AuthDBUnitOfWork.session_factory is None:
            engine = PostgresConfig(
                user_name=AUTH_DB_USER,
                password=AUTH_DB_PASSWORD,
                domain=AUTH_DB_DOMAIN,
                port=AUTH_DB_PORT,
                db_name=AUTH_DB_NAME,
            )
            engine.create_engine()
            AuthDBUnitOfWork.session_factory = sessionmaker(
                autoflush=True, bind=engine.engine
            )

    @contextmanager
    def start(self) -> Session:
        self._session = AuthDBUnitOfWork.session_factory()
        try:
            yield self
            self._session.commit()
            self._session.close()
        except:
            self._session.rollback()
            raise
        finally:
            self._session.close()

    @property
    def auth_repository(self) -> AuthRepository:
        return AuthRepository(self._session)

    @property
    def stat_repository(self) -> AuthRepository:
        return StatRepository(self._session)


class IsDBUnitOfWork:
    session_factory = None

    def __init__(self):

        if IsDBUnitOfWork.session_factory is None:
            config = PostgresConfig(
                user_name=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                domain=POSTGRES_DOMAIN,
                port=POSTGRES_PORT,
                db_name=POSTGRES_DB_NAME,
            )
            config.create_engine()
            IsDBUnitOfWork.session_factory = sessionmaker(
                autoflush=True, bind=config.engine
            )

    @contextmanager
    def start(self) -> Session:
        self._session = IsDBUnitOfWork.session_factory()
        try:
            yield self
            self._session.commit()
        except:
            self._session.rollback()
            raise
        finally:
            self._session.close()

    @property
    def monitoring_events_repository(self) -> MonitoringEventsRepository:
        return MonitoringEventsRepository(self._session)
