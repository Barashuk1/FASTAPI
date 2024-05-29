from sqlalchemy import (
    Table, Column, String, Integer, ForeignKey, func, UniqueConstraint
)
from sqlalchemy.orm import (
    Mapped, mapped_column, relationship, declarative_base
)
from datetime import datetime

from photoshare_src.database.db import engine

Base = declarative_base()

image_m2m_tag = Table(
    "image_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("image_id", Integer, ForeignKey("images.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)

image_m2m_user = Table(
    'image_m2m_user',
    Base.metadata,
    Column('image_id', Integer, ForeignKey('images.id')),
    Column('user_id_like', Integer, ForeignKey('users.id'), nullable=True),
    Column('user_id_dislike', Integer, ForeignKey('users.id'), nullable=True),
    UniqueConstraint('image_id', 'user_id_like', name='unique_like'),
    UniqueConstraint('image_id', 'user_id_dislike', name='unique_dislike'),
    UniqueConstraint(
        'image_id', 'user_id_like', 'user_id_dislike',
        name='unique_like_dislike'
    )
)



class Image(Base):
    """
    Model for images table

    :param id: int: Image id
    :param url: str: Image url in Cloudinary
    :param description: str: Image description
    :param tags: List[Tag]: Image tags
    :param comments: List[Comment]: Image comments
    :param rate: float: Image rate
    :param url_view: str: Edited image view url
    :param qr_code_view: str: Edited image QR code view url
    :param created_at: datetime: Image creation date
    :param user_id: int: User id
    :param user: User: User object
    """
    __tablename__ = "images"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    tags = relationship("Tag", secondary=image_m2m_tag, backref="images")
    comments = relationship('Comment', backref='images')
    _likes = relationship(
        'User', secondary=image_m2m_user,
        primaryjoin='Image.id == image_m2m_user.c.image_id',
        secondaryjoin='User.id == image_m2m_user.c.user_id_like',
        foreign_keys='[image_m2m_user.c.image_id, image_m2m_user.c.user_id_like]',
        backref='liked_images',
        overlaps="disliked_images,dislikes,_dislikes"
    )
    _dislikes = relationship(
        'User', secondary=image_m2m_user,
        primaryjoin='Image.id == image_m2m_user.c.image_id',
        secondaryjoin='User.id == image_m2m_user.c.user_id_dislike',
        foreign_keys='[image_m2m_user.c.image_id, image_m2m_user.c.user_id_dislike]',
        backref='disliked_images',
        overlaps="liked_images,likes,_likes"
    )
    rate: Mapped[float] = mapped_column(default=0.0)
    url_view: Mapped[str | None] = mapped_column(String(255), default=None)
    qr_code_view: Mapped[str | None] = mapped_column(String(255), default=None)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )
    user = relationship('User', backref="images")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._likes = []
        self._dislikes = []

    @property
    def likes(self):
        """int: The number of likes for the image"""
        return len(self._likes)

    @property
    def dislikes(self):
        """int: The number of dislikes for the image"""
        return len(self._dislikes)

    def update_like(self, user, operation):
        """
        Method for updating likes for the image

        :param user: User: User object
        :param operation: str: Operation type ('add' or 'remove')
        :return: None
        """
        if operation == 'add':
            # Перевірка чи користувач не ставив вже лайк на картинку
            if user not in self._likes:
                # Якщо користувач вже ставив дизлайк, то видаляємо його
                if user in self._dislikes:
                    self._dislikes.remove(user)
                # Додаємо користувача до списку лайків
                self._likes.append(user)
                self.update_rate()
        elif operation == 'remove':
            if user in self._likes:
                self._likes.remove(user)
                self.update_rate()

    def update_dislike(self, user, operation):
        """
        Method for updating dislikes for the image

        :param user: User: User object
        :param operation: str: Operation type ('add' or 'remove')
        :return: None
        """
        if operation == 'add':
            if user not in self._dislikes:
                if user in self._likes:
                    self._likes.remove(user)
                self._dislikes.append(user)
                self.update_rate()
        elif operation == 'remove':
            self._dislikes.remove(user)
            self.update_rate()

    # Автоматично оновлює рейтинг коли змінюється кількість лайків або
    # дизлайків через методи update_like та update_dislike
    def update_rate(self):
        """Method for updating image rate"""
        total_amount = self.likes + self.dislikes

        if total_amount == 0:
            self.rate =  0.0
        else:
            self.rate = round((self.likes / total_amount) * 100, 1)


class Tag(Base):
    """
    Method for creating a tag model

    :param id: int: Tag id
    :param name: str: Tag name
    """
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)



