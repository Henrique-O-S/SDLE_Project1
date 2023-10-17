from flask import Flask
from models import db
from routes import routes
import os

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

DATABASE = os.path.join(PROJECT_ROOT, 'database', 'shopping_list.db')

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.register_blueprint(routes)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE  # Use SQLite in the 'database' folder
db.init_app(app)

# Create the database tables
with app.app_context():
    db.create_all()  # create models not yet created

if __name__ == '__main__':
    app.run()
