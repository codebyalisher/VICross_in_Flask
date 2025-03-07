import click
from flask_migrate import Migrate
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
migrate = Migrate()

def init_app(app):
    """Initialize the app with database and migration setup."""
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI']    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
    
    db.init_app(app)
    migrate.init_app(app, db)    
    app.cli.add_command(init_db_command)
    
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    with current_app.app_context():
        db.create_all()  
    click.echo('Initialized the database.')

#flask --app AdminDashboard init-db
# flask --app AdminDashboard db init for makemigrations which creates a migrations folder
#flask --app AdminDashboard db migrate -m "Increase password_hash length"
#flask --app AdminDashboard db upgrade
#flask --app AdminDashboard run --debugger --reload

