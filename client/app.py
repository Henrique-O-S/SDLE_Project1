from flask import Flask
from models import db
from routes import routes
import os
import socket
from sqlalchemy import text

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(PROJECT_ROOT, 'database', 'shopping_list.db')

# Function to find an available port
def find_available_port(start_port, max_attempts=10):
    for _ in range(max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", start_port))
                return start_port
        except OSError:
            start_port += 1
    raise Exception("No available ports found")

# Create a function to create and configure your Flask app
def create_app():
    port = find_available_port(5000)  # Start at port 5000 and find an available port
    app = Flask(__name__)
    app.secret_key = 'your_secret_key_here'
    app.register_blueprint(routes)
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE
    db.init_app(app)
    return app, port

# Create and run your app on an available port
if __name__ == '__main__':
    app, port = create_app()
    print(f"Starting app on port {port}")
    app.run(port=port)
