from fastapi import APIRouter, Body, Header, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from web_server.extensions import password_hasher, token_manager
from web_server.models import User
from typing import Optional

api = APIRouter()
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#
#
# class LoginBody(BaseModel):
#     email: str
#     password: Optional[str]
#     token: Optional[str]
#
#
# @api.get("/")
# def get_test(token: str = Depends(oauth2_scheme)):
#     return {"token": token}
#
#
# @api.post("/login")
# def login_post(data: LoginBody = Body(None, help="The login information")):
#     user = User.get_by_email(data.email)
#     if user is not None:
#         if user.password is not None:
#             if user.verify_password(data.password):
#                 # login user and return a JsonWebToken to use for auth and session storage
#                 pass
#             else:
#                 pass
#                 # return message stating that the password is wrong
#
#         elif user.token is not None:
#             token = token_manager.validate_token(user.token)
#             if token:
#                 pass
#
#     else:
#         pass
#         # return a message stating that the user does not exist
