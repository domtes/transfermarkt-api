import random

import requests

from app.settings import settings


def list_proxies() -> list[str]:
    if not settings.WEBSHARE_API_KEY:
        return []

    response = requests.get(
        "https://proxy.webshare.io/api/proxy/list/",
        headers={"Authorization": f"Token {settings.WEBSHARE_API_KEY}"},
        params={"page_size": 100},
    )
    response.raise_for_status()
    data = response.json()
    proxies = [
        f"http://{item['username']}:{item['password']}@{item['proxy_address']}:{item['ports']['http']}"
        for item in data["results"]
    ]
    return proxies


def get_random_proxy() -> str | None:
    proxies = list_proxies()
    if not proxies:
        return None

    return random.choice(proxies)
