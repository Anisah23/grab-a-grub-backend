from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from config import db, bcrypt
from sqlalchemy.ext.hybrid import hybrid_property
import re

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128), nullable=False)
    bio = db.Column(db.Text)
    profile_picture = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    recipes = db.relationship('Recipe', back_populates='user', cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='user', cascade='all, delete-orphan')
    likes = db.relationship('Like', back_populates='user', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', back_populates='user', cascade='all, delete-orphan')
    
    notifications = db.relationship('Notification', foreign_keys='Notification.user_id', back_populates='user')
    
    actor_notifications = db.relationship('Notification', foreign_keys='Notification.actor_id', back_populates='actor')

    serialize_rules = (
        '-_password_hash', 
        '-recipes.user', 
        '-comments.user', 
        '-likes.user',
        '-favorites.user',
        '-notifications.user',
        '-actor_notifications.actor'
    )

    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password hashes may not be viewed.')

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

    @validates('username')
    def validate_username(self, key, username):
        if not username or len(username) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if User.query.filter(User.username == username).first():
            raise ValueError("Username already taken")
        return username

    @validates('email')
    def validate_email(self, key, email):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError("Invalid email format")
        if User.query.filter(User.email == email).first():
            raise ValueError("Email already registered")
        return email

    def __repr__(self):
        return f'<User {self.username}>'

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    cooking_time = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', back_populates='recipes')
    comments = db.relationship('Comment', back_populates='recipe', cascade='all, delete-orphan')
    likes = db.relationship('Like', back_populates='recipe', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', back_populates='recipe', cascade='all, delete-orphan')

    serialize_rules = (
        '-user.recipes', 
        '-user.comments', 
        '-user.likes',
        '-user.favorites',
        '-user.notifications',
        '-user.actor_notifications',
        '-comments.recipe',
        '-comments.user.recipes',
        '-comments.user.comments',
        '-likes.recipe',
        '-likes.user.recipes',
        '-likes.user.likes',
        '-favorites.recipe',
        '-favorites.user.recipes',
        '-favorites.user.favorites'
    )

    @validates('title')
    def validate_title(self, key, title):
        if not title or len(title) < 3:
            raise ValueError("Title must be at least 3 characters long")
        return title

    @validates('cooking_time')
    def validate_cooking_time(self, key, cooking_time):
        if not isinstance(cooking_time, int) or cooking_time <= 0:
            raise ValueError("Cooking time must be a positive integer")
        return cooking_time

    @validates('ingredients', 'instructions')
    def validate_content(self, key, content):
        if not content or len(content) < 10:
            raise ValueError(f"{key} must be at least 10 characters long")
        return content

    def __repr__(self):
        return f'<Recipe {self.title}>'

class Comment(db.Model, SerializerMixin):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)

    user = db.relationship('User', back_populates='comments')
    recipe = db.relationship('Recipe', back_populates='comments')

    serialize_rules = ('-user.comments', '-recipe.comments')

    @validates('content')
    def validate_content(self, key, content):
        if not content or len(content.strip()) < 1:
            raise ValueError("Comment cannot be empty")
        return content

    def __repr__(self):
        return f'<Comment by User {self.user_id}>'

class Like(db.Model, SerializerMixin):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)

    user = db.relationship('User', back_populates='likes')
    recipe = db.relationship('Recipe', back_populates='likes')

    serialize_rules = ('-user.likes', '-recipe.likes')

    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id', name='unique_user_recipe_like'),)

    def __repr__(self):
        return f'<Like User {self.user_id} -> Recipe {self.recipe_id}>'

class Favorite(db.Model, SerializerMixin):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)

    user = db.relationship('User', back_populates='favorites')
    recipe = db.relationship('Recipe', back_populates='favorites')

    serialize_rules = ('-user.favorites', '-recipe.favorites')

    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id', name='unique_user_recipe_favorite'),)

    def __repr__(self):
        return f'<Favorite User {self.user_id} -> Recipe {self.recipe_id}>'

class Notification(db.Model, SerializerMixin):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)
    read_status = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=True)

    user = db.relationship('User', foreign_keys=[user_id], back_populates='notifications')
    actor = db.relationship('User', foreign_keys=[actor_id], back_populates='actor_notifications')
    recipe = db.relationship('Recipe')

    serialize_rules = ('-user.notifications', '-actor.actor_notifications', '-recipe.notifications')

    @validates('type')
    def validate_type(self, key, type):
        valid_types = ['like', 'comment', 'follow', 'comment_deleted']
        if type not in valid_types:
            raise ValueError(f"Notification type must be one of: {valid_types}")
        return type

    def __repr__(self):
        return f'<Notification {self.type} for User {self.user_id}>'