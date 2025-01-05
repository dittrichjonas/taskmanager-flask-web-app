from enum import Enum
from flask_login import UserMixin
from . import db_instance as db

# Definiert eine Enumeration für Benutzerrollen mit zwei Rollen: ADMIN und USER.
class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"

# Eine Hilfstabelle für die Many-to-Many-Beziehung zwischen Task- und User-Modellen.
task_identifier = db.Table("task_identifier",
                             db.Column('task_id', db.Integer, db.ForeignKey('tasks.id')),
                             db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
                            )

# Das Task-Modell definiert die Struktur für Aufgaben in der Datenbank.
class Task(db.Model):
    __tablename__ = "tasks"  # Der Tabellenname in der Datenbank.
    id = db.Column(db.Integer, primary_key=True)  # Eindeutige ID für jede Aufgabe.
    title = db.Column(db.String(100), nullable=False)  # Der Titel der Aufgabe.
    description = db.Column(db.Text, nullable=True)  # Eine optionale Beschreibung.
    due_date = db.Column(db.DateTime, nullable=True)  # Ein optionales Fälligkeitsdatum.
    completed = db.Column(db.Boolean, default=False)  # Status, ob die Aufgabe abgeschlossen ist.
    # Beziehungsfeld für die Zuordnung von Benutzern zu Aufgaben. Implementiert eine Many-to-Many-Beziehung.
    users_assign = db.relationship("User", secondary="task_identifier", back_populates="tasks_assign", lazy=True)

# Das TaskPoints-Modell definiert eine Struktur für Punkte oder Teilaufgaben einer Hauptaufgabe.
class TaskPoints(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Eindeutige ID für jeden Punkt.
    text = db.Column(db.Text, nullable=True)  # Der Text des Punktes.
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)  # Fremdschlüssel zur Task-Tabelle.

# Das User-Modell definiert die Struktur für Benutzer in der Datenbank.
class User(db.Model, UserMixin):
    __tablename__ = "users"  # Der Tabellenname in der Datenbank.
    id = db.Column(db.Integer, primary_key=True)  # Eindeutige ID für jeden Benutzer.
    username = db.Column(db.String(50), unique=True, nullable=False)  # Eindeutiger Benutzername.
    password = db.Column(db.String(100), nullable=False)  # Passwort des Benutzers.
    role = db.Column(db.Enum(UserRole))  # Die Rolle des Benutzers, basierend auf der UserRole Enum.
    # Beziehungsfeld für die Zuordnung von Aufgaben zu Benutzern. Implementiert eine Many-to-Many-Beziehung.
    tasks_assign = db.relationship("Task", secondary="task_identifier", back_populates="users_assign", lazy=True)