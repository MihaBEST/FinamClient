import requests


def get_account_info(token: str, account_id: str):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.finam.ru/v1/accounts/{account_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_trades(token: str, account_id: str, limit: int = None, start_time: str = None, end_time: str = None):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.finam.ru/v1/accounts/{account_id}/trades"
    params = {}
    if limit: params["limit"] = limit
    if start_time: params["interval.start_time"] = start_time
    if end_time: params["interval.end_time"] = end_time
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def get_transactions(token: str, account_id: str, limit: int = None, start_time: str = None, end_time: str = None):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.finam.ru/v1/accounts/{account_id}/transactions"
    params = {}
    if limit: params["limit"] = limit
    if start_time: params["interval.start_time"] = start_time
    if end_time: params["interval.end_time"] = end_time
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def get_orders(token: str, account_id: str):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.finam.ru/v1/accounts/{account_id}/orders"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
