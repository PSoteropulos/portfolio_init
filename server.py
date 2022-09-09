from flask_app import app
from flask_app.controllers.adventure_controllers import adventures
from flask_app.controllers.recipes_controllers import recipes
from flask_app.controllers.recipes_controllers import users

if __name__ == "__main__":
    app.run(debug=True)