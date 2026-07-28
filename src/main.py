import jwt
from os import getenv
from typing import Annotated, Union
from fastapi import FastAPI, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from src.comment_actions import create_new_comment, get_all_comments_from_post, like_comment, rm_like_comment
from src.post_actions import choose_answer, close_or_open_post, create_new_post, delete_post, get_all_posts, get_all_posts_from_user, get_post_by_id, like_post, rm_like_post, view_post
from src.user_actions import create_new_user, get_user_by_id, login_with_user_or_email
from utils.api_types import (
    BestCommentRef, CommentRef, CommentResponse, LoggedResponse,
    MessageResponse, NewComment, NewPost, NewUser, PostRef,
    PostResponse, UIDToken, UserPayload, UserResponse,
)

app = FastAPI()

cors_raw = getenv("CORS_ORIGINS", "")
origins = [o.strip() for o in cors_raw.split(",") if o.strip()]

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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    try:
      uid_token = jwt.decode(uid, secret_key, algorithms=["HS256"])
      return UIDToken.model_validate(uid_token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Error: {e}")

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/api/logged", response_model=LoggedResponse)
async def logged(uid_token: Annotated[UIDToken, Depends(token_validation)]):
    return {"res": f"User {uid_token.user_id} Logged In"}


@app.get("/api/profile", response_model=UserResponse)
def profile(uid_token: Annotated[UIDToken, Depends(token_validation)]):
    query = get_user_by_id(uid_token.user_id)
    if query[0] is not None:
        return query[0]
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=query[1])


@app.get("/api/user/{userID}", response_model=UserResponse)
async def getUserByID(userID: int):
    query = get_user_by_id(userID)
    if query[0] is not None:
        if not query[0]:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        return query[0]
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=query[1])


@app.get("/api/posts/{postID}", response_model=PostResponse)
async def getPostByID(postID: int):
    query = get_post_by_id(postID)
    if query[0] is not None:
        if not query[0]:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        return query[0]
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=query[1])


@app.get("/api/posts", response_model=list[PostResponse])
def getAllPosts():
    query = get_all_posts()
    if query[0] is not None:
        if not query[0]:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        return query[0]
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=query[1])


@app.get("/api/posts/user/{userID}", response_model=list[PostResponse])
def getAllPostsFromUser(userID: int):
    query = get_all_posts_from_user(userID)
    if query[0] is not None:
        if not query[0]:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        return query[0]
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=query[1])


@app.get("/api/comments/{postID}", response_model=list[CommentResponse])
def getAllCommentsFromPost(postID: int):
    query = get_all_comments_from_post(postID)
    if query[0] is not None:
        if not query[0]:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        return query[0]
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=query[1])


@app.post("/api/posts/create", response_model=PostResponse)
def createNewPost(uid_token: Annotated[UIDToken, Depends(token_validation)], new_post: NewPost):
    task = create_new_post(post=new_post, currentUser=uid_token.user_id)
    if task[0]:
        return task[0]
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=task[1])


@app.delete("/api/posts/delete/{postID}", response_model=MessageResponse)
def deletePost(uid_token: Annotated[UIDToken, Depends(token_validation)], postID: int):
    task = delete_post(post_id=postID, currentUser=uid_token.user_id)
    if task[0]:
        return {"message": task[0]}
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=task[1])


@app.post("/api/posts/comment", response_model=CommentResponse)
def createNewComment(uid_token: Annotated[UIDToken, Depends(token_validation)], new_comment: NewComment):
    task = create_new_comment(comment=new_comment, currentUser=uid_token.user_id)
    if task[0]:
        return task[0]
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=task[1])


@app.post("/api/posts/like", response_model=MessageResponse)
def likePost(uid_token: Annotated[UIDToken, Depends(token_validation)], post_ref: PostRef):
    task = like_post(post_id=post_ref.post_id, currentUser=uid_token.user_id)
    if task[0]:
        return {"message": task[0]}
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=task[1])


@app.delete("/api/posts/like", response_model=MessageResponse)
def unlikePost(uid_token: Annotated[UIDToken, Depends(token_validation)], post_ref: PostRef):
    task = rm_like_post(post_id=post_ref.post_id, currentUser=uid_token.user_id)
    if task[0]:
        return {"message": task[0]}
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=task[1])


@app.post("/api/comments/like", response_model=MessageResponse)
def likeComment(uid_token: Annotated[UIDToken, Depends(token_validation)], comment_ref: CommentRef):
    task = like_comment(comment_id=comment_ref.comment_id, currentUser=uid_token.user_id)
    if task[0]:
        return {"message": task[0]}
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=task[1])


@app.delete("/api/comments/like", response_model=MessageResponse)
def unlikeComment(uid_token: Annotated[UIDToken, Depends(token_validation)], comment_ref: CommentRef):
    task = rm_like_comment(comment_id=comment_ref.comment_id, currentUser=uid_token.user_id)
    if task[0]:
        return {"message": task[0]}
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=task[1])


@app.put("/api/comments/best", response_model=MessageResponse)
def bestComment(uid_token: Annotated[UIDToken, Depends(token_validation)], best_comment_ref: BestCommentRef):
    task = choose_answer(
        post_id=best_comment_ref.post_id,
        comment_id=best_comment_ref.comment_id,
        currentUser=uid_token.user_id,
    )
    if task[0]:
        return {"message": task[0]}
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=task[1])


@app.post("/api/posts/view", response_model=MessageResponse)
def viewPost(uid_token: Annotated[UIDToken, Depends(token_validation)], post_ref: PostRef):
    task = view_post(post_id=post_ref.post_id, currentUser=uid_token.user_id)
    if task[0]:
        return {"message": task[0]}
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=task[1])


@app.put("/api/posts/closed", response_model=MessageResponse)
def closeOpenPost(uid_token: Annotated[UIDToken, Depends(token_validation)], post_ref: PostRef):
    task = close_or_open_post(post_id=post_ref.post_id, currentUser=uid_token.user_id)
    if task[0]:
        return {"message": task[0]}
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=task[1])


@app.post("/api/register", response_model=MessageResponse)
def createNewUser(new_user: NewUser):
    task = create_new_user(new_user)
    if task[0]:
        return {"message": task[0]}
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=task[1])


@app.post("/api/login", response_model=MessageResponse)
def login(user: UserPayload, response: Response):
    task = login_with_user_or_email(user.user, user.password)
    if task[0]:
        response.set_cookie(key="uid", value=task[0], samesite="lax")
        return {"message": "Cookies!"}
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=task[1])


@app.post("/api/logout", response_model=MessageResponse)
def logout(uid_token: Annotated[UIDToken, Depends(token_validation)], response: Response):
    response.set_cookie(key="uid", expires=0)
    return {"message": f"User:{uid_token.user_id} logged out"}
