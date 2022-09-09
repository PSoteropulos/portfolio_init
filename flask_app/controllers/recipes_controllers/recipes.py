import re
from flask_app import app
from flask import render_template,redirect,request,session,flash
from datetime import datetime
from flask_app.models.recipe import Recipe 
from flask_app.models.user import User
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route("/new_recipe")
def new_recipe():
    if "id" not in session:
        return redirect("/l&r")
    else:
        id= {"id": session['id']}
        user=User.get_one_id(id)
        print(session)
        return render_template("new_recipe.html", user=user)

@app.route("/create_recipe", methods=["post"])
def create_recipe():
    # print(request.form)
    if "id" not in session:
        return redirect("/l&r")
    else:
        if not Recipe.validate_recipe(request.form):
            session['name'] = request.form['name']
            session['description'] = request.form['description']
            session['instructions'] = request.form['instructions']
            session['date_made'] = request.form['date_made']
            if 'under_30' in request.form:
                session['under_30'] = request.form['under_30']
            #     print(session['under_30'])
            # print(session['name'])
            # print(session['description'])
            # print(session['instructions'])
            # print(session['date_made'])
            return redirect("/new_recipe")
    
        else:
            data = {
            'name': request.form['name'],
            'description': request.form['description'],
            'instructions': request.form['instructions'],
            'date_made': request.form['date_made'],
            'under_30': request.form['under_30'],
            'user_id': request.form['user_id']
            }
            session.pop('name', None)
            session.pop('description', None)
            session.pop('instructions', None)
            session.pop('date_made', None)
            if 'under_30' in session:
                session.pop('under_30', None)
        Recipe.save(data)
        return redirect (f"/dashboard")

@app.route("/view_recipe/<int:id>")
def view_recipe(id):
    if "id" not in session:
        return redirect("/l&r")
    else:
        user_id= {"id": session['id']}
        user=User.get_one_id(user_id)
        recipe_id= {"id": id}
        recipe=Recipe.get_recipe_by_id(recipe_id)[0]
        print(session)
        return render_template(f"view_recipe.html", user=user, recipe=recipe)

@app.route("/delete_recipe", methods=["post"])
def delete_recipe():
    if "id" not in session:
        return redirect("/l&r")
    else:
        recipe_id={
            "id":request.form["recipe_id"]
        }
        Recipe.delete(recipe_id)
        return redirect (f"/dashboard")

@app.route("/edit_recipe/<int:id>")
def edit_recipe(id):
    if "id" not in session:
        return redirect("/l&r")
    else:
        user_id= {"id": session['id']}
        user=User.get_one_id(user_id)
        recipe_id= {"id": id}
        recipe=Recipe.get_recipe_by_id(recipe_id)[0]
        if user.id == recipe.creator.id:
            return render_template(f"edit_recipe.html", user=user, recipe=recipe)
        else:
            return redirect("/dashboard")

@app.route("/submit_edit_recipe", methods=["post"])
def submit_edit_recipe():
    # print(request.form)
    if "id" not in session:
        return redirect("/l&r")
    else:
        if not Recipe.validate_recipe(request.form):
            return redirect(f"/edit_recipe/{request.form['recipe_id']}")    
        else:
            data = {
            'id': request.form['recipe_id'],
            'name': request.form['name'],
            'description': request.form['description'],
            'instructions': request.form['instructions'],
            'date_made': request.form['date_made'],
            'under_30': request.form['under_30'],
            'user_id': request.form['user_id']
            }
        Recipe.update(data)
        return redirect (f"/dashboard")