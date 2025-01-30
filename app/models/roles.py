from sqlalchemy import Column, Integer, String

from app.core.database import Base


class RolePrivilege:
    ADMIN = 1
    EDITOR = 2
    SUPPORT = 3
    VIEWER = 4
    DEVELOPER = 5


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
