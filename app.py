from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key
bcrypt = Bcrypt(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client.todo_db
users = db.users
todos = db.todos

# User model for Flask-Login
class User(UserMixin):
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    user = users.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(str(user['_id']), user['username'], user['password'])
    return None

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        users.insert_one({"username": username, "password": hashed_password})
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            login_user(User(str(user['_id']), user['username'], user['password']))
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    tasks = list(todos.find({"user_id": current_user.id}))
    for task in tasks:
        task['_id'] = str(task['_id'])
    return render_template('index.html', tasks=tasks)

@app.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    tasks = list(todos.find({"user_id": current_user.id}))
    for task in tasks:
        task['_id'] = str(task['_id'])
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
@login_required
def add_task():
    task = request.json
    task['user_id'] = current_user.id
    task['status'] = 'Not Started'  # Default status
    todos.insert_one(task)
    task['_id'] = str(task['_id'])
    return jsonify(task), 201

@app.route('/tasks/<task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    updated_task = request.json
    result = todos.update_one({'_id': ObjectId(task_id), 'user_id': current_user.id}, {'$set': updated_task})
    if result.modified_count == 1:
        updated_task['_id'] = task_id
        return jsonify(updated_task)
    else:
        return jsonify({"error": "Task not found or no changes made"}), 404

@app.route('/tasks/<task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    result = todos.delete_one({'_id': ObjectId(task_id), 'user_id': current_user.id})
    if result.deleted_count == 1:
        return jsonify({"message": "Task deleted"})
    else:
        return jsonify({"error": "Task not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0')
