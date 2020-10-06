from fastapi import APIRouter, Body, Header
from pydantic import BaseModel
from web_server.extensions import password_hasher, token_manager
from web_server.models import User


api = APIRouter()


class LoginBody(BaseModel):
    email: str
    password: str


@api.post("/login")
def login_post(data: LoginBody = Body(None, help="The login information")):
    user = User.get_by_email(data.email)
    if user is not None:
        if user.verify_password(data.password):
            pass
            # login user and return a JsonWebToken to use for auth and session storage
        else:
            pass
            # return message stating that the password is wrong
    else:
        pass
        # return a message stating that the user does not exist
