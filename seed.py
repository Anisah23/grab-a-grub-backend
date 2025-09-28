#!/usr/bin/env python3

from app import app, db
from models import User, Recipe, Comment, Like, Favorite, Notification
import random

def seed_data():
    with app.app_context():
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        print("Creating users...")
        users_data = [
            {"username": "chef_mario", "email": "mario@recipes.com", "bio": "Italian cuisine expert", "profile_picture": "https://images.unsplash.com/photo-1577219491135-ce391730fb2c?w=200&h=200&fit=crop&crop=face"},
            {"username": "baker_sarah", "email": "sarah@baking.com", "bio": "Professional baker and pastry chef", "profile_picture": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200&h=200&fit=crop&crop=face"},
            {"username": "healthy_cook", "email": "health@food.com", "bio": "Nutritionist and healthy recipe creator", "profile_picture": "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=200&h=200&fit=crop&crop=face"},
            {"username": "spice_master", "email": "spice@flavors.com", "bio": "Indian and Asian cuisine specialist", "profile_picture": "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=200&h=200&fit=crop&crop=face"},
            {"username": "grill_king", "email": "grill@bbq.com", "bio": "BBQ and grilling enthusiast", "profile_picture": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face"}
        ]
        
        users = []
        for user_data in users_data:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                bio=user_data["bio"],
                profile_picture=user_data["profile_picture"]
            )
            user.password_hash = "password123"
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        print(f"Created {len(users)} users")
        
        print("Creating recipes...")
        recipes_data = [
            {
                "title": "Classic Spaghetti Carbonara",
                "description": "Authentic Italian pasta dish with eggs, cheese, and pancetta",
                "ingredients": "400g spaghetti, 200g pancetta, 4 large eggs, 100g Pecorino Romano cheese, Black pepper, Salt",
                "instructions": "1. Cook spaghetti in salted water. 2. Fry pancetta until crispy. 3. Whisk eggs with cheese. 4. Combine hot pasta with pancetta, then add egg mixture off heat. 5. Toss quickly and serve with black pepper.",
                "cooking_time": 25,
                "image_url": "https://images.unsplash.com/photo-1621996346565-e3dbc353d2e5?w=400&h=300&fit=crop"
            },
            {
                "title": "Chocolate Chip Cookies",
                "description": "Soft and chewy homemade chocolate chip cookies",
                "ingredients": "2 cups flour, 1 tsp baking soda, 1 tsp salt, 1 cup butter, 3/4 cup brown sugar, 1/4 cup white sugar, 2 eggs, 2 tsp vanilla, 2 cups chocolate chips",
                "instructions": "1. Preheat oven to 375°F. 2. Mix dry ingredients. 3. Cream butter and sugars. 4. Add eggs and vanilla. 5. Combine wet and dry ingredients. 6. Fold in chocolate chips. 7. Bake for 9-11 minutes.",
                "cooking_time": 30,
                "image_url": "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=400&h=300&fit=crop"
            },
            {
                "title": "Quinoa Buddha Bowl",
                "description": "Nutritious bowl with quinoa, roasted vegetables, and tahini dressing",
                "ingredients": "1 cup quinoa, 2 cups mixed vegetables, 1/4 cup tahini, 2 tbsp lemon juice, 1 tbsp olive oil, Salt, pepper, herbs",
                "instructions": "1. Cook quinoa according to package directions. 2. Roast vegetables at 400°F for 25 minutes. 3. Make tahini dressing with lemon juice and olive oil. 4. Assemble bowl with quinoa, vegetables, and dressing.",
                "cooking_time": 45,
                "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop"
            },
            {
                "title": "Chicken Tikka Masala",
                "description": "Creamy Indian curry with tender chicken pieces",
                "ingredients": "1 lb chicken breast, 1 cup yogurt, 2 tbsp tikka masala spice, 1 onion, 3 cloves garlic, 1 can tomatoes, 1/2 cup heavy cream, Basmati rice",
                "instructions": "1. Marinate chicken in yogurt and spices for 2 hours. 2. Grill chicken pieces. 3. Sauté onion and garlic. 4. Add tomatoes and simmer. 5. Add cream and grilled chicken. 6. Serve with rice.",
                "cooking_time": 60,
                "image_url": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&h=300&fit=crop"
            },
            {
                "title": "BBQ Pulled Pork",
                "description": "Slow-cooked pork shoulder with homemade BBQ sauce",
                "ingredients": "3 lb pork shoulder, 2 tbsp brown sugar, 1 tbsp paprika, 1 tsp garlic powder, 1 tsp onion powder, BBQ sauce ingredients",
                "instructions": "1. Rub pork with spice mixture. 2. Slow cook for 8 hours on low. 3. Shred meat with forks. 4. Mix with BBQ sauce. 5. Serve on buns with coleslaw.",
                "cooking_time": 480,
                "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?w=400&h=300&fit=crop"
            }
        ]
        
        recipes = []
        for recipe_data in recipes_data:
            recipe = Recipe(
                title=recipe_data["title"],
                description=recipe_data["description"],
                ingredients=recipe_data["ingredients"],
                instructions=recipe_data["instructions"],
                cooking_time=recipe_data["cooking_time"],
                image_url=recipe_data["image_url"],
                user_id=random.choice(users).id
            )
            recipes.append(recipe)
            db.session.add(recipe)
        
        db.session.commit()
        print(f"Created {len(recipes)} recipes")
        
        print("Creating comments...")
        comments_data = [
            "This recipe is amazing! Made it for dinner tonight.",
            "Perfect! My family loved it.",
            "Easy to follow instructions, great results.",
            "Will definitely make this again.",
            "Delicious! Added some extra spices.",
            "Best recipe I've tried in a while.",
            "Simple and tasty, exactly what I needed.",
            "Great for meal prep too!",
            "My kids actually ate their vegetables with this recipe.",
            "Restaurant quality at home!"
        ]
        
        comments = []
        for i in range(20):
            comment = Comment(
                content=random.choice(comments_data),
                user_id=random.choice(users).id,
                recipe_id=random.choice(recipes).id
            )
            comments.append(comment)
            db.session.add(comment)
        
        db.session.commit()
        print(f"Created {len(comments)} comments")
        
        print("Creating likes...")
        likes = []
        for i in range(80):
            try:
                like = Like(
                    user_id=random.choice(users).id,
                    recipe_id=random.choice(recipes).id
                )
                likes.append(like)
                db.session.add(like)
            except:
                continue
        
        db.session.commit()
        print(f"Created {len(likes)} likes")
        
        print("Creating favorites...")
        favorites = []
        for i in range(60):
            try:
                favorite = Favorite(
                    user_id=random.choice(users).id,
                    recipe_id=random.choice(recipes).id
                )
                favorites.append(favorite)
                db.session.add(favorite)
            except:
                continue
        
        db.session.commit()
        print(f"Created {len(favorites)} favorites")
        
        print("Creating notifications...")
        notifications = []
        for i in range(30):
            notification = Notification(
                type=random.choice(['like', 'comment']),
                user_id=random.choice(users).id,
                actor_id=random.choice(users).id,
                recipe_id=random.choice(recipes).id
            )
            notifications.append(notification)
            db.session.add(notification)
        
        db.session.commit()
        print(f"Created {len(notifications)} notifications")
        
        print("Seeding completed successfully!")

if __name__ == '__main__':
    seed_data()