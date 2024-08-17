import jwt
from os import getenv
from typing import Annotated, Union
from fastapi import FastAPI, Cookie,Depends, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from src.comment_actions import create_new_comment, get_all_comments_from_post, like_comment, rm_like_comment
from src.post_actions import choose_answer, close_or_open_post, create_new_post, delete_post, get_all_posts, get_all_posts_from_user, get_post_by_id, like_post, rm_like_post, view_post
from src.user_actions import create_new_user, get_user_by_id, login_with_user_or_email
from utils.api_types import BestCommentRef, CommentRef, NewComment, NewPost, NewUser, PostRef, UIDToken, UserPayload

app = FastAPI()

origins = [
    "http://25.6.211.62:5173",
    "https://for-um-front-end.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

secret_key = getenv("JWT_SECRET_KEY")

def token_validation(uid: Union[str, None] = Cookie(None)):
    if not uid:
        return {"message": "Token is missing"}

    try:
      uid_token = jwt.decode(uid, secret_key, algorithms=["HS256"])
      return UIDToken.model_validate(uid_token)
    except Exception as e:
        return f"Error: {e}"

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/api/logged")
async def logged(uid_token: Annotated[UIDToken, Depends(token_validation)]):
    return {"res": f"User {uid_token.user_id} Logged In"}


@app.get("/api/profile")
def profile(uid_token: Annotated[UIDToken, Depends(token_validation)], response: Response):
    query = get_user_by_id(uid_token.user_id)
    if query[0] is not None:
        return query[0]
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return query[1]


@app.get("/api/user/{userID}")
async def getUserByID(userID: int, response: Response):
    query = get_user_by_id(userID)
    if query[0] is not None:
        if not query[0]:
            response.status_code = status.HTTP_204_NO_CONTENT
        return query[0]
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return query[1]


@app.get("/api/posts/{postID}")
async def getPostByID(postID: int, response: Response):
    query = get_post_by_id(postID)
    if query[0] is not None:
        if not query[0]:
            response.status_code = status.HTTP_204_NO_CONTENT
        return query[0]
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return query[1]


@app.get("/api/posts")# TODO - Adicionar paginação
def getAllPosts(response: Response):
    query = get_all_posts()
    print(query)
    if query[0] is not None:
        if not query[0]:
            response.status_code = status.HTTP_204_NO_CONTENT
        return query[0]
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return query[1]


@app.get("/api/posts/user/{userID}")# TODO - Adicionar paginação
def getAllPostsFromUser(userID: int, response: Response):
    query = get_all_posts_from_user(userID)
    if query[0] is not None:
        if not query[0]:
            response.status_code = status.HTTP_204_NO_CONTENT
        return query[0]
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return query[1]


@app.get("/api/comments/{postID}")# TODO - Adicionar paginação
def getAllCommentsFromPost(postID: int, response: Response):
    query = get_all_comments_from_post(postID)
    if query[0] is not None:
        if not query[0]:
            response.status_code = status.HTTP_204_NO_CONTENT
        return query[0]
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return query[1]


@app.post("/api/posts/create")
def createNewPost(uid_token: Annotated[UIDToken, Depends(token_validation)], new_post: NewPost, response: Response):
    task = create_new_post(post=new_post, currentUser=uid_token.user_id)
        
    if task[0] is not None:
            return task[0]
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return task[1]


@app.delete("/api/posts/delete/{postID}")
def deletePost(uid_token: Annotated[UIDToken, Depends(token_validation)], postID: int, response: Response):
    task = delete_post(post_id=postID, currentUser=uid_token.user_id)

    if task[0] is not None:
        return task[0]
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return task[1]


@app.post("/api/posts/comment")
def createNewComment(uid_token: Annotated[UIDToken, Depends(token_validation)], new_comment: NewComment, response: Response):
    task = create_new_comment(comment=new_comment, currentUser=uid_token.user_id)

    if task[0] is not None:
        return task[0]
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return task[1]


@app.route("/api/posts/like", methods=["POST", "DELETE"])
def likePost(uid_token: Annotated[UIDToken, Depends(token_validation)], post_ref: PostRef, request: Request, response: Response):
    if (request.method == "POST"):
        task = like_post(
            post_id=post_ref.post_id, currentUser=uid_token.user_id)
    elif (request.method == "DELETE"):
        task = rm_like_post(
            post_id=post_ref.post_id, currentUser=uid_token.user_id)

    if task[0] is not None:
        return task[0]
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return task[1]


@app.route("/api/comments/like", methods=["POST", "DELETE"])
def likeComment(uid_token: Annotated[UIDToken, Depends(token_validation)], comment_ref: CommentRef, request: Request, response: Response):
    if (request.method == "POST"):
        task = like_comment(
            comment_id=comment_ref.comment_id, currentUser=uid_token.user_id)
    elif (request.method == "DELETE"):
        task = rm_like_comment(
            comment_id=comment_ref.comment_id, currentUser=uid_token.user_id)

    if task[0] is not None:
        return task[0]
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return task[1]


@app.put("/api/comments/best")
def bestComment(uid_token: Annotated[UIDToken, Depends(token_validation)], best_comment_ref: BestCommentRef, response: Response):
    task = choose_answer(
        post_id=best_comment_ref.post_id, 
        comment_id=best_comment_ref.comment_id, 
        currentUser=uid_token.user_id
    )

    if task[0] is not None:
        return task[0]
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return task[1]


@app.post("/api/posts/view")
def viewPost(uid_token: Annotated[UIDToken, Depends(token_validation)], post_ref: PostRef, response: Response):
    task = view_post(post_id=post_ref.post_id, currentUser=uid_token.user_id)

    if task[0] is not None:
        return task[0]
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return task[1]


@app.put("/api/posts/closed")
def closeOpenPost(uid_token: Annotated[UIDToken, Depends(token_validation)], post_ref: PostRef, response: Response):
    task = close_or_open_post(
        post_id=post_ref.post_id, 
        currentUser=uid_token.user_id
    )

    if task[0] is not None:
        return task[0]
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return task[1]


@app.post("/api/register")
def createNewUser(new_user: NewUser, response: Response):
    task = create_new_user(new_user)

    if task[0] is not None:
        return task[0]
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return task[1]


@app.post("/api/login")
def login(user: UserPayload, response: Response):
    task = login_with_user_or_email(user.user, user.password)

    if task[0] is not None:
        response.set_cookie(
        key="uid",
        value=task[0],
        secure=True,
        samesite="none"
        )
        return { "message": "Cookies!" }
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return task[1]

    



@app.post("/api/logout")
def logout(uid_token: Annotated[UIDToken, Depends(token_validation)], response: Response):
    response.set_cookie(key="uid", expires=0)
    return { "message": f"User:{uid_token.user_id} logged out" }