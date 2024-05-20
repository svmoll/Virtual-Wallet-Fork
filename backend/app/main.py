from fastapi import FastAPI
from core.database import engine
from api.models import models
from core import data_load
import uvicorn


models.Base.metadata.create_all(bind=engine)
data_load.data_load()

app = FastAPI()


# if __name__ == "__main__":
#     uvicorn.run(app="main:app", host="127.0.0.1", port=8001)


# project_root/
# ├── backend/
# │   ├── app/
# │   │   ├── api/
# │   │   │   ├── models/
# │   │   │   │   ├── models.py
# │   │   │   ├── routes/
# │   │   │   │   ├── users/
# │   │   │   │   │   ├── router.py
# │   │   │   │   │   ├── service.py
# │   │   │   │   │   ├── schemas.py
# │   │   │   │   ├── cards/
# │   │   │   │   │   ├── router.py
# │   │   │   │   │   ├── service.py
# │   │   │   │   │   ├── schemas.py
# │   │   │   │   ├── transactions/
# │   │   │   │   │   ├── router.py
# │   │   │   │   │   ├── service.py
# │   │   │   │   │   ├── schemas.py
# │   │   │   ├── utils/
# │   │   │   │   ├── utils.py
# │   │   ├── core/
# │   │   │   ├── config.py
# │   │   │   ├── data_load.py
# │   │   │   ├── database.py
# │   │   ├── main.py
# │   │   ├── dependencies.py
# │   ├── tests/
# │   ├── requirements.txt
# │   ├── README.md