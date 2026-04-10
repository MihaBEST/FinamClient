# 📚 Докуентация FinamClient

---

Модуль для работы с API Finam Trade (REST) в Python. Предоставляет удобный интерфейс для получения рыночных данных, управления счетом и выставления заявок.


## 🔑 Инициализация клиента

Для начала работы необходимо создать экземпляр класса `Client`, передав ему ваш секретный API-ключ (получается в личном кабинете Finam).

```python
from FinamClient import Client

API_SECRET = "ВАШ_API_SECRET_KEY"
client = Client(API_SECRET)

print(f"Account ID: {client.account_id}")
```

При инициализации клиент автоматически:
1. Получает JWT-токен.
2. Определяет `account_id` вашего торгового счета.

---

## 📈 Рыночные данные

### 1. Получение свечей (Bars)

Вы можете получить исторические свечи за произвольный период или быстро получить последние N свечей.

#### Быстрое получение последних свечей

```python
# Последние 5 часовых свечей по Сбербанку
df_hourly = client.get_last_hour_bars("SBER@MISX", n=5)
print(df_hourly[['close', 'volume']])

# Последние 10 минутных свечей по Газпрому
df_minutely = client.get_last_min_bars("GAZP@MISX", n=10)
print(df_minutely[['close', 'volume']])
```

*   **Формат ответа:** `pd.DataFrame` с индексом `timestamp` и колонками: `open`, `high`, `low`, `close`, `volume`.
*   **Таймфреймы:** `get_last_hour_bars` использует `TIME_FRAME_H1`, `get_last_min_bars` — `TIME_FRAME_M1`.

#### Произвольный период

```python
from datetime import datetime, timezone

start_time = "2026-04-08T00:00:00Z"
end_time = "2026-04-09T00:00:00Z"

df_custom = client.get_bars(
    symbol="SBER@MISX",
    timeframe="TIME_FRAME_H1",
    start_time=start_time,
    end_time=end_time
)
print(df_custom.head())
```

### 2. Стакан котировок (Order Book)

Получает текущий стакан по инструменту. Возвращает два DataFrame: для заявок на покупку (`bids`) и на продажу (`asks`).

```python
bids_df, asks_df = client.get_orderbook("SBER@MISX")

print("Top 5 Bids (Покупка):")
print(bids_df.head()) 
# Колонки: price, value

print("Top 5 Asks (Продажа):")
print(asks_df.head())
# Колонки: price, value
```

### 3. Последняя котировка и сделки

```python
# Последняя котировка (Best Bid/Ask, Last Price)
quote = client.get_latest_quote("SBER@MISX")
print(quote)

# Последние сделки
trades = client.get_latest_trades("SBER@MISX")
print(trades)
```

---

## 💼 Управление счетом и заявками

Все методы торговли автоматически используют `account_id`, полученный при инициализации.

### 1. Информация о счете

```python
info = client.get_account_info(client.account_id)
print(f"Equity: {info['equity']['value']}")
print(f"Positions: {len(info['positions'])}")
```

### 2. Выставление обычной заявки (Limit/Market)

```python
order_data = {
    "symbol": "SBER@MISX",
    "quantity": {"value": "1"},
    "side": "SIDE_BUY",          # SIDE_BUY или SIDE_SELL
    "type": "ORDER_TYPE_LIMIT",  # ORDER_TYPE_MARKET или ORDER_TYPE_LIMIT
    "time_in_force": "TIME_IN_FORCE_DAY",
    "limit_price": {"value": "315.00"}, # Обязательно для LIMIT
    "comment": "Test Order"
}

result = client.place_order(client.account_id, order_data)
print(f"Order ID: {result['order_id']}")
```

### 3. Stop-Loss / Take-Profit (SL/TP)

Выставляется отдельной условной заявкой. Важно правильно указать `side`: сторона сделки, которая **закроет** вашу позицию.
*   Если вы в Лонге (купили), то SL/TP будут продавать → `side: "SIDE_SELL"`.
*   Если вы в Шорте (продали), то SL/TP будут покупать → `side: "SIDE_BUY"`.

