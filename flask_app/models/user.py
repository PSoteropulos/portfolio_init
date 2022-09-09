from flask_app.config.mysqlconnection import connectToMySQL
import re
from flask import flash
from datetime import date, datetime
from flask_app import app
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
from flask_app.models import recipe


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'[a-zA-Z ]')
PASSWORD_REGEX = re.compile(r'(?=.{8,}$)(?=.*[A-Z])(?=.*[0-9])')
# this password regex was found at https://riptutorial.com/regex/example/18996/a-password-containing-at-least-1-uppercase--1-lowercase--1-digit--1-special-character-and-have-a-length-of-at-least-of-10

class User:
    def __init__( self , data ):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.favorite_recipes=[ ]
        self.recipes_created= [ ]

    def __repr__(self):
        display = f"<{self.first_name} {self.last_name}>"
        return display

    @classmethod
    def save(cls, data ):
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at ) VALUES ( %(first_name)s, %(last_name)s, %(email)s, %(password)s, NOW(), NOW());"
        return connectToMySQL('recipes').query_db( query, data )

    @classmethod
    def update(cls, data ):
        query = "UPDATE users SET first_name=%(first_name)s, last_name=%(last_name)s , email=%(email)s, password=%(password)s, updated_at=NOW() where id= %(id)s;"
        return connectToMySQL('recipes').query_db( query, data )

    @classmethod
    def get_one_id(cls, data):
        query= "SELECT * FROM users WHERE id=%(id)s;"
        results = connectToMySQL('recipes').query_db(query, data)
        # print(results)
        return cls(results[0]) 

    @classmethod
    def get_one_email(cls, data):
        query= "SELECT * FROM users WHERE email=%(email)s;"
        results = connectToMySQL('recipes').query_db(query, data)
        # print(results)
        return cls(results[0]) 

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"
        results = connectToMySQL('recipes').query_db(query)  
        users = []
        for user in results:
            users.append( cls(user) )
        # print(users)
        return users

    @classmethod
    def add_favorite(cls, data):
        query = "SELECT * FROM favorites WHERE user_id=%(user_id)s AND recipe_id=%(recipe_id)s;"
        results = connectToMySQL('recipes').query_db(query, data)
        print(results)
        if results == ():
            query = "INSERT INTO favorites (user_id, recipe_id) VALUES (%(user_id)s, %(recipe_id)s);"
            return connectToMySQL('recipes').query_db( query, data )
        else:
            print("Favorite already in database.")
            return False

    @classmethod
    def delete_favorite(cls, data):
        query = "DELETE FROM favorites WHERE user_id=%(user_id)s AND recipe_id=%(recipe_id)s;"
        return connectToMySQL('recipes').query_db( query, data )

    @classmethod
    def get_favorite_recipes(cls, data):
        query = "SELECT * FROM users LEFT JOIN favorites ON users.id=favorites.user_id LEFT JOIN recipes on recipes.id=favorites.recipe_id WHERE users.id=%(id)s;"
        results = connectToMySQL('recipes').query_db(query, data)
        # print (f"these are the results of get favorite recipes query:", results)
        user = cls(results[0])
        user.favorite_recipes=[ ]
        if results[0]['recipes.id'] == None:
            return False
        else:

            results_sorted=sorted(
            results,
            key=lambda x: datetime.strftime(x['recipes.created_at'], '%m/%d/%y %H:%M:%S'), reverse=True)
            # a whole lot of googling and stitching together pieces of stuff for this
            print(results_sorted)
            for row in results_sorted:
            # for row in results:
                one_recipe_info={
                    "id":row["recipes.id"],
                    "name": row['name'],
                    "description": row['description'],
                    "instructions": row['instructions'],
                    "date_made": row['date_made'],
                    "under_30": row['under_30'],
                    "created_at": row['recipes.created_at'],
                    "updated_at": row['recipes.updated_at'],
                    "user_id": row['recipes.user_id']
                }
                creator_id={
                    "id":one_recipe_info['user_id']
                }
                one_favorite_recipe=recipe.Recipe(one_recipe_info)
                # print("about to query2")
                query2 = "SELECT * FROM users WHERE id=%(id)s;"
                results2 = connectToMySQL('recipes').query_db(query2, creator_id)
                # print(f"super cool query2 results", results2)
                creator_obj=User(results2[0])
                # print(creator_obj)
                one_favorite_recipe.creator = creator_obj
                if one_favorite_recipe not in user.favorite_recipes:
                    user.favorite_recipes.append(one_favorite_recipe)
                # print(one_recipe)
                # print(one_recipe.creator)
            return user




    @staticmethod
    def validate_login(user):
        is_valid = True

        query= "SELECT * FROM users WHERE email=%(email)s;"
        results = connectToMySQL('recipes').query_db(query, user)
        if len(results) != 1:
            flash("Invalid email/password.", "login")
            is_valid=False
            return is_valid

        if not bcrypt.check_password_hash(results[0]['password'], user['password']):
            flash("Invalid email/password.", "login")
            is_valid=False

        return is_valid

    @staticmethod
    def validate_user(user):
        is_valid = True

        if len(user['first_name']) < 2 or not NAME_REGEX.match(user['first_name']):
            flash("First name must be at least 2 characters, and can only contain letters.", "register")
            is_valid = False

        if len(user['last_name']) < 2 or not NAME_REGEX.match(user['last_name']):
            flash("Last name must be at least 2 characters, and can only contain letters.", "register")
            is_valid = False

        query= "SELECT * FROM users WHERE email=%(email)s;"
        results = connectToMySQL('recipes').query_db(query, user)
        print(results)
        if len(results) >= 1:
            flash("Email address already registered. Please Login, or register a different email address.", "register")
            is_valid = False

        if not EMAIL_REGEX.match(user['email']): 
            flash("Invalid email address.", "register")
            is_valid = False

        if not PASSWORD_REGEX.match(user["password"]):
            flash("Invalid password format: must be at least 8 characters, contain at least 1 uppercase letter, and at least 1 number.", "register")
            is_valid = False

        if user["password_confirm"] != user["password"]:
            flash("Passwords do not match.", "register")
            is_valid = False

        return is_valid