import os
from flask_login import LoginManager
from flask import Flask, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Initialisiert eine Instanz von SQLAlchemy. Dies wird für die Datenbankoperationen verwendet.
db_instance = SQLAlchemy()

# Bestimmt den absoluten Pfad des Verzeichnisses, in dem sich diese Datei befindet. 
# Wird verwendet, um relative Pfadangaben zu vermeiden.
basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)

def create_app():
    # Erstellt eine Instanz der Flask-Anwendung.
    app_main = Flask(__name__)
    # Setzt einen geheimen Schlüssel für die Anwendung, der für die Sicherheit bei Formularübertragungen etc. wichtig ist.
    app_main.config['SECRET_KEY'] = 'your_secret_key_here'  # Change this to a random secret key
    # Konfiguriert den Pfad zur Datenbankdatei. Hier wird SQLite verwendet und die Datenbank heißt 'tasks.db'.
    app_main.config['SQLALCHEMY_DATABASE_URI'] =  'sqlite:///' + os.path.join(basedir, 'tasks.db')  # Database file will be created in the project folder
    # Initialisiert die Datenbankinstanz mit der Flask-Anwendung.
    db_instance.init_app(app_main)
    
    # Initialisiert den LoginManager, der für die Benutzerauthentifizierung zuständig ist.
    login_manager = LoginManager()
    # Definiert die Ansicht (View), die für nicht authentifizierte Benutzer geladen wird.
    login_manager.login_view = 'login'
    # Initialisiert den LoginManager mit der Flask-Anwendung.
    login_manager.init_app(app_main)
    
    # Importiert das User-Modell aus der Datenbankkonfigurationsdatei.
    from .db import User
    
    # Eine Funktion, die vom LoginManager verwendet wird, um Benutzerobjekte anhand ihrer ID zu laden.
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Eine Funktion, die aufgerufen wird, wenn ein nicht authentifizierter Benutzer auf eine geschützte Route zugreifen möchte.
    @login_manager.unauthorized_handler
    def unauthorized():
        flash('Sie müssen eingeloggt sein, um auf diese Seite zugreifen zu können.', 'danger')
        return redirect(url_for('app.login'))
    
    # Importiert und registriert die Blueprint-Instanz aus der Ansichtsmoduldatei.
    from taskmanager.view import app
    app_main.register_blueprint(app)
    
    # Erstellt alle Datenbanktabellen, die noch nicht existieren, im Kontext der Anwendung.
    with app_main.app_context():
        db_instance.create_all()
    
    # Gibt die konfigurierte Flask-Anwendung zurück.
    return app_main