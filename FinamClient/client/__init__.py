#FinamClient/client/__init__.py
from datetime import datetime, timedelta, timezone
import requests

from .account import get_account_info, get_trades, get_transactions, get_orders
from .bars import get_bars
from .orders import place_order, cancel_order, get_order, place_sltp_order
from .stock import get_orderbook, get_latest_quote, get_latest_trades, get_all_assets, get_asset_info


class Client:
    def __init__(self, api_secret: str, account_id: str = None):
        self.api_secret = api_secret
        self._token = None
        self.account_id = account_id
        self._initialize()

    def _initialize(self):
        self._get_token()
        self._fetch_account_id()

    def _get_token(self):
        if self._token is None:
            self._token = self._fetch_token()
        return self._token

    def _fetch_token(self):
        import requests
        response = requests.post(
            "https://api.finam.ru/v1/sessions",
            headers={"Content-Type": "application/json"},
            json={"secret": self.api_secret}
        )
        response.raise_for_status()
        return response.json()["token"]

    def _fetch_account_id(self):
        if self.account_id:
            return
        token = self._get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            "https://api.finam.ru/v1/sessions/details",
            headers=headers,
            json={"token": token}
        )
        response.raise_for_status()
        data = response.json()
        account_ids = data.get("account_ids", [])
        if not account_ids:
            raise ValueError("No accounts found for this token")
        self.account_id = account_ids[0]

    def get_bars(self, symbol: str, timeframe: str, start_time: str, end_time: str):
        return get_bars(self._get_token(), symbol, timeframe, start_time, end_time)

    def get_last_hour_bars(self, symbol: str, n: int = 60):
        """
        Получает последние n часовых свечей для символа.
        """
        now_utc = datetime.now(timezone.utc)
        end_time = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

        start_time_dt = now_utc - timedelta(hours=n)
        start_time = start_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        return self.get_bars(symbol, "TIME_FRAME_H1", start_time, end_time)

    def get_last_min_bars(self, symbol: str, n: int = 60):
        """
        Получает последние n минутных свечей для символа.
        """
        now_utc = datetime.now(timezone.utc)
        end_time = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

        start_time_dt = now_utc - timedelta(minutes=n)
        start_time = start_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        return self.get_bars(symbol, "TIME_FRAME_M1", start_time, end_time)

    def get_orderbook(self, symbol: str):
        return get_orderbook(self._get_token(), symbol)

    def get_latest_quote(self, symbol: str):
        from .stock import get_latest_quote as gq
        return gq(self._get_token(), symbol)

    def get_latest_trades(self, symbol: str):
        from .stock import get_latest_trades as glt
        return glt(self._get_token(), symbol)

    def get_account_info(self, account_id: str):
        return get_account_info(self._get_token(), account_id)

    def get_trades(self, account_id: str, limit: int = None, start_time: str = None, end_time: str = None):
        return get_trades(self._get_token(), account_id, limit, start_time, end_time)

    def get_transactions(self, account_id: str, limit: int = None, start_time: str = None, end_time: str = None):
        return get_transactions(self._get_token(), account_id, limit, start_time, end_time)

    def get_orders(self, account_id: str):
        return get_orders(self._get_token(), account_id)

    def place_order(self, account_id: str, order_data: dict):
        return place_order(self._get_token(), account_id, order_data)

    def cancel_order(self, account_id: str, order_id: str):
        return cancel_order(self._get_token(), account_id, order_id)

    def get_order(self, account_id: str, order_id: str):
        return get_order(self._get_token(), account_id, order_id)

    def place_sltp_order(self, account_id: str, sltp_data: dict):
        return place_sltp_order(self._get_token(), account_id, sltp_data)