class Comment(Base):
    """
    Method for creating a comment model

    :param id: int: Comment id
    :param text: str: Comment text
    :param created_at: datetime: Comment creation date
    :param updated_at: datetime: Comment update date
    :param image_id: int: Image id
    :param user_id: int: User id
    :param user: User: User object
    """
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now())
    image_id: Mapped[int] = mapped_column(
        ForeignKey('images.id', ondelete='CASCADE')
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )
    user = relationship('User', backref='comments')


class User(Base):
    """
    Model for users table

    :param id: int: User id
    :param username: str: User username
    :param email: str: User email
    :param password: str: User password
    :param role: str: User role
    :param created_at: datetime: User creation date
    :param is_active: bool: User active status
    :param refresh_token: str: User refresh token, nullable
    """
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True)
    password: Mapped[str]
    role: Mapped[str] = mapped_column(default='user')
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    is_active: Mapped[bool] = mapped_column(default=True)
    refresh_token: Mapped[str | None]

# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)




# from photoshare.database.db import test_session

# user1 = User(
#     username='user1',
#     email='dffdfdf@fdf.dfpdf',
#     password='password1',
#     role='user'
# )

# image1 = Image(
#     url='https://www.example.com/image1.jpg',
#     description='Image 1 description',
#     user_id=1
# )
# image2 = Image(
#     url='https://www.example.com/image2.jpg',
#     description='Image 2 description',
#     user_id=1
# )

# image1.update_like(user1, 'add')
# image2.update_dislike(user1, 'add')

# test_session.add(user1)
# test_session.commit()
# test_session.add_all([image1, image2])
# test_session.commit()

"""
from photoshare.database.db import test_session

user1 = User(
    username='user1',
    email='dffdfdf@fdf.dfpdf',
    password='password1',
    role='user'
)
user2 = User(
    username='user2',
    email='dsadasdas@dsa.cs',
    password='password2',
    role='moderator'
)

image1 = Image(
    url='https://www.example.com/image1.jpg',
    description='Image 1 description',
    user_id=1
)
image2 = Image(
    url='https://www.example.com/image2.jpg',
    description='Image 2 description',
    user_id=2
)

Tag1 = Tag(name='Tag1')
Tag2 = Tag(name='Tag2')


comment11 = Comment(
    text='Comment 1',
    user_id=1,
    image_id=1
)
comment12 = Comment(
    text='Comment 2',
    user_id=2,
    image_id=1
)
comment22 = Comment(
    text='Comment 2',
    user_id=2,
    image_id=2
)
comment21 = Comment(
    text='Comment 1',
    user_id=1,
    image_id=2
)

test_session.add_all([user1, user2, image1, image2, Tag1, Tag2, comment11, comment12, comment21, comment22])
test_session.commit()

print(f'User1 id: {user1.id}')
print(f'User2 id: {user2.id}')
print(f'Image1 id: {image1.id}')
print(f'Image2 id: {image2.id}')
print(f'Tag1 id: {Tag1.id}')
print(f'Tag2 id: {Tag2.id}')
print(f'Comment11 id: {comment11.id}')
print(f'Comment12 id: {comment12.id}')
print(f'Comment21 id: {comment21.id}')
print(f'Comment22 id: {comment22.id}')
print(f'User1 images: {user1.images}')
print(f'User2 images: {user2.images}')
print(f'Image1 comments: {image1.comments}')
print(f'Image2 comments: {image2.comments}')
print(f'Comment11 image: {comment11.image}')
print(f'Comment12 image: {comment12.image}')
print(f'Comment21 image: {comment21.image}')
print(f'Comment22 image: {comment22.image}')
print(f'Comment11 user: {comment11.user}')
print(f'Comment12 user: {comment12.user}')
print(f'Comment21 user: {comment21.user}')
print(f'Comment22 user: {comment22.user}')

image1.tags.append(Tag1)
image1.tags.append(Tag2)
image2.tags.append(Tag1)

test_session.commit()

print(f'Image1 user: {image1.user}')
print(f'Image2 user: {image2.user}')
print(f'Image1 tags: {image1.tags}')
print(f'Image2 tags: {image2.tags}')

image1.update_like(user1, 'add')
image1.update_like(user2, 'add')
image2.update_dislike(user1, 'add')
image2.update_like(user2, 'add')

test_session.commit()

print(f'Image1 rate: {image1.rate}')
print(f'Image2 rate: {image2.rate}')

image2.update_like(user1, 'add')

print(f'Image1 rate: {image2.likes}')
print(f'Image2 rate: {image2.rate}')

test_session.close()
"""