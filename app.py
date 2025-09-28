#!/usr/bin/env python3
from flask import Flask, request, session, jsonify, make_response, send_from_directory
from flask_restful import Resource
from config import app, db, api
from models import User, Recipe, Comment, Like, Favorite, Notification
from werkzeug.exceptions import NotFound, Unauthorized
from werkzeug.utils import secure_filename
import os
import uuid

@app.route('/')
def index():
    return '<h1>Recipe App Backend</h1>'

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Signup(Resource):
    def post(self):
        data = request.get_json()
        
        try:
            user = User(
                username=data.get('username'),
                email=data.get('email'),
            )
            user.password_hash = data.get('password')
            
            db.session.add(user)
            db.session.commit()
            
            session['user_id'] = user.id
            
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'bio': user.bio,
                'profile_picture': user.profile_picture,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }, 201
            
        except ValueError as e:
            return {'error': str(e)}, 400

class Login(Resource):
    def post(self):
        data = request.get_json()
        
        user = User.query.filter(User.username == data.get('username')).first()
        
        if user and user.authenticate(data.get('password')):
            session['user_id'] = user.id
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'bio': user.bio,
                'profile_picture': user.profile_picture,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }, 200
        
        return {'error': 'Invalid credentials'}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None
            return {}, 204
        return {'error': 'Not logged in'}, 401

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            recipe_count = Recipe.query.filter_by(user_id=user_id).count()
            
            likes_received = db.session.query(Like).join(Recipe).filter(Recipe.user_id == user_id).count()
            
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'bio': user.bio,
                'profile_picture': user.profile_picture,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'recipe_count': recipe_count,
                'likes_received': likes_received
            }, 200
        return {'error': 'Not logged in'}, 401

class Recipes(Resource):
    def get(self):
        recipes = Recipe.query.all()
        result = []
        for recipe in recipes:
            result.append({
                'id': recipe.id,
                'title': recipe.title,
                'description': recipe.description,
                'ingredients': recipe.ingredients,
                'instructions': recipe.instructions,
                'cooking_time': recipe.cooking_time,
                'image_url': recipe.image_url,
                'created_at': recipe.created_at.isoformat() if recipe.created_at else None,
                'user': {
                    'id': recipe.user.id,
                    'username': recipe.user.username,
                    'profile_picture': recipe.user.profile_picture
                },
                'likes': [{'id': like.id, 'user_id': like.user_id} for like in recipe.likes],
                'favorites': [{'id': fav.id, 'user_id': fav.user_id} for fav in recipe.favorites],
                'comments': [{'id': comment.id, 'content': comment.content, 'user_id': comment.user_id} for comment in recipe.comments]
            })
        return result, 200

    def post(self):
        if not session.get('user_id'):
            return {'error': 'Not logged in'}, 401
            
        data = request.get_json()
        
        try:
            recipe = Recipe(
                title=data.get('title'),
                description=data.get('description'),
                ingredients=data.get('ingredients'),
                instructions=data.get('instructions'),
                cooking_time=data.get('cooking_time'),
                image_url=data.get('image_url'),
                user_id=session.get('user_id')
            )
            
            db.session.add(recipe)
            db.session.commit()
            
            return {
                'id': recipe.id,
                'title': recipe.title,
                'description': recipe.description,
                'ingredients': recipe.ingredients,
                'instructions': recipe.instructions,
                'cooking_time': recipe.cooking_time,
                'image_url': recipe.image_url,
                'created_at': recipe.created_at.isoformat() if recipe.created_at else None
            }, 201
            
        except ValueError as e:
            return {'error': str(e)}, 400

