## Grab-a-Grub 
A full-stack recipe sharing application where food enthusiasts can discover, share, and interact with delicious recipes from around the world.

## Features

### Core Functionality
- User Authentication: Secure signup/login with password hashing
- Recipe Management: Create, read, update, and delete recipes
- Social Interactions: Like, favorite, and comment on
recipes
- User Profiles: Customizable profiles with bio and profile pictures
- Real-time Notifications: Get notified when users interact with your recipes
- Image Upload: Upload and display recipe and profile images

### User Experience
- Responsive Design: Works seamlessly 
- Search & Filter: Find recipes by various criteria
- Personal Collections: Save favorite recipes for easy access
- Community Features: Follow other chefs and see their latest creations

## Tech Stack

### Backend
- Flask: Python web framework
- SQLAlchemy: Database ORM
- Flask-RESTful: RESTful API development
- Flask-Migrate: Database migrations
- Flask-CORS: Cross-origin resource sharing
- Flask-Bcrypt: Password hashing
- SQLite: Database 

### Frontend
- React: User interface library
- React Router: Client-side routing
- Formik: Form handling and validation
- CSS3: Styling 

## Prerequisites

- Python 3.12+
- Node.js 14+
- npm 

## Installation & Setup

### Backend Setup

1. Clone the repository
   git clone: git@github.com:Anisah23/grab-a-grub-backend.git
   cd grab-a-grub-backend

2. Create virtual environment
   pipenv shell

3. Install dependencies
   pip install -r requirements.txt

5. Initialize database
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   

6. Seed the database (optional)
   python seed.py

7. Run the server
   python run.py or flask run
   
The backend will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory
     grab-a-grub-frontend

2. Instructions on the setup are stated in the directory's README.md

The frontend will be available at `http://localhost:3000`

## Database Schema

### Models
- User: User accounts with authentication
- Recipe: Recipe posts with ingredients and instructions
- Comment: User comments on recipes
- Like: Recipe likes (many-to-many with timestamp)
- Favorite: Saved recipes (many-to-many with timestamp)
- Notification: User notifications for interactions

### Relationships
- User → Recipes (One-to-Many)
- User → Comments (One-to-Many)
- Recipe → Comments (One-to-Many)
- User ↔ Recipes via Likes (Many-to-Many)
- User ↔ Recipes via Favorites (Many-to-Many)

## API Endpoints

### Authentication
- Create new user account
- User login
- User logout
- Check authentication status

### Recipes
- Get all recipes
- Create new recipe
- Get specific recipe
- Update recipe
- Delete recipe
- Get user's recipes

### Social Features
- Like a recipe
- Unlike a recipe
- Favorite a recipe
- Unfavorite a recipe
- Get user's favorites

### Comments
- Add comment
- Delete comment
- Get recipe comments

### User Management
- Get user profile
- Update user profile
- Get user notifications

### Test Accounts
- Username: chef_mario | Password: password123
- Username: baker_sarah | Password: password123
- Username: healthy_cook | Password: password123
- Username: spice_master | Password: password123
- Username: grill_king | Password: password123

## Author
-Anisah23
-Carltonshiyai

## License
This project is licensed under the MIT License.
