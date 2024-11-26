from sqlalchemy import Connection, Engine, create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager


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
        self.__engine = create_engine(self.__url)

    @property
    def engine(self) -> Engine:
        return self.__engine

    def start_connection(self) -> None:
        self.__connection: Connection = self.__engine.connect()

    def stop_connection(self) -> None:
        self.__connection.close()


class UnitOfWork:
    def __init__(self, db_config: PostgresConfig):
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