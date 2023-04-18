import uvicorn
import setproctitle

from app.factory import create_app

setproctitle.setproctitle("xapi")
app = create_app()

if __name__ == "__main__":
    uvicorn.run("run:app", host="0.0.0.0", port=8080, reload=True)


