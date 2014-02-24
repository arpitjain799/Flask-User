from flask import Flask, render_template_string
from flask.ext.babel import Babel
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.user import UserManager, UserMixin, SQLAlchemyAdapter

# Setup Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'my-super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///minimal_app.db'

# Setup Flask-Babel and Flask-SQLAlchemy
app.babel = Babel(app)
db = SQLAlchemy(app)

# Define User model. Make sure to add flask.ext.user UserMixin!!
class User(db.Model, UserMixin):
    # Required fields for Flask-Login
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean(), nullable=False, default=False)
    # Required fields for Flask-User
    email = db.Column(db.String(255), nullable=True, unique=True)
    password = db.Column(db.String(255), nullable=False, default='')
    # Optional fields for Flask-User (depends on app config settings)
    username = db.Column(db.String(50), nullable=True, unique=True)
    email_confirmed_at = db.Column(db.DateTime())
    reset_password_token = db.Column(db.String(100), nullable=False, default='')

# Create all database tables
db.create_all()

# Setup Flask-User
db_adapter = SQLAlchemyAdapter(db,  User)       # Select database adapter
user_manager = UserManager(db_adapter, app)     # Init Flask-User and bind to app

# Home page
@app.route('/')
def home():
    return render_template_string(
        """
        {% extends "base.html" %}

        {% block content %}
            {% if not current_user.is_authenticated() %}
                <p>{%trans%}Hello Visitor,{%endtrans%}</p>
                <p><a href="{{ url_for('user.login') }}">{%trans%}Sign in{%endtrans%}</a></p>
                <p><a href="{{ url_for('user.register') }}">{%trans%}Register{%endtrans%}</a></p>
            {% else %}
                <p>{%trans%}Hello{%endtrans%} {{ current_user.username or current_user.email }},</p>
                <p><a href="{{ url_for('user.change_password') }}">{%trans%}Change password{%endtrans%}</a></p>
                <p><a href="{{ url_for('user.logout') }}">{%trans%}Sign out{%endtrans%}</a></p>
            {% endif %}
        {% endblock %}
        """)

# Start development web server
app.run(host='0.0.0.0', port=5000, debug=True)
