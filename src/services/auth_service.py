from database.db_core import UnitOfWork

from config import AUTH_DB_USER, AUTH_DB_PASSWORD, AUTH_DB_DOMAIN, AUTH_DB_PORT, AUTH_DB_NAME
from database.db_core import PostgresConfig
from database.user_dto import UserDto


async def check_phone_number(phone_num) -> bool:
    config = PostgresConfig(
        user_name=AUTH_DB_USER,
        password=AUTH_DB_PASSWORD,
        domain=AUTH_DB_DOMAIN,
        port=AUTH_DB_PORT,
        db_name=AUTH_DB_NAME,
    )

    config.create_engine()
    uow = UnitOfWork(config)
    with uow.start() as session:
        exists: bool = (
            session.auth_repository.check_if_exists(
                phone_num,
            )
        )

    return exists
