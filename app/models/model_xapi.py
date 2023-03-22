from typing import Optional

from pydantic.main import BaseModel
from pydantic import Field, Extra

from dataclasses import dataclass


# Actor
class ActorAccount(BaseModel):
    name: str = Field(title='에이전트 계정')
    home_page: str = Field(title='에이전트 URL')

    class Config:
        extra = Extra.allow


class ActorExtensions(BaseModel):
    birth: Optional[int] = Field(None, title='생일')
    gender: Optional[str] = Field(None, title='성별')

    class Config:
        extra = Extra.allow


class Actor(BaseModel):
    name: str = Field(title='사용자')
    mbox: str = Field(title='사용자 메일')
    account: ActorAccount = Field(title='에이전트', alias='agentaccount')
    extensions: Optional[ActorExtensions] = Field(None, title='사용자 추가정보')

    class Config:
        extra = Extra.allow
        schema_extra = {
            'example': {
                'name': 'test-name',
                'mbox': 'https://test.hunet.co.kr',
                'agentaccount': {
                    'name': 'test011',
                    'home_page': 'https://all.labs.hunet.co.kr',
                    'session': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
                },
                'extensions': {
                    'birth': '19890715',
                    'gender': 'male'
                }
            }
        }


# Verb
class VerbDisplay(BaseModel):
    en_us: str = Field(title='행위 en-us', alias='en-us')
    ko_kr: Optional[str] = Field(None, title='행위 ko-kr', alias='ko-kr')

    class Config:
        extra = Extra.allow
        schema_extra = {
            'example': {
                'en-us': 'viewed',
                'ko-kr': '접속'
            }
        }


class Verb(BaseModel):
    id: str = Field(title='행위 ID')
    display: VerbDisplay = Field(title='행위 표시')

    class Config:
        extra = Extra.allow


# Object
class Description(BaseModel):
    en_us: str = Field('None', title='대상 en-us', alias='en-us')
    ko_kr: str = Field('None', title='대상 ko-kr', alias='ko-kr')

    class Config:
        extra = Extra.allow


class Extensions(BaseModel):
    url: Optional[str] = Field(None, title='URL')
    pre_url: Optional[str] = Field(None, title='이전 URL')

    class Config:
        extra = Extra.allow


class Definition(BaseModel):
    description: Description = Field(title='대상 en-us')
    extensions: Extensions = Field(title='대상 추가정보')

    class Config:
        extra = Extra.allow


class Object(BaseModel):
    id: str = Field(title='대상 ko-kr')
    definition: Definition = Field(title='대상 정의')

    class Config:
        extra = Extra.allow
        schema_extra = {
            'example': {
                'id': '마이페이지',
                'definition': {
                    'description': {
                        'en-us': 'mypage'
                    },
                    'extensions': {
                        'company_cd': '40287',
                        'url': 'https://test.hunet.co.kr/Classroom/StudyIng?_=example-number',
                        'pre_url': 'https://test.hunet.co.kr/classroom/online'
                    }
                }
            }
        }


# xAPI
class XapiModel(BaseModel):
    topic: str = Field('experience-api-test', title='토픽')
    actor: Actor = Field(title='사용자')
    verb: VerbDisplay = Field(title='행위')
    object: Object = Field(title='대상')

    class Config:
        extra = Extra.allow



