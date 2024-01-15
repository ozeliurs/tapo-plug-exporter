# Start service by

Modify: docker-compose.yaml
+ TAPO_USER
+ TAPO_PASS

Configure: tapo.json

```json
{
    "p115": ["192.168.69.65"],
    "p110": ["192.168.69.61"],
    "l530": ["192.168.69.70","192.168.69.59"]
}
```

Run docker compose:
```bash
docker compose build --no-cache && docker compose up -d
```

## Reference

+ [https://github.com/prometheus/client_python](https://github.com/prometheus/client_python)
+ [https://github.com/mihai-dinculescu/tapo](https://github.com/mihai-dinculescu/tapo)
