from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

# Models
class Todo(db.Model):  # Assignment Model
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.id}>'

class Project(db.Model):  # Project Model
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    task = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    file_path = db.Column(db.String(200), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Project {self.title}>'

# Initialize the database
with app.app_context():
    db.create_all()

# Landing Page
@app.route('/')
def landing_page():
    return render_template('landing.html')

# Assignment Routes
@app.route('/assignment/', methods=['GET', 'POST'])
def assignment_index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/assignment/')
        except:
            return "Error adding task"
    tasks = Todo.query.order_by(Todo.date_created).all()
    return render_template('assignment/index.html', tasks=tasks)

@app.route('/assignment/update/<int:id>', methods=['GET', 'POST'])
def update_assignment(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/assignment/')
        except:
            return "Error updating task"
    return render_template('assignment/update.html', task=task)

@app.route('/assignment/delete/<int:id>')
def delete_assignment(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/assignment/')
    except:
        return "Error deleting task"

# Project Routes
@app.route('/projects/', methods=['GET'])
def project_index():
    projects = Project.query.order_by(Project.date_created).all()
    return render_template('projects/index.html', projects=projects)

@app.route('/projects/new', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        title = request.form['title']
        task = request.form['task']
        category = request.form['category']
        priority = int(request.form['priority'])
        due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()
        file = request.files['file']
        file_path = None
        if file:
            file_path = f"{app.config['UPLOAD_FOLDER']}/{file.filename}"
            file.save(file_path)
        new_project = Project(
            title=title, task=task, category=category,
            priority=priority, due_date=due_date, file_path=file_path
        )
        try:
            db.session.add(new_project)
            db.session.commit()
            return redirect('/projects/')
        except:
            return "Error adding project"
    return render_template('projects/form.html')

@app.route('/projects/edit/<int:id>', methods=['GET', 'POST'])
def edit_project(id):
    project = Project.query.get_or_404(id)
    if request.method == 'POST':
        project.title = request.form['title']
        project.task = request.form['task']
        project.category = request.form['category']
        project.priority = int(request.form['priority'])
        project.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()
        file = request.files['file']
        if file:
            file_path = f"{app.config['UPLOAD_FOLDER']}/{file.filename}"
            file.save(file_path)
            project.file_path = file_path
        try:
            db.session.commit()
            return redirect('/projects/')
        except:
            return "Error updating project"
    return render_template('projects/edit.html', project=project)

@app.route('/projects/delete/<int:id>')
def delete_project(id):
    project_to_delete = Project.query.get_or_404(id)
    try:
        db.session.delete(project_to_delete)
        db.session.commit()
        return redirect('/projects/')
    except:
        return "Error deleting project"
    
@app.route('/projects/details/<int:id>', methods=['GET'])
def project_details(id):
    project = Project.query.get_or_404(id)  # Get the project or return 404 if not found
    return render_template('projects/details.html', project=project)

if __name__ == "__main__":
    app.run(debug=True)