```python
sltp_data = {
    "symbol": "SBER@MISX",
    "side": "SIDE_SELL",         # Закрываем лонг
    "quantity_sl": {"value": "1"},
    "sl_price": {"value": "310.00"},     # Цена активации SL
    "limit_price": {"value": "309.50"},  # Лимитная цена исполнения SL
    "quantity_tp": {"value": "1"},
    "tp_price": {"value": "330.00"},     # Цена активации TP
    "tp_guard_spread": {"value": "0.1"},
    "tp_spread_measure": "TP_SPREAD_MEASURE_VALUE",
    "valid_before": "VALID_BEFORE_GOOD_TILL_CANCELLED",
    "comment": "AI SL/TP"
}

result = client.place_sltp_order(client.account_id, sltp_data)
print(f"SL/TP Order ID: {result['order_id']}")
```

### 4. Отмена заявки

```python
order_id_to_cancel = "YOUR_ORDER_ID"
client.cancel_order(client.account_id, order_id_to_cancel)
```

### 5. Список активных заявок

```python
orders = client.get_orders(client.account_id)
for order in orders['orders']:
    print(f"ID: {order['order_id']}, Symbol: {order['order']['symbol']}, Status: {order['status']}")
```

---

## 🛠 Вспомогательные функции (Calculate)

Модуль `calculate.py` содержит полезные утилиты для анализа данных и получения списков инструментов.

### 1. Технические индикаторы

Принимают `pd.DataFrame` со свечами (колонки `close`, `high`, `low` обязательны).

```python
from FinamClient import calculate_ema20, calculate_rsi14, calculate_atr14, calculate_macd

# Получаем свечи
df = client.get_last_min_bars("SBER@MISX", n=100)

ema = calculate_ema20(df)
rsi = calculate_rsi14(df)
atr = calculate_atr14(df)
macd_line, signal, histogram = calculate_macd(df)

print(f"EMA20: {ema}, RSI: {rsi}, ATR: {atr}")
```

### 2. Списки тикеров

#### Быстрый список ликвидных акций (Hardcoded)

Возвращает список самых популярных инструментов с актуальной лотностью. Работает мгновенно, без запросов к API.

```python
from FinamClient import get_fast_tickers

tickers = get_fast_tickers()
# Формат: (symbol, ticker, lot_size, name_ru)
for item in tickers[:5]:
    print(item)
# ('SBER@MISX', 'SBER', 1, 'Сбербанк')
```

#### Полный список всех активов (API)

Получает все доступные инструменты через API и подгружает лотность для каждого. **Работает медленно**, так как делает много запросов. Используйте только при необходимости получить полный универсум.

```python
from FinamClient import get_all_tickers

all_assets = get_all_tickers(client)
print(f"Total assets: {len(all_assets)}")
```

### 3. Проверка времени торгов

Проверяет, идет ли сейчас основная или вечерняя сессия на Мосбирже (МСК время).

```python
from FinamClient import is_trading_time

if is_trading_time():
    print("Рынок открыт")
else:
    print("Рынок закрыт")
```

---

## ⚠️ Важные замечания

1.  **Формат символов:** Всегда используйте формат `TICKER@MIC` (например, `SBER@MISX`).
2.  **Время:** Все временные метки в API должны быть в UTC с суффиксом `Z` (RFC 3339). Методы `get_last_..._bars` делают это автоматически.
3.  **Лотность:** При выставлении заявок количество бумаг (`quantity`) должно быть кратно лотности инструмента. Используйте `get_fast_tickers()` чтобы узнать лотность.
4.  **Ошибки:** Если токен протухнет, методы могут вернуть ошибку 401. В текущей реализации токен получается один раз при старте. Для долгоживущих скриптов рекомендуется добавить логику обновления токена при ошибке авторизации.