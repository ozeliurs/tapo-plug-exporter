import os
import re
import platform
import shutil
import logging
import asyncio
import json
import threading

from dotenv import load_dotenv
from pathlib import Path
from time import sleep
from tapo import ApiClient

from prometheus_client import Summary, Info, Gauge, Counter
from prometheus_client import start_http_server, REGISTRY, CollectorRegistry, multiprocess

# logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

labels = ["ip", "mac", "model", "name", "type", "ssid"]
power_status = Gauge('tapo_power_status', 'Power status on/off', labels)
power_current = Gauge('tapo_power_current', 'Power being consumed right now', labels)
power_usage_today = Gauge('tapo_power_usage_today', 'Power usage used today', labels)
power_saved_today = Gauge('tapo_power_saved_today', 'Power usage used today', labels)
time_used = Gauge('tapo_time_used_today', 'Power usage used today', labels)

async def get_metrics(devices):

    dotenv_path = Path('./.env')
    load_dotenv(dotenv_path=dotenv_path)

    TAPO_USER = os.getenv('TAPO_USER')
    TAPO_PASS = os.getenv('TAPO_PASS')

    data = []

    types = list(devices.keys())

    for product in types:
        for ip in devices[product]:

            client = ApiClient(TAPO_USER, TAPO_PASS)
            device = None

            if product == "p115":
                device = await client.p115(ip)  
            if product == "p100":
                device = await client.p100(ip)
            if product == "p110":
                device = await client.p110(ip)
            if product == "l530":
                device = await client.l530(ip)

            logger.info(f"Getting device info for {ip}")

            device_info = await device.get_device_info()

            logger.info(f"Received device info for {ip}: {device_info}")

            power_usage = None
            time_used_today = None
            power_saved_today = None
            power_usage_today = None
            
            if product in ["p115"]:
                device_usage = await device.get_device_usage()
                time_used_today = device_usage.to_dict()['time_usage']['today']
                power_saved_today = device_usage.to_dict()['saved_power']['today']
                current_power = await device.get_current_power()
                energy_usage = await device.get_energy_usage()
                # energy_data = await device.get_energy_data()

                power_usage = current_power.to_dict()['current_power']
                time_used_today = device_usage.to_dict()['time_usage']['today']
                power_saved_today = device_usage.to_dict()['saved_power']['today']
                power_usage_today = device_usage.to_dict()['power_usage']['today']
        
            device_info_dict = device_info.to_dict()
            # print(device_info_dict)
            firmware_version = device_info_dict['fw_ver']
            ip = device_info_dict['ip'] 
            mac = device_info_dict['mac'] 
            model = device_info_dict['model'] 
            name = device_info_dict['nickname'] 
            product_type = device_info_dict['type'] 
            ssid = device_info_dict['ssid']
            status = 0
            if device_info_dict['device_on']:
                status = 1

            data.append({
                'ip': ip, 
                'mac':mac, 
                'model':model, 
                'name':name, 
                'type':product_type, 
                'ssid':ssid, 
                'on':status,
                'power': power_usage,
                'time_used_today': time_used_today,
                'power_saved_today': power_saved_today,
                'power_usage_today': power_usage_today
            })
        
    with open('./data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

class RetrieveTapo(object):

    def __init__(self, interval=1):

        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution
        
    def run(self):
        f = open('./tapo.json') # loads target tapo devices
        devices = json.load(f)

        while True:            
            asyncio.run(get_metrics(devices))
            sleep(5)

def apply_metrics():
    if os.path.isfile('./data.json'):
        f = open('./data.json')
        data = json.load(f)
        for device in data:
            # print(device['power'], device['ip'],device['on'],device["mac"],device["model"],device["name"],device["type"],device["ssid"])

            power_status.labels(
                ip=device['ip'], 
                mac=device["mac"], 
                model=device["model"], 
                name=device["name"], 
                type=device["type"], 
                ssid=device["ssid"]
            ).set(device['on'])

            if not device['power'] is None:
                power_current.labels(
                    ip=device['ip'], 
                    mac=device["mac"], 
                    model=device["model"], 
                    name=device["name"], 
                    type=device["type"], 
                    ssid=device["ssid"]
                ).set(device['power'])

            if not device['power_usage_today'] is None:
                power_usage_today.labels(
                    ip=device['ip'], 
                    mac=device["mac"], 
                    model=device["model"], 
                    name=device["name"], 
                    type=device["type"], 
                    ssid=device["ssid"]
                ).set(device['power_usage_today'])

            if not device['power_saved_today'] is None:
                power_saved_today.labels(
                    ip=device['ip'], 
                    mac=device["mac"], 
                    model=device["model"], 
                    name=device["name"], 
                    type=device["type"], 
                    ssid=device["ssid"]
                ).set(device['power_saved_today'])

            if not device['time_used_today'] is None:
                time_used.labels(
                    ip=device['ip'], 
                    mac=device["mac"], 
                    model=device["model"], 
                    name=device["name"], 
                    type=device["type"], 
                    ssid=device["ssid"]
                ).set(device['time_used_today'])

if __name__ == "__main__":

    # prome_stats = os.environ["PROMETHEUS_MULTIPROC_DIR"]
    # if os.path.exists(prome_stats):
    #     shutil.rmtree(prome_stats)
    # os.mkdir(prome_stats)
    
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    start_http_server(8000, registry=registry)

    retriever = RetrieveTapo()

    while True:
        apply_metrics()
        sleep(5)