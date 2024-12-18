from database.db_core import AuthDBUnitOfWork


async def check_phone_number(phone_num: str) -> bool:

    uow = AuthDBUnitOfWork()
    with uow.start() as session:
        exists: bool = await session.auth_repository.check_if_exists(
            phone_num,
        )

    return exists