class RecipeByID(Resource):
    def get(self, id):
        recipe = Recipe.query.get(id)
        if recipe:
            return {
                'id': recipe.id,
                'title': recipe.title,
                'description': recipe.description,
                'ingredients': recipe.ingredients,
                'instructions': recipe.instructions,
                'cooking_time': recipe.cooking_time,
                'image_url': recipe.image_url,
                'created_at': recipe.created_at.isoformat() if recipe.created_at else None,
                'user': {
                    'id': recipe.user.id,
                    'username': recipe.user.username,
                    'profile_picture': recipe.user.profile_picture
                },
                'likes': [{'id': like.id, 'user_id': like.user_id} for like in recipe.likes],
                'favorites': [{'id': fav.id, 'user_id': fav.user_id} for fav in recipe.favorites],
                'comments': [{
                    'id': comment.id, 
                    'content': comment.content, 
                    'user_id': comment.user_id,
                    'created_at': comment.created_at.isoformat() if comment.created_at else None,
                    'user': {
                        'id': comment.user.id,
                        'username': comment.user.username,
                        'profile_picture': comment.user.profile_picture
                    }
                } for comment in recipe.comments]
            }, 200
        return {'error': 'Recipe not found'}, 404

    def patch(self, id):
        if not session.get('user_id'):
            return {'error': 'Not logged in'}, 401
            
        recipe = Recipe.query.get(id)
        if not recipe:
            return {'error': 'Recipe not found'}, 404
            
        if recipe.user_id != session.get('user_id'):
            return {'error': 'Not authorized'}, 403
            
        data = request.get_json()
        
        try:
            for attr in data:
                setattr(recipe, attr, data[attr])
                
            db.session.commit()
            return {
                'id': recipe.id,
                'title': recipe.title,
                'description': recipe.description,
                'ingredients': recipe.ingredients,
                'instructions': recipe.instructions,
                'cooking_time': recipe.cooking_time,
                'image_url': recipe.image_url,
                'created_at': recipe.created_at.isoformat() if recipe.created_at else None
            }, 200
            
        except ValueError as e:
            return {'error': str(e)}, 400

    def delete(self, id):
        if not session.get('user_id'):
            return {'error': 'Not logged in'}, 401
            
        recipe = Recipe.query.get(id)
        if not recipe:
            return {'error': 'Recipe not found'}, 404
            
        if recipe.user_id != session.get('user_id'):
            return {'error': 'Not authorized'}, 403
            
        db.session.delete(recipe)
        db.session.commit()
        
        return {}, 204

class UserRecipes(Resource):
    def get(self, user_id):
        recipes = Recipe.query.filter(Recipe.user_id == user_id).all()
        result = []
        for recipe in recipes:
            result.append({
                'id': recipe.id,
                'title': recipe.title,
                'description': recipe.description,
                'ingredients': recipe.ingredients,
                'instructions': recipe.instructions,
                'cooking_time': recipe.cooking_time,
                'image_url': recipe.image_url,
                'created_at': recipe.created_at.isoformat() if recipe.created_at else None,
                'user': {
                    'id': recipe.user.id,
                    'username': recipe.user.username,
                    'profile_picture': recipe.user.profile_picture
                },
                'likes': [{'id': like.id, 'user_id': like.user_id} for like in recipe.likes],
                'comments': [{'id': comment.id, 'content': comment.content, 'user_id': comment.user_id} for comment in recipe.comments]
            })
        return result, 200

