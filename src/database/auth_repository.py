from sqlalchemy.orm import Session

from database.models import Users


class AuthRepository:

    def __init__(self, session: Session):
        self.session = session

    def check_if_exists(self, phone_number: str) -> bool:
        user: Users = (
            self.session.query(Users)
            .filter_by(phone_number=phone_number)
            .first()
        )
        if user is None:
            return None

        print(user.is_active)
        return user.is_active