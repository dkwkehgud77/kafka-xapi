from pydantic.main import BaseModel


class Auth(BaseModel):
    api_key: str = "DFD21DASF754FGDFGD5474fFASF"


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class KafkaModel(BaseModel):
    topic: str = "flink-test"
    field: object = {"message": "hello world", "add-column": "just put in any data"}


class MessageOk(BaseModel):
    result: str = "success"
