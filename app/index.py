from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import Response, RedirectResponse
from elasticsearch import Elasticsearch
import re

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def index():
    """
    swagger 로 리다이렉트
    :return:
    """
    return RedirectResponse(url="/docs", status_code=302)


@router.get("/health")
async def status():
    """
    ELB 상태 체크용 API
    :return:
    """
    current_time = datetime.utcnow()
    return Response(f"Hunet B2C Search API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})"), 200



########################################################################### Flink 세션 윈도우 테스트

# @router.get("/visualize")
async def visualize(request: Request):
    """
    Sankey Diagram 시각화
    :return:
    """
    from_rows = search_index()
    response = processed_data(from_rows)

    return templates.TemplateResponse("sankey_diagram.html", {"request": request, "response": response})


def setup_connection():
    # _userpw = "enroll-list-user:tprPdlfemdDBA1%23"
    _userpw = "flink-test:rlaehgud1!"
    _elastic = [
        'https://{}@10.30.31.20:9200'.format(_userpw),
        'https://{}@10.30.31.21:9200'.format(_userpw),
        'https://{}@10.30.31.22:9200'.format(_userpw),
    ]
    es_obj = Elasticsearch(
        _elastic,
        cs_certs=False,
        verify_certs=False,
        timeout=3,
        max_retrie=10,
        retry_on_timeout=True
    )

    return es_obj


def search_index():
    es = setup_connection()
    # query = {"query": {"match": {"pk": "hmall1905314_hmall"}}}
    query = {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "terms": {
                            "site": ["koroad", "donga", "dlive"]
                        }
                    }
                ]
            }
        },
        "aggs": {
            "FROM": {
                "terms": {
                    "field": "from_url",
                    "size": 15
                    # "order": {
                    #   "_key": "asc"
                    # }
                },
                "aggs": {
                    "TO": {
                        "terms": {
                            "field": "to_url",
                            "size": 5,
                            "order": {
                                "_count": "desc"
                            }
                        }
                    }
                }
            }
        }
    }
    res = es.search(index='flink-test', body=query)
    # hits = res['hits']['hits']
    froms = res['aggregations']['FROM']['buckets']
    # print(froms)

    return froms


def processed_data(from_rows):
    res = []

    for from_row in from_rows:
        from_url = from_row['key']
        # from_url = re.sub(r'^\d+(/.*)?th', 'f', from_url)
        # if from_url not in ['0th_', '1th_', '2th_', '3th_', '4th_', '5th_', '6th_', '7th_', '8th_', '9th_'] and not re.search('/main', from_url) and not re.search('/customerSso', from_url) and not re.search('/classroomStudy/classroomStudyList', from_url):
        to_rows = from_row['TO']['buckets']
        for to_row in to_rows:
            to_url = to_row['key']
            # to_url = re.sub(r'^\d+(/.*)?th_', 't', to_url)
            count = int(to_row['doc_count'])
            row = {
                "from": from_url,
                "to": to_url,
                "value": count
            }
            res.append(row)
    return res


# @router.get("/search")
async def search():
    """
    elasticsearch index 검색
    :return:
    """
    try:
        from_rows = search_index()
        res = processed_data(from_rows)
        return res
    except Exception as e:
        print(f"error :: {e}")
        pass
