#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        username = request.get_json().get("username")
        image_url = request.get_json().get("image_url")
        bio = request.get_json().get("bio")
        password = request.get_json().get("password")

        if username:
            user = User(username = username, image_url = image_url, bio = bio)
            user.password_hash = password

            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id

            return user.to_dict(), 201
        return {"error": "Invalid entry"}, 422

class CheckSession(Resource):
    def get(self):
        user_id = session["user_id"]
        if user_id:
            current_user = User.query.filter(User.id == user_id).first()
            return current_user.to_dict(), 200
        return {"error": "Not logged in."}, 401

class Login(Resource):
    def post(self):
        username = request.get_json().get("username")
        password = request.get_json().get("password")
        user = User.query.filter(User.username == username).first()
        if user:            
            if user.authenticate(password):
                session["user_id"] = user.id
                return user.to_dict(), 200
        return {"error": "Invalid information"}, 401

@app.before_request
def check_for_logged_in():
    basic_endpoints = ["signup", "check_session", "login"]
    if request.endpoint not in basic_endpoints and not session.get("user_id"):
        return {"error": "Not logged in."}, 401            

class Logout(Resource):
    def delete(self):
        print(session["user_id"])       
        session["user_id"] = None
        return {}, 204

class RecipeIndex(Resource):
    def get(self):
        user = User.query.filter(User.id == session["user_id"]).first()
        recipe_list = [n.to_dict() for n in user.recipes]

        return recipe_list, 200

    def post(self):
        title = request.get_json()["title"]
        instructions = request.get_json()["instructions"]
        minutes_to_complete = request.get_json()["minutes_to_complete"]

        if title and instructions and minutes_to_complete and len(instructions) >= 50:
            new_recipe = Recipe(title = title)
            new_recipe.instructions = instructions
            new_recipe.minutes_to_complete = minutes_to_complete
            new_recipe.user_id = session["user_id"]

            db.session.add(new_recipe)
            db.session.commit()

            return new_recipe.to_dict(), 201
        return {"error": "Invalid entry"}, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)