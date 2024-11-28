from database.models import Users


class UserDto:

    def __init__(self, user: Users):
        self.__phone_number = user.phone_number
        self.__is_active = user.is_active

    @property
    def phone_number(self) -> int:
        return self.__phone_number

    @property
    def is_active(self) -> str:
        return self.__is_active
