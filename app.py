from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
db = SQLAlchemy(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id
    
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    file_path = db.Column(db.String(200), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Project {self.title}>'

with app.app_context():
    db.create_all()

# Landing Page Route
@app.route('/')
def landing_page():
    if request.method == 'POST':
        # Handle POST request logic here
        pass
    return render_template('landing.html')

#@app.route('/projects/', methods=['GET'])
#def projects():
 #   if request.method == 'POST':
  #      pass
   # return render_template('projects/index.html', projects=projects)
@app.route('/projects/', methods=['GET'])
def projects():
    """
    Displays all projects with optional sorting.
    """
    sort_by = request.args.get('sort_by', 'date_created')  # Default sorting by creation date
    if sort_by == 'priority':
        projects = Project.query.order_by(Project.priority).all()
    elif sort_by == 'category':
        projects = Project.query.order_by(Project.category).all()
    elif sort_by == 'due_date':
        projects = Project.query.order_by(Project.due_date).all()
    else:
        projects = Project.query.order_by(Project.date_created).all()
    return render_template('projects/index.html', projects=projects)

@app.route('/new_project/', methods=['GET', 'POST'])
def new_project():
    """
    Route to add a new project.
    """
    if request.method == 'POST':
        try:
            # Collect form data
            title = request.form['task']
            category = request.form['category']
            priority = int(request.form['priority'])
            due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()
            file = request.files['file']

            # Handle file upload
            file_path = None
            if file and file.filename != '':
                filename = file.filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

            # Create new project
            new_project = Project(
                title=title,
                category=category,
                priority=priority,
                due_date=due_date,
                file_path=file_path
            )

            # Commit to database
            db.session.add(new_project)
            db.session.commit()
            return redirect('/projects/')
        except Exception as e:
            # Print error to console for debugging
            print(f"Error adding project: {e}")
            return 'There was an issue adding your project.'
    return render_template('projects/new.html')

@app.route('/edit_project/<int:id>/', methods=['GET', 'POST'])
def edit_project(id):
    """
    Route to edit an existing project.
    """
    project = Project.query.get_or_404(id)
    if request.method == 'POST':
        project.title = request.form['task']
        project.category = request.form['category']
        project.priority = int(request.form['priority'])
        project.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()

        file = request.files['file']
        if file and file.filename != '':
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            project.file_path = file_path

        try:
            db.session.commit()
            return redirect('/projects/')
        except:
            return 'There was an issue updating your project.'

    return render_template('projects/edit.html', project=project)

@app.route('/delete_project/<int:id>/')
def delete_project(id):
    """
    Route to delete a project.
    """
    project_to_delete = Project.query.get_or_404(id)
    try:
        db.session.delete(project_to_delete)
        db.session.commit()
        return redirect('/projects/')
    except:
        return 'There was an issue deleting your project.'

@app.route('/assignment/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/assignment/')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('assignment/index.html', tasks=tasks)

@app.route('/assignment/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/assignment/')
    except:
        return 'There was a problem deleting that task'

@app.route('/assignment/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/assignment/')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('assignment/update.html', task=task)
    
if __name__ == "__main__":
    app.run(debug=True)
