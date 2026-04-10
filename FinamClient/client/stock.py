import requests
import pandas as pd


def get_orderbook(token: str, symbol: str):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.finam.ru/v1/instruments/{symbol}/orderbook"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return orderbook_to_df(response.json())


def get_latest_quote(token: str, symbol: str):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.finam.ru/v1/instruments/{symbol}/quotes/latest"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_latest_trades(token: str, symbol: str):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.finam.ru/v1/instruments/{symbol}/trades/latest"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_all_assets(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://api.finam.ru/v1/assets"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_asset_info(token: str, symbol: str):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.finam.ru/v1/assets/{symbol}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def orderbook_to_df(orderbook_response: dict):
    """
    Возвращает кортеж (bids_df, asks_df).
    bids_df колонки: price, value (объем покупки)
    asks_df колонки: price, value (объем продажи)
    """
    rows = orderbook_response.get('orderbook', {}).get('rows', [])

    bids_data = []
    asks_data = []

    for row in rows:
        price = float(row['price']['value'])

        if 'sell_size' in row:
            asks_data.append({
                'price': price,
                'value': float(row['sell_size']['value'])
            })
        elif 'buy_size' in row:
            bids_data.append({
                'price': price,
                'value': float(row['buy_size']['value'])
            })

    bids_df = pd.DataFrame(bids_data, columns=['price', 'value'])
    asks_df = pd.DataFrame(asks_data, columns=['price', 'value'])

    if not bids_df.empty:
        bids_df.sort_values(by='price', ascending=False, inplace=True)
    if not asks_df.empty:
        asks_df.sort_values(by='price', ascending=True, inplace=True)

    return bids_df, asks_df
