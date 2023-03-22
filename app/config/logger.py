import json
import logging
import logging.config
from dataclasses import asdict
from datetime import datetime, timedelta
from time import time

from fastapi.requests import Request
from app.config.config import conf


logConfig = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "simple": {"format": "[%(levelname)s] %(message)s"},
        "complex": {
            "format": "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] - %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "complex",
            "level": "DEBUG",
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "complex",
            "level": "INFO",
            "when": "midnight",
            "interval": 1,
            "backupCount": 4,
            "filename": f"logs/app.log"
        }
    },

    "loggers": {
        "default": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": True
        }
    }
}

# logging.config.dictConfig(logConfig)


class Logger(object):
    __instance = None
    logger = None

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = Logger()
            cls.logger = logging.getLogger("default")
        return cls.__instance


class SingleTone(object):
    """
    하나의 싱글톤 인스턴스를 생성
    이미 생성된 인스턴스가 있다면 재사용
    """

    def __new__(cls, *args, **kwargs):
        """
        *args와 **kwargs는 무슨의미일까?
        여러 가변인자를 받겠다고 명시하는 것이며, *args는 튜플형태로 전달, **kwargs는 키:값 쌍의 사전형으로 전달된다.
        def test(*args, **kwargs):
            print(args)
            print(kwargs)

        test(5,10,'hi', k='v')
        결과 : (5, 10, 'hi') {'k': 'v'}
        """
        if not hasattr(cls, 'instance'):
            cls.instance = super(Logger, cls, *args, **kwargs).__new__(cls, *args, **kwargs)
        return cls.instance


async def api_logger(request: Request, response=None, error=None):
    logger = Logger().get_instance().logger
    time_format = "%Y/%m/%d %H:%M:%S"
    t = time() - request.state.start
    status_code = error.status_code if error else response.status_code
    error_log = None
    payload = request.state.payload
    if error:
        if request.state.inspect:
            frame = request.state.inspect
            error_file = frame.f_code.co_filename
            error_func = frame.f_code.co_name
            error_line = frame.f_lineno
        else:
            error_func = error_file = error_line = "UNKNOWN"

        error_log = dict(
            errorFunc=error_func,
            location="{} line in {}".format(str(error_line), error_file),
            raised=str(error.__class__.__name__),
            msg=str(error.ex),
        )

    # email = user.email.split("@") if user and user.email else None
    user_log = dict(
        client=request.state.ip,
        user=payload
        # user=user.id if user and user.id else None,
        # email="**" + email[0][2:-1] + "*@" + email[1] if user and user.email else None,
    )

    log_dict = dict(
        url=request.url.hostname + request.url.path,
        method=str(request.method),
        statusCode=status_code,
        errorDetail=error_log,
        client=user_log,
        processedTime=str(round(t * 1000, 5)) + "ms",
        datetimeUTC=datetime.utcnow().strftime(time_format),
        datetimeKST=(datetime.utcnow() + timedelta(hours=9)).strftime(time_format),
    )
    if error and error.status_code >= 500:
        logger.error(json.dumps(log_dict))
    else:
        logger.info(json.dumps(log_dict))