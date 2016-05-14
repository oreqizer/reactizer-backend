from sqlalchemy import Column, Integer, String
from flask import Blueprint, request, jsonify

from reactizer.database import Base, db_session


class Todo(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True)
    text = Column(String(256))

    def __init__(self, text=None):
        self.text = text

    def __repr__(self):
        return '<Todo: %r>' % self.text


todos = Blueprint('todos', __name__)


@todos.route('/api/todos', methods=['GET', 'POST'])
def show_entries():
    if request.method == 'POST':
        """creates a new todo"""
        todo = Todo(request.form['text'])
        db_session.add(todo)
        db_session.commit()
        return jsonify(status='ok')
    else:
        """sends all todos in the database"""
        todos = Todo.query.all()
        return jsonify(todos=todos)