from datetime import datetime, timedelta

from fastapi import APIRouter, Security
from fastapi.security import APIKeyHeader
from jwt import ExpiredSignatureError, DecodeError

import jwt
from app.middlewares.errors import exceptions as ex
from app.config.consts import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/jwt")
api_key = APIKeyHeader(name='Authorization')


@router.post("/access_token")
async def access_token(api_key: str):
    if api_key == 'DFD21DASF754FGDFGD5474fFASF':
        _access_token = await create_access_token(data={"auth": "certified_access"})
        _refresh_token = await create_refresh_token(data={"auth": "certified_access"})
        return {"access_token": _access_token, "refresh_token": _refresh_token, "result": "success"}
    else:
        raise ex.NoKeyMatchEx()


@router.post("/refresh_token")
async def refresh_token(token=Security(api_key)):
    payload = await token_decode(access_token=token)

    if payload["auth"] == "certified_access":
        _access_token = await create_access_token(data={"auth": "certified_access"})
        return {"access_token": _access_token, "result": "success"}
    else:
        raise ex.TokenDecodeEx()


@router.post("/protected")
async def protected(token=Security(api_key)):
    payload = await token_decode(access_token=token)

    if payload["auth"] == "certified_access":
        return {"result": "success", "identity": "certified_access"}
    else:
        raise ex.TokenDecodeEx()


async def create_access_token(data: dict, expires_delta: int = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def create_refresh_token(data: dict, expires_delta: int = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    else:
        expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def token_decode(access_token):
    """
    :param access_token:
    :return:
    """
    try:
        _access_token = access_token.replace("Bearer ", "")
        payload = jwt.decode(_access_token, key=JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except ExpiredSignatureError:
        raise ex.TokenExpiredEx()
    except DecodeError:
        raise ex.TokenDecodeEx()
    return payload


