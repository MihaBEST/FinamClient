import requests


def place_order(token: str, account_id: str, order_data: dict):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = f"https://api.finam.ru/v1/accounts/{account_id}/orders"
    response = requests.post(url, headers=headers, json=order_data)
    response.raise_for_status()
    return response.json()


def cancel_order(token: str, account_id: str, order_id: str):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.finam.ru/v1/accounts/{account_id}/orders/{order_id}"
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_order(token: str, account_id: str, order_id: str):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.finam.ru/v1/accounts/{account_id}/orders/{order_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def place_sltp_order(token: str, account_id: str, sltp_data: dict):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = f"https://api.finam.ru/v1/accounts/{account_id}/sltp-orders"
    response = requests.post(url, headers=headers, json=sltp_data)
    response.raise_for_status()
    return response.json()
