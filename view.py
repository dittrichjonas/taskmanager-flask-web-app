
# from config import login_manager
# from db import db, User, UserRole, Task, TaskPoints
from .db import User, UserRole, Task, TaskPoints
from . import db_instance as db
from flask_login import login_user, login_required, logout_user, current_user
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask import redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import or_


app = Blueprint('app',__name__)


# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))


# @login_manager.unauthorized_handler
# def unauthorized():
#     flash('Sie müssen eingeloggt sein, um auf diese Seite zugreifen zu können.', 'danger')
#     return redirect(url_for('app.login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Erfolgreich ausgeloggt.', 'success')
    return redirect(url_for('app.login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Der Benutzername existiert bereits. Bitte wählen Sie einen anderen Benutzernamen.', 'danger')
            return redirect(url_for('app.register'))

        new_user = User(username=username, password=generate_password_hash(password), role=UserRole.ADMIN)
        db.session.add(new_user)
        db.session.commit()

        flash('Registrierung erfolgreich. Sie können sich jetzt anmelden.', 'success')
        return redirect(url_for('app.login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Erfolgreich eingeloggt!', 'success')
            return redirect(url_for('app.dashboard'))
        else:
            flash('Ungültiger Benutzername oder Passwort. Bitte versuchen Sie es erneut.', 'danger')

    return render_template('login.html')



# User View

# @app.route('/add_task', methods=['GET', 'POST'])
# @login_required
# def add_task():
#     if request.method == 'POST':
#         title = request.form['title']
#         description = request.form['description']
#         due_date = datetime.strptime(request.form['due_date'],"%Y-%M-%d")
        

#         new_task = Task(title=title, description=description, due_date=due_date, user_id=current_user.id)
#         db.session.add(new_task)
#         db.session.commit()

#         flash('Aufgabe erfolgreich hinzugefügt!', 'success')
#         return redirect(url_for('app.dashboard'))

#     return render_template('user/add_task.html')

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    if current_user.role!=UserRole.ADMIN:
        flash('Sie sind nicht berechtigt, diese Aufgabe zu bearbeiten.', 'danger')
        return redirect(url_for('app.dashboard'))

    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        task.due_date = datetime.strptime(request.form['due_date'],"%Y-%M-%d")
        

        db.session.commit()

        flash('Aufgabe erfolgreich aktualisiert!', 'success')
        return redirect(url_for('app.home'))

    return render_template('admin/edit_task.html', task=task)

@app.route('/assign_task/<int:task_id>', methods=['POST'])
@login_required
def assign_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # task.user_id = current_user.id

    task.users_assign.append(current_user)


    db.session.commit()

    flash('Aufgabe erfolgreich zugewiesen!', 'success')
    return redirect(url_for('app.dashboard'))

@app.route('/assign/task_point/<int:task_id>', methods=['POST'])
@login_required
def add_task_point(task_id):
    task = Task.query.get_or_404(task_id)
    if current_user.role == UserRole.ADMIN or current_user in task.users_assign :
        task_point_text = request.form['text']
        new_task_point = TaskPoints(text=task_point_text,task_id=task_id)
        db.session.add(new_task_point)
        db.session.commit()
        flash('Aufgabenpunkt erfolgreich hinzugefügt!', 'success')
        return redirect(url_for('app.dashboard'))

@app.route('/delete/task_point/<int:task_point_id>', methods=['POST'])
@login_required
def delete_task_point(task_point_id):
    task_point = TaskPoints.query.get_or_404(task_point_id)
    task = Task.query.get(task_point.task_id)
    if current_user not in task.users_assign  and current_user.role!=UserRole.ADMIN:
        flash('Sie sind nicht berechtigt, diesen Aufgabenpunkt zu löschen.', 'danger')
        return redirect(url_for('app.dashboard'))

    db.session.delete(task_point)
    db.session.commit()

    flash('Aufgabe erfolgreich gelöscht!', 'success')
    return redirect(url_for('app.dashboard'))

# @app.route('/delete_task/<int:task_id>', methods=['POST'])
# @login_required
# def delete_task(task_id):
#     task = Task.query.get_or_404(task_id)

#     if task.user_id != current_user.id:
#         flash('ie sind nicht berechtigt, diesen Aufgabenpunkt zu löschen.', 'danger')
#         return redirect(url_for('app.dashboard'))

#     db.session.delete(task)
#     db.session.commit()

#     flash('Aufgabe erfolgreich gelöscht!', 'success')
#     return redirect(url_for('app.dashboard'))

@app.route('/unassign/task_point/<int:task_id>', methods=['POST'])
@login_required
def unclaim_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    task.users_assign.remove(current_user)

    db.session.commit()

    flash('Aufgabe nicht zugewiesen erfolgreich!', 'success')
    return redirect(url_for('app.dashboard'))
    # app.py (continued from Step 6)





# Admin View

@app.route("/add_users", methods=['GET','POST'])
@login_required
def add_users():
    if current_user.role == UserRole.USER:
        flash('Sie sind nicht berechtigt', 'danger')
        return redirect(url_for('app.home'))

    if request.method == "POST":
        if current_user.role == UserRole.ADMIN:
            username = request.form['username']
            password = request.form['password']
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Der Benutzername existiert bereits. Bitte wählen Sie einen anderen Benutzernamen.', 'danger')
                return redirect(url_for('app.add_users'))

            new_user = User(username=username, password=generate_password_hash(password), role=UserRole.USER)
            db.session.add(new_user)
            db.session.commit()
            flash('Benutzer erfolgreich angelegt', 'success')
            
    return render_template('admin/create_user.html')








@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == UserRole.ADMIN:
        tasks = Task.query.all()
        users = User.query.filter_by(role=UserRole.USER).all()
        return render_template('/admin/admin_home.html', tasks=tasks, users=users)
    else:
        tasks_to_select = Task.query.filter(~Task.users_assign.any(User.id==current_user.id))
        taken_tasks = current_user.tasks_assign
        taken_tasks_context = []
        for task in taken_tasks:
            taken_tasks_context.append({"task":task,'task_list':TaskPoints.query.filter_by(task_id=task.id).all()})
        return render_template('user/student_dashboard.html',tasks=taken_tasks_context, tasks_to_select = tasks_to_select)

@app.route('/todo-list')
@login_required
def admin_todo():
    if current_user.role == UserRole.ADMIN:
        tasks = Task.query.all()
        return render_template('admin/admin_todo_list.html', tasks=tasks)


@app.route('/todo-list/task/<int:task_id>')
@login_required
def admin_task_view(task_id):
    task = Task.query.get_or_404(task_id)
    print(task.users_assign)
    if current_user.role == UserRole.ADMIN:
    
        task_points = TaskPoints.query.filter_by(task_id=task.id).all()

        return render_template('admin/admin_todo_task.html', task=task, task_points=task_points)

@app.route('/todo-list/add/task', methods=['GET','POST'])
@login_required
def admin_task_add():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_date = datetime.strptime(request.form['due_date'],"%Y-%M-%d")
        

        new_task = Task(title=title, description=description, due_date=due_date)
        db.session.add(new_task)
        db.session.commit()

        flash('Aufgabe erfolgreich hinzugefügt!', 'success')
        return redirect(url_for('app.admin_todo'))

    return render_template('admin/add_task_admin.html',redirect=redirect)


@app.route('/todo-list/edit/task/<int:task_id>', methods=['GET','POST'])
@login_required
def admin_task_edit(task_id):
    task = Task.query.get_or_404(task_id)
    if current_user.role!=UserRole.ADMIN:
        flash('Sie sind nicht berechtigt, diese Aufgabe zu bearbeiten.', 'danger')
        return redirect(url_for('app.home'))

    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        task.due_date = datetime.strptime(request.form['due_date'],"%Y-%M-%d")
        

        db.session.commit()

        flash('Aufgabe erfolgreich aktualisiert!', 'success')
        return redirect(url_for('app.admin_todo'))

    return render_template('admin/edit_task_admin.html', task=task, redirect=redirect)

@app.route('/todo-list/delete/task/<int:task_id>', methods=['POST'])
@login_required
def admin_task_delete(task_id):
    task = Task.query.get_or_404(task_id)

    if current_user.role!=UserRole.ADMIN:
        flash('Sie sind nicht berechtigt, diese Aufgabe zu löschen.', 'danger')
        return redirect(url_for('app.admin_todo'))
    task_points = TaskPoints.query.filter_by(task_id=task.id).delete()
    db.session.delete(task)
    db.session.commit()

    flash('Aufgabe erfolgreich gelöscht!', 'success')
    return redirect(url_for('app.admin_todo'))

@app.route('/todo-list/task/add/<int:task_id>', methods=['POST'])
@login_required
def admin_task_point_add(task_id):
    task = Task.query.get_or_404(task_id)
    if current_user.role == UserRole.ADMIN:
        task_point_text = request.form['text']
        new_task_point = TaskPoints(text=task_point_text,task_id=task_id)
        db.session.add(new_task_point)
        db.session.commit()
        flash('Aufgabenpunkt erfolgreich hinzugefügt!', 'success')
        return redirect(url_for('app.admin_task_view',task_id=task_id))
    else:
        flash('Sie sind nicht berechtigt, diese Aufgabe zu ergänzen.', 'danger')
        return redirect(url_for('app.home'))

@app.route('/todo-list/task/delete/<int:task_id>/<int:task_point_id>', methods=['POST'])
@login_required
def admin_task_point_delete(task_id,task_point_id):
    task_point = TaskPoints.query.get_or_404(task_point_id)
    task = Task.query.get(task_point.task_id)
    if  current_user.role!=UserRole.ADMIN:
        flash('Sie sind nicht berechtigt, diesen Aufgabenpunkt zu löschen.', 'danger')
        return redirect(url_for('app.admin_task_view',task_id=task_id))

    db.session.delete(task_point)
    db.session.commit()

    flash('Aufgabe erfolgreich gelöscht!', 'success')
    return redirect(url_for('app.admin_task_view',task_id=task_id))


@app.route('/admin/user/dashboard')
@login_required
def admin_user_dashboard():
      if current_user.role == UserRole.ADMIN:
          users = User.query.filter_by(role=UserRole.USER).all()
          return render_template('admin/admin_user.html', users=users)


@app.route('/admin/user/update', methods=['GET','POST'])
@login_required
def admin_update_self():
    if request.method == "POST":
        if current_user.role == UserRole.ADMIN:
                
                username = request.form['username']
                password = request.form['password']
                
                user = current_user
                if username != '':
                    
                    
                    existing_user = User.query.filter_by(username=username).first()
                    if existing_user:
                        flash('Der Benutzername existiert bereits. Bitte wählen Sie einen anderen Benutzernamen.', 'danger')
                        return redirect(url_for('app.admin_update_self'))
                    user.username = username
                if password != '':
                    
                    user.password = generate_password_hash(password=password)
                

                db.session.commit()
                flash('Benutzer erfolgreich aktualisiert', 'success')
                return redirect(url_for('app.home'))
                
        else:
            flash('Sie sind nicht berechtigt', 'danger')
            return redirect(url_for('app.home'))
    
    
    return render_template('admin/edit_user_admin.html',username=current_user.username)

@app.route('/admin/student/update/<int:id>', methods=['GET','POST'])
@login_required
def update_student_creds(id):
    if current_user.role == UserRole.ADMIN:
        user = User.query.get_or_404(id)
        if request.method == "POST":
            username = request.form['username']
            if username == user.username:

                password = request.form['password']
                if password != '':

                    user.password = generate_password_hash(password=password)
                    db.session.commit()
                    flash('Benutzer erfolgreich aktualisiert', 'success')
                    return redirect(url_for('app.admin_user_dashboard'))
                else:
                    flash('Ungültiges Passwort', 'error')
                    return redirect(url_for('app.admin_user_dashboard'))
            else:
                flash('Ungültiger Benutzer', 'error')
                return redirect(url_for('app.admin_user_dashboard'))
        return render_template("admin/admin_update_user_creds.html",user=user)
    else:
        flash('Sie sind nicht berechtigt', 'error')
        return redirect(url_for('app.home'))   
        
    





@app.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.role ==  UserRole.ADMIN:
            return render_template('admin/admin_home.html', user=current_user)
        else:
            return redirect(url_for('app.dashboard'))
    else:
        return redirect(url_for('app.login'))


