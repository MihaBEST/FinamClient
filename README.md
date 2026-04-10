# FinamClient

Python-клиент для работы с [Finam Trade API](https://api.finam.ru) — REST-интерфейсом брокера Финам.

Предназначен для алгоритмической торговли, сбора рыночных данных и управления счетом через Python. Включает удобные методы для получения свечей, стакана котировок, выставления заявок (включая SL/TP), а также встроенные технические индикаторы (RSI, EMA, ATR, MACD, Bollinger Bands).

## Особенности

- Автоматическая авторизация и получение `account_id` при инициализации.
- Готовые методы для получения последних N свечей (минутных/часовых).
- Преобразование ответов API в Pandas DataFrame.
- Быстрый доступ к списку ликвидных тикеров с лотностями.
- Поддержка Stop-Loss / Take-Profit ордеров.
- Легко интегрируется в Google Colab или локальные скрипты.

## Установка

```bash
pip install -e .
```

Требуется Python 3.8+

## Зависимости

Указаны в `requirements.txt`:
- `requests`
- `pandas`
- `pytz`

## Пример использования

```python
from FinamClient import Client

client = Client("YOUR_API_SECRET")

# Получить последние 10 минутных свечей по Сбербанку
df = client.get_last_min_bars("SBER@MISX", n=10)
print(df[['close', 'volume']])

# Выставить SL/TP
sltp_data = {
    "symbol": "SBER@MISX",
    "side": "SIDE_SELL",
    "quantity_sl": {"value": "1"},
    "sl_price": {"value": "310.00"},
    "limit_price": {"value": "309.50"},
    "quantity_tp": {"value": "1"},
    "tp_price": {"value": "330.00"},
    "valid_before": "VALID_BEFORE_GOOD_TILL_CANCELLED"
}
result = client.place_sltp_order(client.account_id, sltp_data)
```