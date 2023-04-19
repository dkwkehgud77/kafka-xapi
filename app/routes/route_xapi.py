import hashlib
import traceback
from ast import literal_eval
from datetime import datetime
from urllib.parse import urlparse

from pandas import DataFrame

from app.config.logger import Logger
from app.models.model_kafka import MessageOk
from fastapi import APIRouter, Security

from app.config.producer import kafkaProducer
from app.middlewares.errors import exceptions as ex
from app.models.model_xapi import XapiModel, Object, Actor, VerbDisplay
from app.routes.route_jwt import api_key, token_decode

router = APIRouter(prefix="/xAPI")
authRouter = APIRouter(prefix="/auth")

from app.utils import tincan

logger = Logger().get_instance().logger


@router.post("/{service}")
async def kafka(service: str, params: XapiModel):
    result = await xapi_send(service, params)
    return result


@authRouter.post("/{service}")
async def kafka(service: str, params: XapiModel, token=Security(api_key)):
    payload = await token_decode(access_token=token)
    if payload["auth"] == "certified_access":
        result = await xapi_send(service, params)
        return result
    else:
        raise ex.NotAuthorized()


async def xapi_send(service: str, params: XapiModel):
    services = ['b2b', 'grow', 'talentbank', 'test']
    if service not in services:
        raise Exception('Unsupported service')

    actor: Actor = params.actor
    verb: VerbDisplay = params.verb
    obj: Object = params.object

    verb, obj = await check_xapi_dict(service, verb, obj)

    # mbox 바이트 변환, SHA1 알고리즘 해시값 계산
    mbox_bytes = actor.mbox.encode('utf-8')
    mbox_hash = hashlib.sha1(mbox_bytes).hexdigest()
    mbox_sha1sum = 'mailto:' + mbox_hash

    _topic = params.topic
    _actor = tincan.Agent(
        name=actor.name,
        mbox=actor.mbox,
        mbox_sha1sum=mbox_sha1sum,
        account=tincan.AgentAccount(
            name=actor.account.name,
            home_page=actor.account.home_page,
            session=actor.account.session
        ),
        extensions=tincan.Extensions(actor.extensions)
    )

    _verb = tincan.Verb(
        id=f"https://xapi.hunet.co.kr/{service}/verbs/{verb.en_us}",
        display=tincan.LanguageMap(verb)
    )

    obj.definition.description.ko_kr = obj.id
    _obj = tincan.Activity(
        id=f"https://xapi.hunet.co.kr/{service}/objects/{obj.definition.description.en_us}",
        definition=tincan.ActivityDefinition(
            description=tincan.LanguageMap(obj.definition.description),
            extensions=tincan.Extensions(obj.definition.extensions)
        )
    )

    _statement = tincan.Statement(
        actor=_actor,
        verb=_verb,
        object=_obj,
        timestamp=datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'
    )
    _value = literal_eval(_statement.to_json())

    kafkaProducer().send(topic=_topic, value=_value)

    return MessageOk()


async def check_xapi_dict(service, verb, obj):
    from main import app
    if service == 'b2b':
        df_b2b: DataFrame = app.state.df_b2b
        obj_extensions = obj.definition.extensions
        url_parts = urlparse(obj_extensions.url).path.split('/')
        chk_url = '/' + url_parts[1].lower()
        logger.info(df_b2b[df_b2b['object.definition.extensions.url'] == chk_url])
        res_xapi_dict = df_b2b[df_b2b['object.definition.extensions.url'] == chk_url].to_dict('records')

        if len(res_xapi_dict) == 0:
            res_xapi_dict = [{
                "verb.en-us": "None",
                "verb.ko-kr": "알수없음",
                "object.id": "알수없음",
                "object.definition.extensions.url": "/None"
            }]
        if verb.en_us is None and verb.ko_kr is None:
            verb.en_us = res_xapi_dict[0]['verb.en-us']
            verb.ko_kr = res_xapi_dict[0]['verb.ko-kr']

        if obj.id is None:
            obj.id = res_xapi_dict[0]['object.id']
    else:
        if verb.en_us is None and verb.ko_kr is None:
            verb.en_us = ""
            verb.ko_kr = ""

    return verb, obj
