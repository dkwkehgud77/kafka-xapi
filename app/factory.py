import logging
import sys

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html, get_redoc_html
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

import app
from app import index
from app.config.config import conf
# from app.middlewares.token_validator import access_control
from app.middlewares.token_validator import access_control
from app.middlewares.trusted_hosts import TrustedHostMiddleware
from app.routes import route_kafka, route_jwt, route_xapi

import pandas as pd

# from app.api import business, edubank, news, prime, professor
# from app import index, auth

API_KEY_HEADER = APIKeyHeader(name="Authorization", auto_error=False)


def create_app():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format="%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] - %(message)s")

    logger = logging.getLogger(__name__)
    logger.info("Kafka xAPI start!")

    # FastAPI 정의
    app = FastAPI(
        title="Kafa xAPI - New Version",
        description="카프카 xAPI 고도화 및 성능 최적화",
        version="0.0.1",
        terms_of_service="https://kafka.hunet.co.kr",
        docs_url=None,
        redoc_url=None)

    # 미들웨어 정의
    app.add_middleware(middleware_class=BaseHTTPMiddleware, dispatch=access_control)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=conf().ALLOW_SITE,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=conf().TRUSTED_HOSTS, except_path=["/health"])

    # xapi 사전 정의
    app.state.df_b2b = pd.read_csv(
        filepath_or_buffer='app/templates/data/xapi_b2b.csv',
        sep=',',
        header=0,
        names=[
            'verb.en-us',
            'verb.ko-kr',
            'object.id',
            'object.definition.extensions.url'
        ],
        encoding='euc-kr'
    )
    app.state.df_b2b["object.definition.extensions.url"] = \
        app.state.df_b2b["object.definition.extensions.url"].str.lower()

    app.state.df_exception = pd.read_csv(
        filepath_or_buffer='app/templates/data/xapi_exception.csv',
        sep=',',
        header=0,
        names=[
            'verb.en-us',
            'verb.ko-kr',
            'object.id',
            'object.definition.extensions.url'
        ],
        encoding='euc-kr'
    )
    app.state.df_exception["object.definition.extensions.url"] = \
        app.state.df_exception["object.definition.extensions.url"].str.lower()

    # 라우터 정의
    app.include_router(route_kafka.router, tags=["kafka"])
    app.include_router(route_xapi.router, tags=["kafka"])
    app.include_router(route_kafka.authRouter, tags=["auth"])
    app.include_router(route_xapi.authRouter, tags=["auth"])
    app.include_router(route_jwt.router, tags=["jwt"])
    app.include_router(index.router, tags=["Index"])
    # app.include_router(auth.router, tags=["Auth"], dependencies=[Depends(API_KEY_HEADER)])
    # app.include_router(business.router, tags=["Api"], dependencies=[Depends(API_KEY_HEADER)])
    # app.include_router(edubank.router, tags=["Api"], dependencies=[Depends(API_KEY_HEADER)])
    # app.include_router(news.router, tags=["Api"], dependencies=[Depends(API_KEY_HEADER)])
    # app.include_router(prime.router, tags=["Api"], dependencies=[Depends(API_KEY_HEADER)])
    # app.include_router(professor.router, tags=["Api"], dependencies=[Depends(API_KEY_HEADER)])

    # static 마운트
    app.mount("/static", StaticFiles(directory="app/templates"), name="static")

    # swagger 정의
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="/static/swagger/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger/swagger-ui.css",
        )

    @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html():
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=app.title + " - ReDoc",
            redoc_js_url="/static/redoc.standalone.js",
        )

    return app
