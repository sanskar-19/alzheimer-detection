from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, DateTime, Boolean
from ..database import Base


class UserModel(Base):
    __tablename__ = "users"

    uid = Column(String(100), unique=True)
    first_name = Column(String(20))
    last_name = Column(String(20))
    email = Column(String(40), primary_key=True, unique=True)
    role = Column(String(10))
    hashed_password = Column(String(256))
    created_at = Column(DateTime)
    otp = Column(String(6))
    otp_expiry_at = Column(DateTime)
    status = Column(Boolean, default=False)

    class Meta:
        db_table = "users"

    # def __init__(self):
    #     self.uid = uid
    #     self.first_name = first_name


# class UnConfirmedUserModel(Base):
