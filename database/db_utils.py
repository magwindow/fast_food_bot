from sqlalchemy.orm import Session

from database.engine import engine


with Session(engine) as session:
    db_session = session