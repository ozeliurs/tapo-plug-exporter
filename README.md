# Start service by

```bash
gunicorn -b 127.0.0.1:8000 main:app -k uvicorn.workers.UvicornWorker
```

## Based on

+ [https://github.com/prometheus/client_python](https://github.com/prometheus/client_python)
+ [https://github.com/mihai-dinculescu/tapo](https://github.com/mihai-dinculescu/tapo)