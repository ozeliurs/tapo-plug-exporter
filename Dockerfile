FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "main.py"]
# ENTRYPOINT [ "gunicorn", "-b", "0.0.0.0:8000", "main:app", "-k", "uvicorn.workers.UvicornWorker"]
# CMD [ "gunicorn", "-b 0.0.0.0:8000", "main:app", "-k uvicorn.workers.UvicornWorker" ]