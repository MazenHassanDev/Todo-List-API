from flask import Blueprint, request, jsonify
from database import Session
from models.todo_model import Todo
from jwt_verification import token_required

todos_bp = Blueprint('todos', __name__)

@todos_bp.route('/todos', methods=['GET'])
@token_required
def get_todos(user_id):
    session = Session()

    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        offset = (page - 1) * limit

        total = session.query(Todo).filter_by(user_id=user_id).count()

        todos = (session.query(Todo).filter_by(user_id=user_id).offset(offset).limit(limit).all())

        return jsonify({
            "data": [
                {
                    "id": todo.id,
                    "title": todo.title,
                    "description": todo.description
                }
                for todo in todos
            ],
            "page": page,
            "limit": limit,
            "total": total
        }), 200
    
    except Exception as e:
        return jsonify({"message": "something went wrong", "error": str(e)}), 500
    
    finally:
        session.close()

@todos_bp.route('/todos', methods=['POST'])
@token_required
def create_todo(user_id):
    data = request.get_json()

    if not data:
        return jsonify({"message": "No data provided."}), 400
    
    title = data.get('title')
    description = data.get('description')

    if not title:
        return jsonify({"message": "Title is required."}), 400

    session = Session()

    try:

        user_todo = Todo(title=title, description=description, user_id=user_id)

        session.add(user_todo)
        session.commit()

        return jsonify({
            "id": user_todo.id,
            "title" : user_todo.title,
            "description": user_todo.description
        })
    
    except Exception as e:
        return jsonify({"message": "Something went wrong.", "error": str(e)}), 500
    
    finally:
        session.close()
