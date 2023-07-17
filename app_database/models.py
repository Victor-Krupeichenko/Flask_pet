from sqlalchemy import Column, Integer, ForeignKey, String, Text, Boolean, TIMESTAMP
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy_utils.types import ChoiceType
from datetime import datetime
from passlib.hash import pbkdf2_sha256
from flask_login import UserMixin

Base = declarative_base()


class User(Base, UserMixin):
    """Model user"""
    GROUP_USERS = (
        ("admin", "ADMIN"),
        ("client", "CLIENT")
    )
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True, nullable=False)
    password = Column(Text, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    active = Column(Boolean, default=True)
    group = Column(ChoiceType(choices=GROUP_USERS), default="client")
    post = relationship("Post", backref="author", cascade="all, delete")

    @property
    def password_hash(self):
        """Password"""
        return self.password_hash

    @password_hash.setter
    def password_hash(self, form_password):
        """Hash Password"""
        self.password = pbkdf2_sha256.hash(form_password)

    def check_password(self, form_password):
        """Verify Password"""
        return pbkdf2_sha256.verify(form_password, self.password)


class Post(Base):
    """Model Post"""
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    title = Column(String(40), nullable=False)
    content = Column(Text, nullable=False)
    date_create = Column(TIMESTAMP, default=datetime.utcnow)
    publish = Column(Boolean, default=True)
    author_id = Column(Integer, ForeignKey("user.id"))
    category_id = Column(Integer, ForeignKey("category.id"))


class Category(Base):
    """Model Category"""
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    title = Column(String(25), nullable=False, unique=True)
    post = relationship("Post", backref="category_title", cascade="all, delete")
