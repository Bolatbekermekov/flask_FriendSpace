from functools import wraps
from flask_restx import Api, Resource, Namespace, fields
from flaskblog.database import Posts, db, Users
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from flask import request
from flaskblog import app
from flask_jwt_extended import create_access_token

# from main import posts

# Create Api service
authorizations = {
        "Bearer Auth":{
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
        }
}
api = Api(doc='/api',
          title="ContentGuard API",
          description="Our API service provides comprehensive filtering and removal of profanity, ensuring a clean and safe environment for user-generated content. Easily integrate our solution to moderate and sanitize text input, creating a more respectful online space.",
          authorizations=authorizations,
          security="Bearer Auth"
          )

ns = Namespace('api')
auth = HTTPBasicAuth()
api.init_app(app)
api.add_namespace(ns)



blacklist = set()




@auth.verify_password
def verify_password(username, password):
    user = Users.query.filter_by(username=username).first()
    if user and username == "admin":
        if check_password_hash(user.password_hash, password):
            token = jwt.encode({'username': username}, 'secret_key', algorithm='HS256')
            return {'token': token}
    return False
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return {'message': 'You have successfully logged Out'}, 401
        return f(*args, **kwargs)
    return decorated


@ns.route('/logout_admin')
class LogoutAdmin(Resource):
    @token_required
    @ns.doc(description="Logout Admin by invalidating the token")
    def post(self):
        """
                Invalidate the token and log out the admin.

        """
        pass

posts_model = api.model('Posts', {
    "id": fields.Integer,
    "title": fields.String,
    "content": fields.String,
    "slug": fields.String,
    "date_posted": fields.DateTime,
    "poster_id": fields.Integer
})
posts_input_model = api.model("PostsInput", {
    "title": fields.String,
    "content": fields.String,
    "slug": fields.String

})
@ns.route('/hello')
class Hello(Resource):
    def get(self):
        return f"Hello World!"


@ns.route('/postsapi')
class PostsListAPI(Resource):
    @auth.login_required
    @ns.marshal_list_with(posts_model)
    @ns.doc(description="Get all posts")
    def get(self):
        """
            Retrieve all posts
        """
        return Posts.query.all()


@ns.route("/posts/<int:id>")
class PostApi(Resource):
    @auth.login_required
    @ns.marshal_list_with(posts_model)
    @ns.doc(description="Retrieve a post based on ID")
    def get(self, id):
        """
               Retrieve a single post by ID
               """
        post = Posts.query.get(id)
        return post

    @auth.login_required
    @ns.expect(posts_input_model)
    @ns.marshal_list_with(posts_model)
    @ns.doc(description="Edit a specific post using ID")
    def put(self, id):
        """
               Update a single post by ID
        """
        post = Posts.query.get(id)
        post.title = ns.payload['title']
        post.content = ns.payload['content']
        post.slug = ns.payload['slug']
        post.poster_id = ns.payload['poster_id']
        db.session.commit()

    @auth.login_required
    @ns.expect(posts_input_model)
    @ns.marshal_list_with(posts_model)
    @ns.doc(description="Create a post with an assigned ID")
    def post(self, id):
        """
                Create a new post by id
        """
        user = Users.query.get(id)

        if user:
            new_post = Posts(
                title=ns.payload['title'],
                content=ns.payload['content'],
                slug=ns.payload['slug'],
                poster_id=id  # Associate the post with the user by using their unique ID
            )
            db.session.add(new_post)
            db.session.commit()
            return new_post, 201
        else:
            return {'message': 'User not found'}, 404

    @auth.login_required
    @ns.doc(description="Remove a post by its ID")
    def delete(self, id):
        """
                Delete a single post by ID
        """
        post = Posts.query.get(id)
        db.session.delete(post)
        db.session.commit()
        return {}, 204


users_model = api.model('UsersInput', {
    "id": fields.Integer,
    "username": fields.String,
    "name": fields.String,
    "email": fields.String,
    "date_added": fields.DateTime,
    "password_hash": fields.String,
    "posts": fields.List(fields.Nested(posts_model))
})
users_input_model = api.model('Users', {
    "username": fields.String,
    "name": fields.String,
    "email": fields.String,
    "password_hash": fields.String
})


@ns.route('/usersapi')
class UsersListAPI(Resource):
    @auth.login_required
    @ns.marshal_list_with(users_model)
    @ns.doc(description="Get complete list of users")
    def get(self):
        """
                Retrieve all users
        """
        return Users.query.all()

    @auth.login_required
    @ns.expect(users_input_model)
    @ns.marshal_list_with(users_model)
    @ns.doc(description="Register a new user")
    def post(self):
        """
                Create a new user
        """
        print(ns.payload)
        users = Users(
            username=ns.payload['username'],
            name=ns.payload['name'],
            email=ns.payload['email'],
            password_hash=ns.payload['password_hash'])
        db.session.add(users)
        db.session.commit()
        return users, 201


@ns.route("/users/<int:id>")
class UserApi(Resource):
    @auth.login_required
    @ns.marshal_list_with(users_model)
    @ns.doc(description="Get a user by ID")
    def get(self, id):
        """
                Retrieve a user by ID
        """
        user = Users.query.get(id)
        return user

    @auth.login_required
    @ns.expect(users_input_model)
    @ns.marshal_list_with(users_model)
    @ns.doc(description="Edit user by ID")
    def put(self, id):
        """
               Update a user by ID
        """
        user = Users.query.get(id)
        user.username = ns.payload['username']
        user.name = ns.payload['name']
        user.email = ns.payload['email']
        user.password_hash = ns.payload['password_hash']
        db.session.commit()

    @auth.login_required
    @ns.doc(description="Remove a user by ID")
    def delete(self, id):
        """
               Delete a user by ID
        """
        user = Users.query.get(id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return {}, 204
        return {'message': 'User not found'}, 404
