from fastapi import APIRouter, Security
from starlette.responses import JSONResponse

from app.config.producer import kafkaProducer
from app.middlewares.errors import exceptions as ex
from app.models.model_kafka import KafkaModel, MessageOk
from app.routes.route_jwt import api_key, token_decode


router = APIRouter(prefix="/api")
authRouter = APIRouter(prefix="/auth")


@router.post("/kafka")
async def kafka(params: KafkaModel):
    result = await kafka_send(params)
    return result


@authRouter.post("/kafka")
async def kafka(params: KafkaModel, token=Security(api_key)):
    payload = await token_decode(access_token=token)

    if payload["auth"] == "certified_access":
        result = await kafka_send(params)
        return result
    else:
        raise ex.NotAuthorized()


async def kafka_send(params: KafkaModel):
    topic = params.topic
    field = params.field
    try:
        if isinstance(field, list):
            for row in field:
                kafkaProducer().send(topic=topic, value=row)
        else:
            kafkaProducer().send(topic=topic, value=field)
            return MessageOk()
    except (BaseException, Exception) as e:
        return JSONResponse(status_code=500, content=dict(message=str(e)))
