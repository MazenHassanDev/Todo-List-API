from flask import Blueprint, request, jsonify
from database import Session
from models.todo_model import Todo
from utils.jwt_verification import token_required, get_current_user_id
from utils.extensions import limiter

todos_bp = Blueprint('todos', __name__)

@todos_bp.route('/todos', methods=['GET'])
@token_required
@limiter.limit('60 per minute',key_func=get_current_user_id)
def get_todos(user_id):

    session = Session()

    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        offset = (page - 1) * limit
        query = session.query(Todo).filter_by(user_id=user_id)
        search_term = request.args.get('term')
        sort = request.args.get('sort')
        order = request.args.get('order')

        if search_term:
            query = query.filter(Todo.title.like(f'%{search_term}%') | Todo.description.like(f'%{search_term}%'))

        allowed_sorts = {
            'title': Todo.title,
            'created_at': Todo.created_at
        }

        sort_column = allowed_sorts.get(sort, Todo.created_at)

        if order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        total = query.count()
        todos = query.offset(offset).limit(limit).all()

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
@limiter.limit('30 per minute', key_func=get_current_user_id)
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

@todos_bp.route('/todos/<int:todo_id>', methods=['PUT'])
@token_required
@limiter.limit('30 per minute', key_func=get_current_user_id)
def update_todo(user_id, todo_id):
    data = request.get_json()

    if not data:
        return jsonify({'message': "No data provided"}), 400
    
    session = Session()

    try:
        todo = session.query(Todo).filter_by(id=todo_id).first()

        if not todo:
            return jsonify({'message': "Todo not found"}), 404
        
        if todo.user_id != user_id:
            return jsonify({'message': "You are not allowed to update this todo"}), 403
        
        todo.title = data.get('title', todo.title)
        todo.description = data.get('description', todo.description)
        session.commit()

        return jsonify({
            "id": todo.id,
            "title": todo.title,
            "description": todo.description
        }), 200
    
    except Exception as e:
        session.rollback()
        return jsonify({'message': 'Something went wrong', 'error': str(e)}), 500
    
    finally:
        session.close()

@todos_bp.route('/todos/<int:todo_id>', methods=['DELETE'])
@token_required
@limiter.limit('30 per minute', key_func=get_current_user_id)
def delete_todo(user_id, todo_id):
    
    session = Session()

    try:
        todo = session.query(Todo).filter_by(id=todo_id).first()

        if not todo:
            return jsonify({'message': "Todo not found"}), 404
        
        if todo.user_id != user_id:
            return jsonify({'message': "You are not allowed to delete this todo"}), 403
        
        session.delete(todo)
        session.commit()

        return "", 204
    
    except Exception as e:
        session.rollback()
        return jsonify({'message': 'Something went wrong', 'error': str(e)}), 500
    
    finally:
        session.close()

