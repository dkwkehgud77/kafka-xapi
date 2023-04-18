import re
import sys
import time

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config.consts import EXCEPT_PATH_LIST, EXCEPT_PATH_REGEX
from app.config.logger import api_logger, Logger
from app.middlewares.errors.exceptions import APIException

from app.utils.date_utils import D

logger = Logger().get_instance().logger


async def access_control(request: Request, call_next):
    request.state.req_time = D.datetime()
    request.state.start = time.time()
    request.state.inspect = None
    # request.state.user = None
    request.state.payload = None
    request.state.service = None

    ip = request.headers["x-forwarded-for"] if "x-forwarded-for" in request.headers.keys() else request.client.host
    request.state.ip = ip.split(",")[0] if "," in ip else ip

    url = request.url.path
    if await url_pattern_check(url, EXCEPT_PATH_REGEX) or url in EXCEPT_PATH_LIST:
        response = await call_next(request)
        if url != "/":
            await api_logger(request=request, response=response)
        return response

    try:
        response = await call_next(request)
        await api_logger(request=request, response=response)
    except Exception as e:
        logger.error(e)
        error = await exception_handler(e)
        error_dict = dict(status=error.status_code, msg=error.msg, detail=error.detail, code=error.code)
        response = JSONResponse(status_code=error.status_code, content=error_dict)
        await api_logger(request=request, error=error)

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
