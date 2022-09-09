from flask_app import app
from flask import render_template,redirect,request,session,flash
from flask_app.models.user import User
from flask_app.models.recipe import Recipe
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route("/")
def portfolio_home():
    return render_template("portfolio_home.html")

@app.route("/l&r")
def index():
    return render_template("l&r.html")

@app.route("/register", methods=["post"])
def register():
    if not User.validate_user(request.form):
        print("reg failed")
        session["first_name"] = request.form["first_name"]
        session["last_name"] = request.form["last_name"]
        session["email"] = request.form["email"]
        session.pop('login_email', None)
        return redirect("/l&r")
    
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    # print(pw_hash)
    data= {
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"],
        "email": request.form["email"],
        "password": pw_hash
    }
    id= User.save(data)
    session["id"]= id
    session.pop("first_name", None)
    session.pop("last_name", None)
    session.pop("email", None)
    # print(session["id"])
    print("reg received")
    return redirect(f"/dashboard")

@app.route("/login", methods=["post"])
def login():
    if not User.validate_login(request.form):
        print("login failed")

        session.pop("first_name", None)
        session.pop("last_name", None)
        session.pop("email", None)
        session["login_email"] = request.form["email"]
        return redirect("/l&r")
    else:
        session['email'] = request.form['email']
        data = {
            "email": session['email']
        }
        user = User.get_one_email(data)
        session['id']= user.id        
        print("login received")
        return redirect("/dashboard")
        # return redirect(f"/dashboard/{id}")

@app.route("/forgot_email_pw")
def punkd():
    return render_template("rekt.html")

# @app.route("/dashboard/<id>")
# def dashboard(id):
@app.route("/dashboard")
def dashboard():
    # print(type(id))
    # print(type(session["id"]))
    if 'id' in session:
        data={
            "id":session['id']
        }
        session.pop("first_name", None)
        session.pop("last_name", None)
        session.pop("email", None)
        session.pop("login_email", None)
        user=User.get_one_id(data)
        # recipes=Recipe.get_all_recipes_with_user()
        user_with_favorites=User.get_favorite_recipes(data)
        if user_with_favorites:
            favorites=user_with_favorites.favorite_recipes
            # print("HEY THESE ARE THE FAVORITES", favorites)
            return render_template("dashboard.html", user=user, recipes=Recipe.get_all_recipes_with_user(), favorites=favorites)
        else:
            return render_template("dashboard.html", user=user, recipes=Recipe.get_all_recipes_with_user())
    else:
        return redirect("/l&r")

@app.route("/add_to_favorites/<int:id>")
def add_to_favorites(id):
    if 'id' in session:
        data={
            'id': session['id'],
            'user_id': session['id'],
            'recipe_id': id
        }
        if not User.add_favorite(data):
            flash("This recipe is already in your favorites.")
            return redirect("/dashboard")
        else:
            return redirect("/dashboard")
    else:
        return redirect("/l&r")

@app.route("/delete_from_favorites", methods=["post"])
def delete_from_favorites():

    if "id" not in session:
        return redirect("/l&r")
    else:
        data={
            "user_id":request.form["user_id"],
            "recipe_id":request.form["recipe_id"]
        }
        User.delete_favorite(data)
        return redirect ("/dashboard")

@app.route("/logout", methods=["post"])
def logout():
    session.clear()
    # session['id']=0
    return redirect("/l&r")