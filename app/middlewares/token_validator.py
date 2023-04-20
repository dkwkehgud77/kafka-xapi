import copy
import json
import re
import sys
import time
import traceback
from json import JSONDecodeError

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import Message

from app.config.consts import EXCEPT_PATH_LIST, EXCEPT_PATH_REGEX
from app.config.logger import api_logger, Logger
from app.middlewares.errors.exceptions import APIException

from app.utils.date_utils import D

logger = Logger().get_instance().logger


async def set_body(request: Request, body: bytes):
    async def receive() -> Message:
        return {"type": "http.request", "body": body}

    request._receive = receive


async def get_body(request: Request) -> bytes:
    body = await request.body()
    await set_body(request, body)
    return body


async def access_control(request: Request, call_next):
    request.state.req_time = D.datetime()
    request.state.start = time.time()
    request.state.inspect = None
    request.state.user = None
    request.state.service = None
    await set_body(request, await request.body())
    request.state.payload = await get_body(request)

    # 클라이언트의 IP 주소를 설정
    ip = request.headers["x-forwarded-for"] if "x-forwarded-for" in request.headers.keys() else request.client.host
    request.state.ip = ip.split(",")[0] if "," in ip else ip

    url = request.url.path
    # EXCEPT_PATH_LIST = ["/", "/openapi.json"]
    # EXCEPT_PATH_REGEX = "^(/docs|/redoc|/api/auth)"
    if await url_pattern_check(url, EXCEPT_PATH_REGEX) or url in EXCEPT_PATH_LIST:
        response = await call_next(request)
        if url != "/":
            await api_logger(request=request, response=response)
        return response

    # API 요청인 경우
    try:
        response = await call_next(request)
        await api_logger(request=request, response=response)
    except (BaseException, Exception) as ex:
        logger.error(f"Exception occurred: {ex}\n{traceback.format_exc()}")
        error = await exception_handler(ex)
        error_dict = dict(status=error.status_code, msg=error.msg, detail=error.detail, code=error.code)
        response = JSONResponse(status_code=error.status_code, content=error_dict)
        request.state.traceback = traceback.extract_tb(ex.__traceback__)
        await api_logger(request=request, error=error)
    finally:
        return response


async def url_pattern_check(path, pattern):
    result = re.match(pattern, path)
    if result:
        return True
    return False


async def exception_handler(error: Exception):
    # print(error)
    # if isinstance(error, sqlalchemy.exc.OperationalError):
    #     error = SqlFailureEx(ex=error)
    if not isinstance(error, APIException):
        error = APIException(ex=error, detail=str(error))
    return error
