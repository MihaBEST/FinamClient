import requests
import pandas as pd
"""
Полный пример запроса:
GET https://api.finam.ru/v1/instruments/SBER@MISX/bars?timeframe=TIME_FRAME_H1&interval.startTime=2026-04-08T00:00:00Z&interval.endTime=2026-04-09T00:00:00Z
Доступные таймфреймы: TIME_FRAME_M1, TIME_FRAME_M5, TIME_FRAME_M15, TIME_FRAME_M30,TIME_FRAME_H1,
TIME_FRAME_H2, TIME_FRAME_H4, TIME_FRAME_H8, TIME_FRAME_D, TIME_FRAME_W,TIME_FRAME_MN, TIME_FRAME_QR.
Глубина данных: M1 — 7 дней, M5–H8 — 30 дней, D — 365 дней, W/MN/QR — 5 лет.
"""


def get_bars(token: str, symbol: str, timeframe: str, start_time: str, end_time: str):
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://api.finam.ru/v1/instruments/{symbol}/bars"
    params = {
        "timeframe": timeframe,
        "interval.start_time": start_time,
        "interval.end_time": end_time
    }
    response = requests.get(url.format(symbol=symbol), headers=headers, params=params)
    response.raise_for_status()
    return bars_to_df(response.json())


def bars_to_df(bars_response: dict) -> pd.DataFrame:
    """
    Колонки: timestamp, open, high, low, close, volume
    """
    bars_list = bars_response.get('bars', [])
    if not bars_list:
        return pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    data = []
    for bar in bars_list:
        data.append({
            'timestamp': bar['timestamp'],
            'open': float(bar['open']['value']),
            'high': float(bar['high']['value']),
            'low': float(bar['low']['value']),
            'close': float(bar['close']['value']),
            'volume': float(bar['volume']['value'])
        })

    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    return df
