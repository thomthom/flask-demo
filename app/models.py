from flask_login import UserMixin
from sqlalchemy import String
from sqlalchemy.orm import (DeclarativeBase, Mapped, MappedAsDataclass, declarative_mixin,
                            declared_attr, mapped_column)
from typing_extensions import Annotated

# https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#native-support-for-dataclasses-mapped-as-orm-models


@declarative_mixin
class Base(DeclarativeBase, MappedAsDataclass):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


id_primary_key = Annotated[int, mapped_column(primary_key=True)]
str100 = Annotated[str, mapped_column(String(100))]


class User(UserMixin, Base):
    id: Mapped[id_primary_key] = mapped_column(init=False)
    email: Mapped[str100] = mapped_column(unique=True, nullable=False)
    password: Mapped[str100] = mapped_column(nullable=False)
    name: Mapped[str100] = mapped_column(nullable=False)

    def __repr__(self):
        return f"<User(id={self.id} email='{self.email}' name='{self.name}')>"
