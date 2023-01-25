from app import db
from app import init_app


app = init_app()
app.config.from_object('config.Development')
with app.app_context():
    db.create_all()
