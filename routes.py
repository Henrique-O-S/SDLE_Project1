from flask import Blueprint, render_template

# Create a Flask Blueprint
routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
    return render_template('index.html')

@routes.route('/about')
def about():
    return "About Page"
