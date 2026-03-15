import pandas as pd

def get_tickers():
    """тикер, компания, лотность"""
    return [
        ('SBER', 'Сбербанк', 1),
        ('SBERP', 'Сбербанк-п', 1),
        ('GAZP', 'Газпром', 10),
        ('LKOH', 'Лукойл', 1),
        ('ROSN', 'Роснефть', 1),
        ('NVTK', 'Новатэк', 1),
        ('TATN', 'Татнефть', 1),
        ('GMKN', 'Норникель', 10),
        ('PLZL', 'Полюс', 1),
        ('ALRS', 'Алроса', 10),
        ('PHOR', 'ФосАгро', 1),
        ('MGNT', 'Магнит', 1),
        ('AFKS', 'Система', 100),
        ('AFLT', 'Аэрофлот', 10),
        ('NLMK', 'НЛМК', 10),
        ('MTSS', 'МТС', 10),
        ('VTBR', 'ВТБ', 1),
        ('MOEX', 'Московская биржа', 10),
        ('QIWI', 'QIWI', 1),
        ('RUAL', 'РУСАЛ', 10),
        ('CHMF', 'Северсталь', 1),
        ('SNGS', 'Сургутнефтегаз', 100),
        ('SNGSP', 'Сургутнефтегаз-п', 10),
        ('BANEP', 'Башнефть-п', 1),
        ('HYDR', 'РусГидро', 1000),
        ('IRAO', 'Интер РАО', 100),
        ('LSRG', 'ЛСР', 1),
        ('MAGN', 'ММК', 10),
        ('MTLR', 'Мечел', 1),
        ('RTKM', 'Ростелеком', 10),
        ('RTKMP', 'Ростелеком-п', 10),
        ('FEES', 'ФСК ЕЭС', 10000),
        ('PIKK', 'ПИК', 1)
    ]

def get_short_tickers():
    return [
        ('SBER', 'Сбербанк', 1),
        ('SBERP', 'Сбербанк-п', 1),
        ('GAZP', 'Газпром', 10),
        ('LKOH', 'Лукойл', 1),
        ('ROSN', 'Роснефть', 1),
        ('NVTK', 'Новатэк', 1),
        ('TATN', 'Татнефть', 1),
        ('GMKN', 'Норникель', 10),
        ('PLZL', 'Полюс', 1),
        ('ALRS', 'Алроса', 10),
        ('PHOR', 'ФосАгро', 1),
        ('MGNT', 'Магнит', 1),
        ('AFKS', 'Система', 100),
        ('AFLT', 'Аэрофлот', 10),
        ('NLMK', 'НЛМК', 10),
        ('MTSS', 'МТС', 10),
        ('VTBR', 'ВТБ', 1),
        ('MOEX', 'Московская биржа', 10),
        ('RUAL', 'РУСАЛ', 10),
        ('CHMF', 'Северсталь', 1),
        ('SNGS', 'Сургутнефтегаз', 100),
        ('SNGSP', 'Сургутнефтегаз-п', 10),
        ('BANEP', 'Башнефть-п', 1),
        ('HYDR', 'РусГидро', 1000),
        ('IRAO', 'Интер РАО', 100),
        ('LSRG', 'ЛСР', 1),
        ('MAGN', 'ММК', 10),
        ('MTLR', 'Мечел', 1),
        ('RTKM', 'Ростелеком', 10),
        ('RTKMP', 'Ростелеком-п', 10),
        ('FEES', 'ФСК ЕЭС', 10000),
        ('PIKK', 'ПИК', 1)
    ]

def prepare_candles(candles, window=60):
    """Ограничивает данные последними `window` свечами"""
    if len(candles) > window:
        return candles.tail(window).reset_index(drop=True)
    return candles


def calculate_indicators(candles):
    """Получает на вход свечи(минутные) в виде nparr полученые с помощью клиента
    Возвращает ema, rsi, atr"""
    # Предполагаем, что candles - DataFrame с колонками 'close', 'high', 'low'
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
    avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()

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
    atr = true_range.ewm(alpha=1/14, adjust=False).mean()  # Wilder's smoothing
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