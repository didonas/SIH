from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import models

engine = create_engine('sqlite:///sql_app.db')
Session = sessionmaker(bind=engine)
db = Session()

alert = db.query(models.Alert).first()
if alert:
    print(alert.evidence)
