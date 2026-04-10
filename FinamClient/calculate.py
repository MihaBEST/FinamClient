import pandas as pd
from .client.stock import get_asset_info, get_all_assets
from datetime import datetime, time, timedelta
import pytz


def is_trading_time():
    moscow_tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(moscow_tz)
    t = now.time()
    if now.weekday() >= 5: return False
    return (time(9, 50) <= t <= time(18, 50)) or (time(19, 0) <= t <= time(23, 50))


def format_assets_with_lot_sizes(client, symbols_list):
    """
    Принимает список символов (например, ['SBER@MISX', 'GAZP@MISX'])
    и для каждого получает лотность через API.
    Возвращает список кортежей: (symbol, ticker, lot_size)
    """
    result = []
    for symbol in symbols_list:
        try:
            ticker = symbol.split('@')[0] if '@' in symbol else symbol
            asset_info = get_asset_info(client._token, symbol)

            lot_size_str = asset_info.get('lot_size', {}).get('value', '1')
            lot_size = int(lot_size_str)

            result.append((symbol, ticker, lot_size))
        except Exception as e:
            print(f"Error fetching info for {symbol}: {e}")
            result.append((symbol, symbol.split('@')[0], 1))

    return result


def get_all_tickers(client):
    """
    Получает актуальный список тикеров через FinamClient и их лотности.
    """
    try:
        assets_data = get_all_assets(client._token)
        assets_list = assets_data.get('assets', [])

        symbols = [asset['symbol'] for asset in assets_list if 'symbol' in asset]

        return format_assets_with_lot_sizes(client, symbols)

    except Exception as e:
        print(f"Error fetching assets list: {e}")
        return []


def prepare_candles(candles, window=60):
    """Ограничивает данные последними `window` свечами"""
    if len(candles) > window:
        return candles.tail(window).reset_index(drop=True)
    return candles


def calculate_indicators(candles):
    """Получает на вход свечи(минутные) в виде nparr полученые с помощью клиента
    Возвращает ema, rsi, atr"""
    candles = prepare_candles(candles)
    prices = candles['close']
    high = candles['high']
    low = candles['low']

    # EMA20
    ema20 = prices.ewm(span=20).mean().iloc[-1]

    # RSI14
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs)).iloc[-1]

    # ATR14
    high_low = high - low
    high_close = (high - prices.shift()).abs()
    low_close = (low - prices.shift()).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(14).mean().iloc[-1]

    return ema20, rsi, atr


def calculate_ema20(candles):
    """
    Экспоненциальное скользящее среднее за 20 периодов.
    Используется для определения тренда:
      - цена выше EMA → восходящий тренд,
      - цена ниже EMA → нисходящий тренд.
    Более чувствительно к недавним ценам, чем SMA.
    """
    if len(candles) > 60:
        candles = candles[-60:]
    return candles['close'].ewm(span=20, adjust=False).mean().iloc[-1]


def calculate_rsi14(candles):
    """
    Индекс относительной силы (0–100).
    Показывает перекупленность/перепроданность:
      - RSI > 70 → перекупленность (возможен разворот вниз),
      - RSI < 30 → перепроданность (возможен рост).
    Используется для фильтрации сигналов.
    """
    if len(candles) > 60:
        candles = candles[-60:]

    close = candles['close']
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # Используем сглаживание по Уайлдеру (Wilder's smoothing)
    avg_gain = gain.ewm(alpha=1 / 14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / 14, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]


def calculate_atr14(candles):
    """
    Средний истинный диапазон — мера волатильности.
    Показывает, насколько цена "движется" в среднем за период.
    Используется для:
      - установки стоп-лосса и тейк-профита (например, 2×ATR),
      - фильтрации шумных/тихих рынков.
    """
    if len(candles) > 60:
        candles = candles[-60:]

    high = candles['high']
    low = candles['low']
    close = candles['close']

    tr0 = high - low
    tr1 = (high - close.shift()).abs()
    tr2 = (low - close.shift()).abs()

    true_range = pd.concat([tr0, tr1, tr2], axis=1).max(axis=1)
    atr = true_range.ewm(alpha=1 / 14, adjust=False).mean()  # Wilder's smoothing
    return atr.iloc[-1]


