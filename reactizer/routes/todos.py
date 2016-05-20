from flask import Blueprint, request, jsonify, g

from reactizer.database import db
from reactizer.models.todos import Todo
from reactizer.tools import auth
from reactizer.enums.todo_keys import TodoKeys

todos = Blueprint('todos', __name__)


@todos.route('/api/todos', methods=['GET', 'POST'])
@auth.authorize()
def list_or_add():
    if request.method == 'POST':
        """creates a new todo"""
        todo = Todo(**request.get_json(), user=g.user)
        db.session.add(todo)
        db.session.commit()
        return jsonify(status='ok')
    else:
        """sends all todos in the database"""
        results = [dict(todo) for todo in Todo.query.filter_by(user_id=g.user.id)]
        return jsonify(todos=results)


@todos.route('/api/todos/<int:todo_id>', methods=['PUT', 'DELETE'])
@auth.authorize()
def manipulate(todo_id):
    if request.method == 'PUT':
        """updates a todo"""
        todo = Todo.query.get(todo_id)
        if not todo:
            return str(TodoKeys.not_found), 404

        if todo.user_id != g.user.id:
            return str(TodoKeys.not_owner), 401

        todo.user_id = 1337
        print(todo)
        db.session.commit()
        return jsonify(status='ok')
    else:
        """deletes a todo"""
        todo = Todo.query.get(todo_id)
        if not todo:
            return str(TodoKeys.not_found), 404

        if todo.user_id != g.user.id:
            return str(TodoKeys.not_owner), 401

        db.session.delete(todo)
        db.session.commit()
        return jsonify(status='ok')
