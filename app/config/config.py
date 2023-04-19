from dataclasses import dataclass
from os import path, environ

base_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))

'''
@dataclass를 사용하여 정의된 클래스는 다음과 같은 내부 메소드를 자동으로 구현합니다.

__init__(self, x: int, y: int) : 인스턴스 생성 시 속성을 초기화하는 메소드입니다.
__repr__(self) : 객체의 문자열 표현을 반환하는 메소드입니다.
__eq__(self, other) : 객체의 동등성을 비교하는 메소드입니다.
'''


@dataclass
class Config:
    """
    기본 Configuration
    """
    BASE_DIR: str = base_dir
    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = True
    DEBUG: bool = False
    TEST_MODE: bool = False


@dataclass
class LocalConfig(Config):
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]
    DEBUG: bool = True


@dataclass
class StagConfig(Config):
    TRUSTED_HOSTS = ["*"]
    # TRUSTED_HOSTS = ["10.20.70.79"]
    ALLOW_SITE = ["*"]
    TEST_MODE: bool = True


@dataclass
class ProdConfig(Config):
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]


def conf():
    """
    환경 불러오기
    :return:
    """
    config = dict(prod=ProdConfig, local=LocalConfig, stag=StagConfig)
    # {'prod': <class 'app.config.config.ProdConfig'>, 'local': <class 'app.config.config.LocalConfig'>, 'stag': <class 'app.config.config.StagConfig'>}
    return config["local"]()
