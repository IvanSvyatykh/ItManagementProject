from sqlalchemy import Connection, Engine, create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from database.repository import MonitoringEventsRepository

from database.repository import AuthRepository


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
            self.__url, echo=True, pool_size=2, max_overflow=0
        )

    @property
    def engine(self) -> Engine:
        return self.__engine


class AuthDBUnitOfWork:
    __session_factory = None

    def __init__(self, db_config: PostgresConfig):

        if self.__session_factory is None:
            self.__session_factory = sessionmaker(
                autoflush=True, bind=db_config.engine
            )

    @contextmanager
    def start(self) -> Session:
        self._session = self.__session_factory()
        try:
            yield self
            self._session.commit()
        except:
            self._session.rollback()
            raise
        finally:
            self._session.close()

    @property
    def auth_repository(self) -> AuthRepository:
        return AuthRepository(self._session)


class IsDBUnitOfWork:
    __session_factory = None

    def __init__(self, db_config: PostgresConfig):

        if self.__session_factory is None:
            self.__session_factory = sessionmaker(
                autoflush=True, bind=db_config.engine
            )

    @contextmanager
    def start(self) -> Session:
        self._session = self.__session_factory()
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
