# gunicorn --bind 0:8090 -w 4 -k uvicorn.workers.UvicornWorker "app.factory:create_app()"
uvicorn --bind 0:8090 main:app --workers 4 --proxy-headers