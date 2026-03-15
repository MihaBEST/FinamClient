from finam_trade_api import Client
from finam_trade_api.order import OrderType, Side, TimeInForce
from datetime import datetime, timedelta
from decimal import Decimal
import pandas as pd
import asyncio


class FinamClient:
    def __init__(self, secret_token, account_id=None):
        self.secret_token = secret_token
        self.account_id = account_id
        self.client = None

        self.printlog = False
        self.filelog = True
        self.logfilename = "log.txt"

    async def __aenter__(self):
        # Инициализация асинхронного клиента
        self.client = Client(token=self.secret_token)
        await self.client.__aenter__()

        if not self.account_id:
            self.account_id = await self.get_account_id()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)

    def log(self, text):
        if self.printlog:
            print(text)
        if self.filelog:
            with open(self.logfilename, "a", encoding='utf-8') as f:
                f.write(text + "\n")

    async def get_account_id(self):
        """Получение ID счета по умолчанию"""
        try:
            accounts = await self.client.get_accounts()
            if not accounts:
                raise ValueError("Не найдено доступных счетов")
            return accounts[0].account_id
        except Exception as e:
            self.log(f"❌ Ошибка получения счета: {e}")
            raise

    # ==========================================
    # ТОРГОВЫЕ ОПЕРАЦИИ (Аналог Tinkoff)
    # ==========================================

    async def buy(self, security_code, lots, price=None, board="TQBR"):
        """Покупка по рынку или лимиту"""
        try:
            order_type = OrderType.Limit if price else OrderType.Market
            request = {
                "account_id": self.account_id,
                "security_code": security_code,
                "board": board,
                "side": Side.Buy,
                "type": order_type,
                "qty": lots,
                "time_in_force": TimeInForce.Day
            }
            if price:
                request["price"] = price

            response = await self.client.create_order(**request)
            self.log(f"✅ Заявка на покупку создана: {response.order_id}")
            return True
        except Exception as e:
            self.log(f"❌ Ошибка покупки: {e}")
            return False

    async def sell(self, security_code, lots, price=None, board="TQBR"):
        """Продажа по рынку или лимиту"""
        try:
            order_type = OrderType.Limit if price else OrderType.Market
            request = {
                "account_id": self.account_id,
                "security_code": security_code,
                "board": board,
                "side": Side.Sell,
                "type": order_type,
                "qty": lots,
                "time_in_force": TimeInForce.Day
            }
            if price:
                request["price"] = price

            response = await self.client.create_order(**request)
            self.log(f"✅ Заявка на продажу создана: {response.order_id}")
            return True
        except Exception as e:
            self.log(f"❌ Ошибка продажи: {e}")
            return False

    async def create_short_position(self, security_code, lots, price=None, board="TQBR"):
        """Открытие шорт-позиции (продажа без покрытия)"""
        # В Finam шорты открываются обычной заявкой Sell при наличии маржи
        return await self.sell(security_code, lots, price, board)

    async def close_short_position(self, security_code, lots, price=None, board="TQBR"):
        """Закрытие шорт-позиции (покупка для покрытия)"""
        return await self.buy(security_code, lots, price, board)

    # ==========================================
    # СТОП-ОРДЕРА (Stop-Loss / Take-Profit)
    # ==========================================

    async def stop_loss_order(self, security_code, lots, stop_price, board="TQBR"):
        """Стоп-лосс для лонга (продажа при падении)"""
        try:
            # Finam API может требовать специфики для стоп-ордеров
            # Здесь упрощенная реализация через лимитную заявку
            request = {
                "account_id": self.account_id,
                "security_code": security_code,
                "board": board,
                "side": Side.Sell,
                "type": OrderType.StopLimit,
                "qty": lots,
                "stop_price": stop_price,
                "price": stop_price * 0.99,  # Цена исполнения чуть ниже стопа
                "time_in_force": TimeInForce.Day
            }
            response = await self.client.create_order(**request)
            self.log(f"✅ Stop-Loss создан: {response.order_id}")
            return True
        except Exception as e:
            self.log(f"❌ Ошибка создания Stop-Loss: {e}")
            return False

    async def take_profit_order(self, security_code, lots, take_price, board="TQBR"):
        """Тейк-профит для лонга (продажа при росте)"""
        try:
            request = {
                "account_id": self.account_id,
                "security_code": security_code,
                "board": board,
                "side": Side.Sell,
                "type": OrderType.StopLimit,
                "qty": lots,
                "stop_price": take_price,
                "price": take_price * 1.01,  # Цена исполнения чуть выше
                "time_in_force": TimeInForce.Day
            }
            response = await self.client.create_order(**request)
            self.log(f"✅ Take-Profit создан: {response.order_id}")
            return True
        except Exception as e:
            self.log(f"❌ Ошибка создания Take-Profit: {e}")
            return False

    async def stop_loss_short(self, security_code, lots, stop_price, board="TQBR"):
        """Стоп-лосс для шорта (покупка при росте цены)"""
        try:
            request = {
                "account_id": self.account_id,
                "security_code": security_code,
                "board": board,
                "side": Side.Buy,
                "type": OrderType.StopLimit,
                "qty": lots,
                "stop_price": stop_price,
                "price": stop_price * 1.01,
                "time_in_force": TimeInForce.Day
            }
            response = await self.client.create_order(**request)
            self.log(f"✅ Stop-Loss (Short) создан: {response.order_id}")
            return True
        except Exception as e:
            self.log(f"❌ Ошибка создания Stop-Loss для шорта: {e}")
            return False

    async def take_profit_short(self, security_code, lots, take_price, board="TQBR"):
        """Тейк-профит для шорта (покупка при падении цены)"""
        try:
            request = {
                "account_id": self.account_id,
                "security_code": security_code,
                "board": board,
                "side": Side.Buy,
                "type": OrderType.StopLimit,
                "qty": lots,
                "stop_price": take_price,
                "price": take_price * 0.99,
                "time_in_force": TimeInForce.Day
            }
            response = await self.client.create_order(**request)
            self.log(f"✅ Take-Profit (Short) создан: {response.order_id}")
            return True
        except Exception as e:
            self.log(f"❌ Ошибка создания Take-Profit для шорта: {e}")
            return False

    # ==========================================
    # ПОРТФЕЛЬ И БАЛАНСЫ
    # ==========================================

    async def get_portfolio(self):
        """Получение полного портфеля"""
        try:
            positions = await self.client.get_positions(self.account_id)
            return positions
        except Exception as e:
            self.log(f"❌ Ошибка получения портфеля: {e}")
            return None

    async def get_portfolio_summary(self):
        """Сводка по портфелю в формате dict (как в TinkoffClient)"""
        try:
            positions = await self.client.get_positions(self.account_id)

            summary = {
                'total_amount_shares': 0.0,
                'total_amount_bonds': 0.0,
                'total_amount_etf': 0.0,
                'total_amount_currencies': 0.0,
                'total_amount_futures': 0.0,
                'expected_yield': 0.0,
                'positions': []
            }

            for pos in positions:
                qty = float(pos.qty) if pos.qty else 0.0
                avg_price = float(pos.avg_price) if pos.avg_price else 0.0
                current_price = float(pos.current_price) if pos.current_price else 0.0

                position_info = {
                    'security_code': pos.security_code,
                    'board': pos.board,
                    'instrument_type': getattr(pos, 'instrument_type', 'share'),
                    'quantity': qty,
                    'average_price': avg_price,
                    'current_price': current_price,
                    'expected_yield': (current_price - avg_price) * qty,
                    'currency': getattr(pos, 'currency', 'RUB')
                }
                summary['positions'].append(position_info)

                # Агрегация по типам (упрощенно)
                if pos.instrument_type == 'bond':
                    summary['total_amount_bonds'] += qty * current_price
                elif pos.instrument_type == 'currency':
                    summary['total_amount_currencies'] += qty * current_price
                else:
                    summary['total_amount_shares'] += qty * current_price

            return summary
        except Exception as e:
            self.log(f"❌ Ошибка получения сводки портфеля: {e}")
            return None

    async def get_balances(self):
        """Балансы по валютам"""
        try:
            positions = await self.client.get_positions(self.account_id)
            balances = {}

            for pos in positions:
                if getattr(pos, 'instrument_type', None) == 'currency':
                    currency = getattr(pos, 'currency', 'RUB').lower()
                    balance = float(pos.qty) if pos.qty else 0.0
                    balances[currency] = balance

            return balances
        except Exception as e:
            self.log(f"❌ Ошибка получения балансов: {e}")
            return None

    async def get_free_rub_balance(self):
        """Свободный остаток рублей"""
        balances = await self.get_balances()
        return balances.get('rub', 0.0) if balances else 0.0

    async def get_positions_list(self):
        """Список позиций (исключая валюты)"""
        try:
            positions = await self.client.get_positions(self.account_id)
            result = []

            for pos in positions:
                if getattr(pos, 'instrument_type', None) == 'currency':
                    continue

                qty = float(pos.qty) if pos.qty else 0.0
                avg_price = float(pos.avg_price) if pos.avg_price else 0.0
                current_price = float(pos.current_price) if pos.current_price else 0.0

                result.append({
                    'security_code': pos.security_code,
                    'board': pos.board,
                    'balance': qty,
                    'average_price': avg_price,
                    'current_price': current_price,
                    'expected_yield': (current_price - avg_price) * qty,
                    'currency': getattr(pos, 'currency', 'RUB')
                })

            return result
        except Exception as e:
            self.log(f"❌ Ошибка получения списка позиций: {e}")
            return None

    # ==========================================
    # РЫНОЧНЫЕ ДАННЫЕ (Стакан, Свечи)
    # ==========================================

    async def get_order_book(self, security_code, depth=10, board="TQBR"):
        """
        Получает стакан по инструменту.
        Возвращает: {'bids': [(price, qty), ...], 'asks': [(price, qty), ...]}
        """
        try:
            ob = await self.client.get_orderbook(security_code, board, depth)

            bids = [(float(b.price), float(b.qty)) for b in ob.bids] if ob.bids else []
            asks = [(float(a.price), float(a.qty)) for a in ob.asks] if ob.asks else []

            return {"bids": bids, "asks": asks}
        except Exception as e:
            self.log(f"❌ Ошибка получения стакана для {security_code}: {e}")
            return {"bids": [], "asks": []}

    async def get_candles_min(self, security_code, board="TQBR", days=1):
        """Получение минутных свечей"""
        try:
            from_date = datetime.now() - timedelta(days=days)
            candles = await self.client.get_candles(
                security_code,
                board,
                from_date,
                datetime.now(),
                interval=1  # 1 минута
            )

            data = []
            for c in candles:
                data.append({
                    'time': c.time,
                    'open': float(c.open),
                    'high': float(c.high),
                    'low': float(c.low),
                    'close': float(c.close),
                    'volume': float(c.volume)
                })

            return pd.DataFrame(data)
        except Exception as e:
            self.log(f"❌ Ошибка получения минутных свечей {security_code}: {e}")
            return pd.DataFrame()

    async def get_candles_hour(self, security_code, board="TQBR", days=7):
        """Получение часовых свечей"""
        try:
            from_date = datetime.now() - timedelta(days=days)
            candles = await self.client.get_candles(
                security_code,
                board,
                from_date,
                datetime.now(),
                interval=60  # 60 минут
            )

            data = []
            for c in candles:
                data.append({
                    'time': c.time,
                    'open': float(c.open),
                    'high': float(c.high),
                    'low': float(c.low),
                    'close': float(c.close),
                    'volume': float(c.volume)
                })

            return pd.DataFrame(data)
        except Exception as e:
            self.log(f"❌ Ошибка получения часовых свечей {security_code}: {e}")
            return pd.DataFrame()

    async def check_short_availability(self, security_code, board="TQBR"):
        """Проверка доступности шорт-продажи (упрощенно)"""
        try:
            # В Finam нет прямого флага, проверяем наличие инструмента
            info = await self.client.get_security_info(security_code, board)
            return info is not None
        except Exception as e:
            self.log(f"❌ Ошибка проверки доступности шорт-продажи: {e}")
            return False