def calculate_macd(candles):
    """
    MACD = EMA(12) - EMA(26)
    Signal = EMA(MACD, 9)
    Histogram = MACD - Signal

    Используется для:
      - определения импульса,
      - поиска дивергенций,
      - подтверждения тренда.

    Возвращает: (macd_line, signal_line, histogram)
    """
    if len(candles) > 60:
        candles = candles[-60:]

    close = candles['close']
    ema_fast = close.ewm(span=12, adjust=False).mean()
    ema_slow = close.ewm(span=26, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line

    return macd_line.iloc[-1], signal_line.iloc[-1], histogram.iloc[-1]


def calculate_bbands_width(candles):
    """
    Ширина полос Боллинджера = (Верхняя полоса - Нижняя полоса) / Средняя
    Мера волатильности:
      - узкие полосы → низкая волатильность (ожидается пробой),
      - широкие → высокая волатильность.
    """
    if len(candles) > 60:
        candles = candles[-60:]

    close = candles['close']
    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    upper = sma20 + 2 * std20
    lower = sma20 - 2 * std20
    width = (upper - lower) / sma20
    return width.iloc[-1]


def get_fast_tickers():
    """
    Возвращает список самых ликвидных инструментов Мосбиржи.
    Формат: (symbol, ticker, lot_size, name_ru)
    Symbol в формате Finam: TICKER@MISX
    """
    return [
        ('SBER@MISX', 'SBER', 1, 'Сбербанк'),
        ('GAZP@MISX', 'GAZP', 10, 'Газпром'),
        ('LKOH@MISX', 'LKOH', 1, 'Лукойл'),
        ('NVTK@MISX', 'NVTK', 1, 'Новатэк'),
        ('ROSN@MISX', 'ROSN', 1, 'Роснефть'),
        ('GMKN@MISX', 'GMKN', 10, 'Норникель'),
        ('PLZL@MISX', 'PLZL', 1, 'Полюс'),
        ('TATN@MISX', 'TATN', 1, 'Татнефть'),
        ('SNGS@MISX', 'SNGS', 100, 'Сургутнефтегаз'),
        ('SNGSP@MISX', 'SNGSP', 10, 'Сургутнефтегаз-п'),
        ('ALRS@MISX', 'ALRS', 10, 'Алроса'),
        ('CHMF@MISX', 'CHMF', 1, 'Северсталь'),
        ('NLMK@MISX', 'NLMK', 10, 'НЛМК'),
        ('MGNT@MISX', 'MGNT', 1, 'Магнит'),
        ('MTSS@MISX', 'MTSS', 10, 'МТС'),
        ('MOEX@MISX', 'MOEX', 10, 'Московская Биржа'),
        ('VTBR@MISX', 'VTBR', 1, 'ВТБ'),
        ('HYDR@MISX', 'HYDR', 1000, 'РусГидро'),
        ('FEES@MISX', 'FEES', 10000, 'ФСК ЕЭС'),
        ('IRAO@MISX', 'IRAO', 100, 'Интер РАО'),
        ('RTKM@MISX', 'RTKM', 10, 'Ростелеком'),
        ('RTKMP@MISX', 'RTKMP', 10, 'Ростелеком-п'),
        ('PHOR@MISX', 'PHOR', 1, 'ФосАгро'),
        ('MAGN@MISX', 'MAGN', 10, 'ММК'),
        ('AFKS@MISX', 'AFKS', 100, 'АФК Система'),
        ('RUAL@MISX', 'RUAL', 10, 'РУСАЛ'),
        ('PIKK@MISX', 'PIKK', 1, 'ПИК'),
        ('LSRG@MISX', 'LSRG', 1, 'ЛСР'),
        ('AFLT@MISX', 'AFLT', 10, 'Аэрофлот'),
        ('BANEP@MISX', 'BANEP', 1, 'Башнефть-п'),
        ('MTLR@MISX', 'MTLR', 1, 'Мечел'),
        ('SBERP@MISX', 'SBERP', 1, 'Сбербанк-п'),
        ('YNDX@MISX', 'YNDX', 1, 'Яндекс'),
        ('OZON@MISX', 'OZON', 1, 'Ozon'),
        ('VKCO@MISX', 'VKCO', 1, 'VK')
    ]
