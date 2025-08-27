import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

load_dotenv()

from database.models import Base, Categories, Products

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_ADDRESS = os.getenv('DB_ADDRESS')
DB_NAME = os.getenv('DB_NAME')

engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_ADDRESS}/{DB_NAME}', echo=True)


def main():
    Base.metadata.create_all(engine)

    categories = ('Лаваши', 'Донары', 'Хот-доги', 'Десерты', 'Соусы')
    products = (
        (1, 'Мини Лаваш', 20000, 'Мясо, тесто, помидоры', 'media/lavash/lavash1.jpg'),
        (1, 'Мини Говяжий', 22000, 'Мясо, тесто, помидоры', 'media/lavash/lavash2.jpg'),
        (1, 'Мини с сыром', 24000, 'Мясо, тесто, помидоры', 'media/lavash/lavash3.jpg'),
        (2, 'Гамбургер', 24000, 'Мясо, тесто, помидоры', 'media/doner/doner1.jpg'),
        (2, 'Дамбургер', 24000, 'Мясо, тесто, помидоры', 'media/doner/doner2.jpg'),
        (2, 'Чизбургер', 24000, 'Мясо, тесто, помидоры', 'media/doner/doner3.jpg')
    )
    with Session(engine) as session:

        for category in categories:
            session.add(Categories(category_name=category))
            session.commit()

        for product in products:
            session.add(Products(category_id=product[0], product_name=product[1], price=product[2],
                                 description=product[3], image=product[4]))
            session.commit()


if __name__ == '__main__':
    main()