class Comments(Resource):
    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Not logged in'}, 401
            
        data = request.get_json()
        if not data:
            return {'error': 'No data provided'}, 400
            
        content = data.get('content', '').strip()
        recipe_id = data.get('recipe_id')
        
        if not content:
            return {'error': 'Comment content is required'}, 400
        if not recipe_id:
            return {'error': 'Recipe ID is required'}, 400
        
        try:
            comment = Comment(
                content=content,
                user_id=user_id,
                recipe_id=int(recipe_id)
            )
            
            db.session.add(comment)
            db.session.commit()
            
            user = User.query.get(user_id)
            
            recipe = Recipe.query.get(recipe_id)
            if recipe and recipe.user_id != user_id:
                notification = Notification(
                    type='comment',
                    user_id=recipe.user_id,
                    actor_id=user_id,
                    recipe_id=recipe.id
                )
                db.session.add(notification)
                db.session.commit()
            
            return {
                'id': comment.id,
                'content': comment.content,
                'user_id': comment.user_id,
                'recipe_id': comment.recipe_id,
                'created_at': comment.created_at.isoformat(),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'profile_picture': user.profile_picture
                }
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'error': 'Failed to create comment'}, 500

    def delete(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Not logged in'}, 401
            
        data = request.get_json()
        comment_id = data.get('comment_id')
        
        if not comment_id:
            return {'error': 'comment_id is required'}, 400
        
        try:
            comment = Comment.query.get(comment_id)
            if not comment:
                return {'error': 'Comment not found'}, 404
            
            recipe = Recipe.query.get(comment.recipe_id)
            if comment.user_id != user_id and (not recipe or recipe.user_id != user_id):
                return {'error': 'Not authorized to delete this comment'}, 403
            
            db.session.delete(comment)
            db.session.commit()
            return {}, 204
            
        except Exception as e:
            db.session.rollback()
            return {'error': 'Failed to delete comment'}, 500

class Likes(Resource):
    def post(self):
        if not session.get('user_id'):
            return {'error': 'Not logged in'}, 401
            
        data = request.get_json()
        
        if not data or not data.get('recipe_id'):
            return {'error': 'recipe_id is required'}, 400
        
        try:
            existing_like = Like.query.filter_by(
                user_id=session.get('user_id'),
                recipe_id=data.get('recipe_id')
            ).first()
            
            if existing_like:
                return {'error': 'Recipe already liked'}, 400
                
            like = Like(
                user_id=session.get('user_id'),
                recipe_id=data.get('recipe_id')
            )
            
            db.session.add(like)
            db.session.flush()
            
            existing_fav = Favorite.query.filter_by(
                user_id=session.get('user_id'),
                recipe_id=data.get('recipe_id')
            ).first()
            
            if not existing_fav:
                favorite = Favorite(
                    user_id=session.get('user_id'),
                    recipe_id=data.get('recipe_id')
                )
                db.session.add(favorite)
            
            recipe = Recipe.query.get(data.get('recipe_id'))
            if recipe and recipe.user_id != session.get('user_id'):
                notification = Notification(
                    type='like',
                    user_id=recipe.user_id,
                    actor_id=session.get('user_id'),
                    recipe_id=recipe.id
                )
                db.session.add(notification)
            
            db.session.commit()
            
            return {
                'id': like.id,
                'user_id': like.user_id,
                'recipe_id': like.recipe_id,
                'created_at': like.created_at.isoformat() if like.created_at else None
            }, 201
            
        except ValueError as e:
            db.session.rollback()
            return {'error': str(e)}, 400
        except Exception as e:
            db.session.rollback()
            return {'error': 'Failed to create like'}, 500

    def delete(self):
        if not session.get('user_id'):
            return {'error': 'Not logged in'}, 401
            
        data = request.get_json()
        
        if not data or not data.get('recipe_id'):
            return {'error': 'recipe_id is required'}, 400
        
        try:
            like = Like.query.filter_by(
                user_id=session.get('user_id'),
                recipe_id=data.get('recipe_id')
            ).first()
            
            if like:
                db.session.delete(like)
                
                favorite = Favorite.query.filter_by(
                    user_id=session.get('user_id'),
                    recipe_id=data.get('recipe_id')
                ).first()
                
                if favorite:
                    db.session.delete(favorite)
                
                db.session.commit()
                return {}, 204
                
            return {'error': 'Like not found'}, 404
        except Exception as e:
            db.session.rollback()
            return {'error': 'Failed to remove like'}, 500

class Favorites(Resource):
    def post(self):
        if not session.get('user_id'):
            return {'error': 'Not logged in'}, 401
            
        data = request.get_json()
        
        if not data or not data.get('recipe_id'):
            return {'error': 'recipe_id is required'}, 400
        
        try:
            existing_fav = Favorite.query.filter_by(
                user_id=session.get('user_id'),
                recipe_id=data.get('recipe_id')
            ).first()
            
            if existing_fav:
                return {'error': 'Recipe already favorited'}, 400
                
            favorite = Favorite(
                user_id=session.get('user_id'),
                recipe_id=data.get('recipe_id')
            )
            
            db.session.add(favorite)
            db.session.commit()
            
            return {
                'id': favorite.id,
                'user_id': favorite.user_id,
                'recipe_id': favorite.recipe_id,
                'created_at': favorite.created_at.isoformat() if favorite.created_at else None
            }, 201
            
        except ValueError as e:
            db.session.rollback()
            return {'error': str(e)}, 400
        except Exception as e:
            db.session.rollback()
            return {'error': 'Failed to create favorite'}, 500

    def delete(self):
        if not session.get('user_id'):
            return {'error': 'Not logged in'}, 401
            
        data = request.get_json()
        
        if not data or not data.get('recipe_id'):
            return {'error': 'recipe_id is required'}, 400
        
        try:
            favorite = Favorite.query.filter_by(
                user_id=session.get('user_id'),
                recipe_id=data.get('recipe_id')
            ).first()
            
            if favorite:
                db.session.delete(favorite)
                
                like = Like.query.filter_by(
                    user_id=session.get('user_id'),
                    recipe_id=data.get('recipe_id')
                ).first()
                
                if like:
                    db.session.delete(like)
                
                db.session.commit()
                return {}, 204
                
            return {'error': 'Favorite not found'}, 404
        except Exception as e:
            db.session.rollback()
            return {'error': 'Failed to remove favorite'}, 500

class UserFavorites(Resource):
    def get(self, user_id):
        favorites = Favorite.query.filter(Favorite.user_id == user_id).all()
        result = []
        for fav in favorites:
            result.append({
                'id': fav.id,
                'user_id': fav.user_id,
                'recipe_id': fav.recipe_id,
                'created_at': fav.created_at.isoformat() if fav.created_at else None,
                'recipe': {
                    'id': fav.recipe.id,
                    'title': fav.recipe.title,
                    'description': fav.recipe.description,
                    'image_url': fav.recipe.image_url,
                    'cooking_time': fav.recipe.cooking_time,
                    'user': {
                        'id': fav.recipe.user.id,
                        'username': fav.recipe.user.username,
                        'profile_picture': fav.recipe.user.profile_picture
                    },
                    'likes': [{'id': like.id, 'user_id': like.user_id} for like in fav.recipe.likes],
                    'comments': [{'id': comment.id, 'content': comment.content, 'user_id': comment.user_id} for comment in fav.recipe.comments]
                }
            })
        return result, 200

class Notifications(Resource):
    def get(self, user_id):
        if not session.get('user_id') or session.get('user_id') != int(user_id):
            return {'error': 'Not authorized'}, 403
            
        notifications = Notification.query.filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).all()
        
        result = []
        for notification in notifications:
            result.append({
                'id': notification.id,
                'type': notification.type,
                'read_status': notification.read_status,
                'created_at': notification.created_at.isoformat() if notification.created_at else None,
                'actor': {
                    'id': notification.actor.id,
                    'username': notification.actor.username,
                    'profile_picture': notification.actor.profile_picture
                },
                'recipe': {
                    'id': notification.recipe.id,
                    'title': notification.recipe.title
                } if notification.recipe else None
            })
        return result, 200

