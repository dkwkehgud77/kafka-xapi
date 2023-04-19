from pydantic import Field
from pydantic.main import BaseModel


class Auth(BaseModel):
    api_key: str = "DFD21DASF754FGDFGD5474fFASF"


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class KafkaModel(BaseModel):
    topic: str = Field(title='토픽')
    field: object = Field(title='데이터')

    class Config:
        schema_extra = {
            "example": {
                "topic": "flink-test",
                "field": {
                    "message": "hello world",
                    "add-column": "just put in any data"
                }
            }
        }


class MessageOk(BaseModel):
    result: str = "success"
