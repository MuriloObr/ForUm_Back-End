from flask import Flask, jsonify, make_response, request, redirect
from flask_cors import CORS
from querys import *
from os import getenv
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

DB_path = getenv("DATABASE_URL")
secret_key = getenv("JWT_SECRET_KEY")

app = Flask(__name__)
app.debug = True
CORS(app, supports_credentials=True)


messages = {
    400: {
        "message": "Bad request"
    },
    401: {
        "message": "Invalid credentials"
    },
    409: {
        "message": "Conflict, may already exist"
    },
    415: {
        "message": "Unsupported media type"
    },
    204: {
        "message": "Does not exist"
    },
    201: {
        "message": "Created successfully"
    },
    200: {
        "message": "OK"
    },
}


def tokenRequired(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("uid")

        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            uid_token = jwt.decode(token, secret_key, algorithms=["HS256"])

        except Exception as e:
            return jsonify({"message": str(e)}), 401

        return func(uid_token["user_id"], *args, **kwargs)

    return wrapper


# GET


@app.route("/", methods=["GET"])
def helloFlask():
    return jsonify({"message": "Hello from flask"})


@app.route("/api/logged", methods=["GET"])
@tokenRequired
def logged(user_id):
    return jsonify({"res": f"User {user_id} Logged In"}), 200


@app.route("/api/user/<int:userID>", methods=["GET"])
def getUserByID(userID):
    query = DBgetUserByID(userID)
    code = query["code"]

    return jsonify(messages[code], query["res"]), code


@app.route("/api/profile", methods=["GET"])
@tokenRequired
def profile(user_id):
    query = DBgetUserByID(user_id)
    code = query["code"]

    return jsonify(messages[code], query["res"]), code


@app.route("/api/posts/<int:postID>", methods=["GET"])
def getPostByID(postID):
    query = DBgetPostByID(postID)
    code = query["code"]

    return jsonify(messages[code], query["res"]), code


@app.route("/api/posts", methods=["GET"])
def getAllPosts():
    query = DBgetAllPosts()
    code = query["code"]

    return jsonify(messages[code], query["res"]), code


@app.route("/api/posts/user/<int:userID>", methods=["GET"])
def getAllPostsFromUser(userID):
    query = DBgetAllPostsFromUser(userID)
    code = query["code"]

    return jsonify(messages[code], query["res"]), code


@app.route("/api/comments/<int:postID>", methods=["GET"])
def getAllCommentsFromPost(postID):
    query = DBgetAllCommentsFromPost(postID)
    code = query["code"]

    return jsonify(messages[code], query["res"]), code

# POST


@app.route("/api/posts/create", methods=["POST"])
@tokenRequired
def createNewPost(user_id):
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        body = request.json
        operation = DBcreateNewPost(post=body, currentUser=user_id)
        code = operation["code"]

        return jsonify(messages[code], operation["res"]), code

    else:
        return jsonify(messages[415]), 415


@app.route("/api/posts/comment", methods=["POST"])
@tokenRequired
def createNewComment(user_id):
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        body = request.json
        operation = DBcreateNewComment(comment=body, currentUser=user_id)
        code = operation["code"]

        return jsonify(messages[code], operation["res"]), code

    else:
        return jsonify(messages[415]), 415


@app.route("/api/posts/like", methods=["POST", "DELETE"])
@tokenRequired
def likePost(user_id):
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        body = request.json
        if (request.method == "POST"):
            operation = DBlikePost(
                post_id=body["post_id"], currentUser=user_id)
        elif (request.method == "DELETE"):
            operation = DBrmlikePost(
                post_id=body["post_id"], currentUser=user_id)
        code = operation["code"]

        return jsonify(messages[code], operation["res"]), code

    else:
        return jsonify(messages[415]), 415


@app.route("/api/comments/like", methods=["POST", "DELETE"])
@tokenRequired
def likeComment(user_id):
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        body = request.json
        if (request.method == "POST"):
            operation = DBlikeComment(
                comment_id=body["comment_id"], currentUser=user_id)
        elif (request.method == "DELETE"):
            operation = DBrmlikeComment(
                comment_id=body["comment_id"], currentUser=user_id)
        code = operation["code"]

        return jsonify(messages[code], operation["res"]), code

    else:
        return jsonify(messages[415]), 415


@app.route("/api/comments/best", methods=["PUT"])
@tokenRequired
def bestComment(user_id):
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        body = request.json
        operation = DBchooseAnswer(
            post_id=body["post_id"], comment_id=body["comment_id"], currentUser=user_id)
        code = operation["code"]

        return jsonify(messages[code], operation["res"]), code

    else:
        return jsonify(messages[415]), 415


@app.route("/api/posts/view", methods=["POST"])
@tokenRequired
def viewPost(user_id):
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        body = request.json
        operation = DBviewPost(post_id=body["post_id"], currentUser=user_id)
        code = operation["code"]

        return jsonify(messages[code], operation["res"]), code

    else:
        return jsonify(messages[415]), 415


@app.route("/api/posts/closed", methods=["PUT"])
@tokenRequired
def closeOpenPost(user_id):
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        body = request.json
        operation = DBcloseOpenPost(
            post_id=body["post_id"], currentUser=user_id)
        code = operation["code"]

        return jsonify(messages[code], operation["res"]), code

    else:
        return jsonify(messages[415]), 415


@app.route("/api/register", methods=["POST"])
def createNewUser():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        body = request.json
        operation = DBcreateNewUser(body)
        code = operation["code"]

        return jsonify(messages[code], operation["res"]), code

    else:
        return jsonify(messages[415]), 415


@app.route("/api/login", methods=["POST"])
def login():
    content_type = request.headers.get('Content-type')
    if (content_type == 'application/json'):
        body = request.json
        operation = DBlogin(body["user"], body["password"])
        code = operation["code"]

        if code == 200:
            response = make_response(jsonify({
                "message": f"Usuário {body['user']} logado"
            }))
            response.set_cookie(
                key="uid",
                value=operation["res"],
                httponly=True,
                samesite=None
            )
        else:
            response = jsonify({"message": operation["res"]})

        return response, code
    else:
        return jsonify(messages[415]), 415


@app.route("/api/logout", methods=["POST"])
@tokenRequired
def logout(user_id):
    response = make_response(
        jsonify({"message": f"User {user_id} have logged out"}))
    response.set_cookie(key="uid", expires=0)
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
