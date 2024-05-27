from app import app, db
from models import User, TaxRecord

with app.app_context():
    db.create_all()