class MarkNotificationRead(Resource):
    def patch(self, id):
        if not session.get('user_id'):
            return {'error': 'Not logged in'}, 401
            
        notification = Notification.query.get(id)
        if not notification:
            return {'error': 'Notification not found'}, 404
            
        if notification.user_id != session.get('user_id'):
            return {'error': 'Not authorized'}, 403
            
        notification.read_status = True
        db.session.commit()
        
        return {
            'id': notification.id,
            'type': notification.type,
            'read_status': notification.read_status,
            'created_at': notification.created_at.isoformat() if notification.created_at else None
        }, 200

class RecipeComments(Resource):
    def get(self, recipe_id):
        comments = Comment.query.filter(Comment.recipe_id == recipe_id).order_by(Comment.created_at.desc()).all()
        result = []
        for comment in comments:
            result.append({
                'id': comment.id,
                'content': comment.content,
                'created_at': comment.created_at.isoformat() if comment.created_at else None,
                'user': {
                    'id': comment.user.id,
                    'username': comment.user.username,
                    'profile_picture': comment.user.profile_picture
                }
            })
        return result, 200

class UserProfile(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        if user:
            recipe_count = Recipe.query.filter_by(user_id=user_id).count()
            likes_received = db.session.query(Like).join(Recipe).filter(Recipe.user_id == user_id).count()
            
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'bio': user.bio,
                'profile_picture': user.profile_picture,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'recipe_count': recipe_count,
                'likes_received': likes_received
            }, 200
        return {'error': 'User not found'}, 404

    def patch(self, user_id):
        if not session.get('user_id') or session.get('user_id') != int(user_id):
            return {'error': 'Not authorized'}, 403
            
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        
        try:
            if request.files and 'profile_picture' in request.files:
                file = request.files['profile_picture']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    user.profile_picture = f'https://grab-a-grub-backend.onrender.com/uploads/{filename}'
            
            if request.form:
                username = request.form.get('username')
                email = request.form.get('email')
                bio = request.form.get('bio')
                
                if username and username != user.username:
                    existing_user = User.query.filter(User.username == username, User.id != user_id).first()
                    if existing_user:
                        return {'error': 'Username already taken'}, 400
                    user.username = username
                    
                if email and email != user.email:
                    existing_user = User.query.filter(User.email == email, User.id != user_id).first()
                    if existing_user:
                        return {'error': 'Email already taken'}, 400
                    user.email = email
                    
                if bio is not None:
                    user.bio = bio
            
            elif request.is_json:
                data = request.get_json()
                if data:
                    if 'username' in data and data['username'] != user.username:
                        existing_user = User.query.filter(User.username == data['username'], User.id != user_id).first()
                        if existing_user:
                            return {'error': 'Username already taken'}, 400
                        user.username = data['username']
                        
                    if 'email' in data and data['email'] != user.email:
                        existing_user = User.query.filter(User.email == data['email'], User.id != user_id).first()
                        if existing_user:
                            return {'error': 'Email already taken'}, 400
                        user.email = data['email']
                        
                    if 'bio' in data:
                        user.bio = data['bio']
                    if 'profile_picture' in data:
                        user.profile_picture = data['profile_picture']
                    
            db.session.commit()
            recipe_count = Recipe.query.filter_by(user_id=user_id).count()
            likes_received = db.session.query(Like).join(Recipe).filter(Recipe.user_id == user_id).count()
            
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'bio': user.bio,
                'profile_picture': user.profile_picture,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'recipe_count': recipe_count,
                'likes_received': likes_received
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 400

api.add_resource(Signup, '/api/signup')
api.add_resource(Login, '/api/login')
api.add_resource(Logout, '/api/logout')
api.add_resource(CheckSession, '/api/check_session')
api.add_resource(Recipes, '/api/recipes')
api.add_resource(RecipeByID, '/api/recipes/<int:id>')
api.add_resource(UserRecipes, '/api/recipes/user/<int:user_id>')
api.add_resource(Comments, '/api/comments')
api.add_resource(RecipeComments, '/api/comments/recipe/<int:recipe_id>')
api.add_resource(Likes, '/api/likes')
api.add_resource(Favorites, '/api/favorites')
api.add_resource(UserFavorites, '/api/favorites/user/<int:user_id>')
api.add_resource(Notifications, '/api/notifications/user/<int:user_id>')
api.add_resource(MarkNotificationRead, '/api/notifications/<int:id>/mark_read')
api.add_resource(UserProfile, '/api/users/<int:user_id>')

if __name__ == '__main__':
    app.run(port=5000, debug=True)