from datetime import datetime
from time import strptime
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models import user

class Recipe:
    def __init__( self , data ):
        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.instructions = data['instructions']
        self.date_made = data['date_made']
        self.under_30 = data['under_30']
        self.user_id=data['user_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.creator= None
        self.recipe_favorite_of_users = [ ]

    def __repr__(self):
        display = f"<{self.id} {self.name} created by {self.creator.first_name} {self.creator.last_name}>"
        return display

    @classmethod
    def save(cls, data ):
        query = "INSERT INTO recipes (name, description, instructions, date_made, under_30, user_id, created_at, updated_at ) VALUES (%(name)s, %(description)s, %(instructions)s, %(date_made)s, %(under_30)s,  %(user_id)s, NOW() , NOW() );"
        return connectToMySQL('recipes').query_db( query, data )

    @classmethod
    def update(cls, data ):
        query = "UPDATE recipes SET name=%(name)s, description=%(description)s, instructions=%(instructions)s, date_made=%(date_made)s, under_30=%(under_30)s, user_id=%(user_id)s, updated_at=NOW() where id= %(id)s;"
        return connectToMySQL('recipes').query_db( query, data )

    @classmethod
    def delete(cls, data):
        query = "DELETE FROM recipes WHERE id=%(id)s;"
        return connectToMySQL('recipes').query_db( query, data )

    @classmethod
    def get_one(cls, data):
        query= "SELECT * FROM recipes WHERE id=%(id)s;"
        results = connectToMySQL('recipes').query_db(query, data)  #we have to pass in data here because we need a specific ID (see blow)
        return cls(results[0]) 
# must be results of class so we can pass results back in to class init to pull apart attributes

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM recipes;"
        results = connectToMySQL('recipes').query_db(query)  
        # print(results)
        recipes = []
        for recipe in results:
            recipes.append(cls(recipe))
        return recipes


    @classmethod
    def get_all_recipes_with_user(cls):
        query = "SELECT * FROM recipes JOIN users ON recipes.user_id=users.id;"
        results = connectToMySQL('recipes').query_db(query)
        # print(f"Results for all recipes with user: {results}")
        results_sorted=sorted(
        results,
        key=lambda x: datetime.strftime(x['created_at'], '%m/%d/%y %H:%M:%S'), reverse=True)
        # a whole lot of googling and stitching together pieces of stuff for this
        all_recipes=[ ]
        for row in results_sorted:
            one_recipe = cls(row)

            one_recipe_creator_info={
                "id":row["users.id"],
                "first_name": row['first_name'],
                "last_name": row['last_name'],
                "email": row['email'],
                "password": row['password'],
                "created_at": row['users.created_at'],
                "updated_at": row['users.updated_at']
            }

            creator= user.User(one_recipe_creator_info)
            one_recipe.creator = creator
            all_recipes.append(one_recipe)
            # print(one_recipe)
            # print(one_recipe.creator)
        return all_recipes

    @classmethod
    def get_recipe_by_id(cls, data):
        query = "SELECT * FROM recipes JOIN users ON recipes.user_id=users.id WHERE recipes.id=%(id)s;"
        results = connectToMySQL('recipes').query_db(query,data)
        # print(f"Results for all recipes with user: {results}")
        all_recipes=[ ]
        for row in results:
            one_recipe = cls(row)

            one_recipe_creator_info={
                "id":row["users.id"],
                "first_name": row['first_name'],
                "last_name": row['last_name'],
                "email": row['email'],
                "password": row['password'],
                "created_at": row['users.created_at'],
                "updated_at": row['users.updated_at']
            }

            creator= user.User(one_recipe_creator_info)
            one_recipe.creator = creator
            all_recipes.append(one_recipe)
            # print(one_recipe)
            # print(one_recipe.creator)
        return all_recipes


    @classmethod
    def create_favorite(cls,data):
        query = "INSERT INTO favorites (user_id, post_id, created_at, updated_at ) VALUES (%(user_id)s, %(post_id)s, NOW() , NOW() );"
        return connectToMySQL('recipes').query_db( query, data )

    @classmethod
    def get_all_recipe_favorite_of_users(cls):
        query = "SELECT * FROM recipes JOIN favorites ON recipes.id=recipe_id JOIN users ON favorites.user_id=users.id;"
        results = connectToMySQL('recipes').query_db(query)
        # print(f"Results for favorites of recipe: {results}")
        results_sorted=sorted(
        results,
        key=lambda x: datetime.strftime(x['comments.created_at'], '%m/%d/%y %H:%M:%S'), reverse=True)
        all_favorites=[ ]
        for row in results_sorted:
            # one_post = cls(row)
            # one_post_author_info={
            #     "id":row["users.id"],
            #     "first_name": row['first_name'],
            #     "last_name": row['last_name'],
            #     "email": row['email'],
            #     "password": row['password'],
            #     "created_at": row['users.created_at'],
            #     "updated_at": row['users.updated_at']
            # }
            one_favorite = {
                "id":row["favorites.id"],
                "user_id":row["favorites.user_id"],
                "post_id":row["recipe_id"],
                "first_name":row["first_name"],
                "last_name":row["last_name"],
                "created_at": row['comments.created_at'],
                "updated_at": row['comments.updated_at']
            }
            # author= user.User(one_post_author_info)
            # one_post.creator = author
            # one_post.comments_on_post.append(one_comment)
            # all_posts.append(one_post)
            all_favorites.append(one_favorite)
            # print(one_post)
            # print(one_post.creator)
        return all_favorites

    @classmethod
    def delete_comment(cls, data):
        query = "DELETE FROM favorites WHERE id=%(id)s;"
        return connectToMySQL('recipes').query_db( query, data )



    # @classmethod
    # def get_comments_on_post(cls,data):
    #     query = "SELECT * FROM recipes LEFT JOIN comments ON comments.post_id=recipes.id LEFT JOIN users ON comments.user_id=users.id WHERE recipes.id=%(id)s";
    #     results = connectToMySQL('books').query_db(query, data)
    #     # print(results)
    #     recipe = cls(results[0])
    #     for row in results:
    #         user_data = {
    #             "id":row["id"],
    #             "first_name": row['first_name'],
    #             "last_name": row['last_name'],
    #             "email": row['email'],
    #             "password": row['password'],
    #             "created_at": row['created_at'],
    #             "updated_at": row['updated_at']
    #         }
    #         recipe.comments_on_post.append(user.User(user_data))
    #     # print(recipe)
    #     return recipe



    @staticmethod
    def validate_recipe(data):
        is_valid = True

        if len(data['name']) < 3:
            flash("Recipe name must be at least 3 characters.")
            is_valid=False

        if len(data['description']) < 3:
            flash("Recipe description must be at least 3 characters.")
            is_valid=False

        if len(data['instructions']) < 3:
            flash("Recipe instructions must be at least 3 characters.")
            is_valid=False

        if len(data['date_made']) < 1:
            flash("Date made can not be empty.")
            is_valid=False

        if 'under_30' not in data:
            flash("Please select if the recipe takes less than 30 minutes to make.")
            is_valid=False

        return is_valid