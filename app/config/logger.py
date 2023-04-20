import json
import logging
import logging.config
from datetime import datetime, timedelta
from json import JSONDecodeError
from time import time

from fastapi.requests import Request

from app.config.producer import kafkaProducer
from app.middlewares.errors import exceptions as ex

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


async def api_logger(request: Request, response=None, error=None):
    logger = Logger().get_instance().logger
    time_format = "%Y/%m/%d %H:%M:%S"
    t = time() - request.state.start
    status_code = error.status_code if error else response.status_code
    error_log = None
    user = request.state.user
    payload = request.state.payload
    payload = payload.decode('utf-8')

    if error:
        if request.state.traceback:
            exc_traceback = request.state.traceback
            error_file, error_line, error_func, _ = exc_traceback[-1]
        else:
            error_func = error_file = error_line = "UNKNOWN"

        error_log = dict(
            errorFunc=error_func,
            location="{} line in {}".format(str(error_line), error_file),
            raised=str(error.__class__.__name__),
            msg=str(error.ex),
        )
        kafkaProducer().send(topic="dead-letter-xapi", value=payload)

    email = user.email.split("@") if user and user.email else None
    user_log = dict(
        client=request.state.ip,
        user=user.id if user and user.id else None,
        email="**" + email[0][2:-1] + "*@" + email[1] if user and user.email else None,
    )

    if status_code == 422:
        try:
            payload = json.loads(payload)
            kafkaProducer().send(topic="dead-letter-xapi", value=payload)
        except JSONDecodeError:
            logger.warning("Invalid JSON request")
            pass

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


