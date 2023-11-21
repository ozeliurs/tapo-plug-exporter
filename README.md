# Start service by

```bash
gunicorn -b 127.0.0.1:8000 main:app -k uvicorn.workers.UvicornWorker
```
