#coding:utf-8
from flask import request
from flask_httpauth import HTTPTokenAuth

from config import TOKEN_SCHEME

token_auth = HTTPTokenAuth(scheme=TOKEN_SCHEME)

@token_auth.verify_token
def verify_token(token):
    if not token:
        return True
    return True
