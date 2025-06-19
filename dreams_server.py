from fastapi import FastAPI, Request
import uvicorn
from datetime import datetime
import pytz
import os.path
import asyncio

LOG_FILE_NAME = "requests.txt"

app = FastAPI()

counter = 0
banned_ips = set()
if os.path.isfile(LOG_FILE_NAME):
    with open(LOG_FILE_NAME) as file:
        counter = len(file.readlines())


@app.get('/update')
async def update(request: Request):
    global counter
    client_ip = request.client.host
    if client_ip not in banned_ips:
        timestamp_ms = int(datetime.now(pytz.timezone('Europe/Moscow')).timestamp() * 1000)
        log_request(client_ip, timestamp_ms)
        asyncio.create_task(ban_and_unban_ip(client_ip, 10))
        counter += 1
    return {"counter": counter}


async def ban_and_unban_ip(client_ip, seconds):
    banned_ips.add(client_ip)
    print(f"{client_ip} banned for {seconds} seconds!")
    await asyncio.sleep(seconds)
    print(f"{seconds} seconds passed! {client_ip} unbanned!")
    banned_ips.remove(client_ip)


def log_request(ip, timestamp):
    with open(LOG_FILE_NAME, 'a') as file:
        file.write(f"{ip} {timestamp}\n")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8086)
