from sqlalchemy import DateTime, func, String, BigInteger, ForeignKey, DECIMAL, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Users(Base):
    """База пользователей"""
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    telegram: Mapped[int] = mapped_column(BigInteger, unique=True)  # unique=True - только уникальный id telegram
    phone: Mapped[str] = mapped_column(String(30), nullable=True)  # nullable=True - это поле может быть пустым

    carts: Mapped[int] = relationship('Carts', back_populates='user_cart')

    def __str__(self):
        return self.name


class Carts(Base):
    """Временная корзина пользователей"""
    __tablename__ = 'carts'

    id: Mapped[int] = mapped_column(primary_key=True)
    # DECIMAL(12, 2) - Цена может быть: 123456789012,00, default=0 - по умолчанию 0
    total_price: Mapped[int] = mapped_column(DECIMAL(12, 2), default=0)
    total_products: Mapped[int] = mapped_column(default=0)  # default=0 - кол-во продуктов в корзине по умолчанию 0
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True)

    user_cart: Mapped[Users] = relationship(back_populates='carts')
    finally_id: Mapped[int] = relationship('FinallyCarts', back_populates='user_cart')

    def __str__(self):
        return str(self.id)


class FinallyCarts(Base):
    """Окончательная корзина пользователей"""
    __tablename__ = 'finally_carts'

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(50))
    final_price: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2))
    quantity: Mapped[int]

    cart_id: Mapped[int] = mapped_column(ForeignKey('carts.id'))
    user_cart: Mapped[Carts] = relationship(back_populates='finally_id')

    # В поле product_name должен быть только уникальный продукт,
    # при добавлении несколько одного и того же продукта будет увеличиваться quantity
    __table_args__ = (UniqueConstraint('cart_id', 'product_name'),)

    def __str__(self):
        return str(self.id)


class Categories(Base):
    """Категории продуктов"""
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    category_name: Mapped[str] = mapped_column(String(20), unique=True)

    products = relationship('Products', back_populates='product_category')

    def __str__(self):
        return self.category_name


class Products(Base):
    """Продукты"""
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(20), unique=True)
    description: Mapped[str]
    image: Mapped[str] = mapped_column(String(100))
    price: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))

    product_category: Mapped[Categories] = relationship(back_populates='products')
