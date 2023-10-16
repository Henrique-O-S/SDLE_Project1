from flask import Flask, render_template
from models import db

app = Flask(__name__)
# app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/shopping_list.db'  # Use SQLite in the 'database' folder
db.init_app(app)

# Import and register the routes Blueprint
from routes import routes
app.register_blueprint(routes)

if __name__ == '__main__':
    app.run()
