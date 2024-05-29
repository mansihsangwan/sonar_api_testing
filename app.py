from flask import Flask, request, g
import sqlite3
from flasgger import Swagger, swag_from

app = Flask(__name__)
swagger = Swagger(app)

DATABASE = 'users.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          username TEXT NOT NULL,
                          email TEXT NOT NULL)''')
        db.commit()

@app.route('/add_user', methods=['POST'])
@swag_from({
    'responses': {
        200: {
            'description': 'User added successfully!'
        }
    },
    'parameters': [
        {
            'name': 'username',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'The username of the user'
        },
        {
            'name': 'email',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'The email of the user'
        }
    ]
})
def add_user():
    username = request.form['username']
    email = request.form['email']
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO users (username, email) VALUES (?, ?)", (username, email))
    db.commit()
    return "User added successfully!"

@app.route('/get_user/<username>', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'User information retrieved successfully',
            'examples': {
                'application/json': {
                    'username': 'testuser',
                    'email': 'testuser@example.com'
                }
            }
        },
        404: {
            'description': 'User not found'
        }
    },
    'parameters': [
        {
            'name': 'username',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'The username of the user to retrieve'
        }
    ]
})
def get_user(username):
    db = get_db()
    cursor = db.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"  # Vulnerable to SQL Injection
    cursor.execute(query)
    user = cursor.fetchone()
    if user:
        return {
            'username': user[1],
            'email': user[2]
        }
    else:
        return "User not found!", 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
