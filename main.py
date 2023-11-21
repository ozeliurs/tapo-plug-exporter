from prometheus_client import make_asgi_app, Summary, Info, Gauge, Counter, REGISTRY
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from pathlib import Path
from tapo import ApiClient
import asyncio
import os
import random
import time

power_usage_today = Gauge('tapo_power_usage_today', 'Power usage used today')
power_saved_today = Gauge('tapo_power_saved_today', 'Power usage used today')
time_used = Gauge('tapo_time_used_today', 'Power usage used today')

async def set_power_usage_today(client, device):
    device = await client.p115(device)
    device_info = await device.get_device_usage()
    power_usage_today.set(device_info.to_dict()['power_usage']['today'])
    power_saved_today.set(device_info.to_dict()['saved_power']['today'])
    time_used.set(device_info.to_dict()['time_usage']['today'])

def tapo_fetcher(ip):

    dotenv_path = Path('./.env')
    load_dotenv(dotenv_path=dotenv_path)

    TAPO_USER = os.getenv('TAPO_USER')
    TAPO_PASS = os.getenv('TAPO_PASS')

    client = ApiClient(TAPO_USER, TAPO_PASS)

    asyncio.create_task(set_power_usage_today(client, ip))
      
    return

app = FastAPI(debug=False)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.middleware("http")
async def generate_metrics(request: Request, call_next):

    if "target" in request.query_params:
        ip = str(request.query_params).split("=")[1]
        tapo_fetcher(ip)
    else:
        print("[ERROR] No target was passed")

    response = await call_next(request)
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)