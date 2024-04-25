import time
from hyperliquid.info import Info
from hyperliquid.utils import constants as hl_constants
import utils.now_timestamp as now_timestamp 
import models.candles as candles
import importlib
importlib.reload(candles)
importlib.reload(now_timestamp)
info = Info(hl_constants.MAINNET_API_URL, skip_ws=True)


def _bar_count_to_start_end(
    bar_count,
    interval,
):
    end = now_timestamp.get_timestamp_from_today_midnight_utc(days=0)
    
    if interval == '1m':
        start = end - 1000 * 60 * bar_count
    elif interval == '5m':
        start = end - 1000 * 60 * 5 * bar_count
    elif interval == '15m':
        start = end - 1000 * 60 * 15 * bar_count
    elif interval == '1h':
        start = end - 1000 * 60 * 60 * bar_count
    elif interval == '4h':
        start = end - 1000 * 60 * 60 * 4 * bar_count
    elif interval == '1d':
        start = end - 1000 * 60 * 60 * 24 * bar_count
    elif interval == '1w':
        start = end - 1000 * 60 * 60 * 24 * 7 * bar_count
    else:
        raise ValueError(f"Invalid interval: {interval}")

    return start, end

def fetch_coin(
        coin,
        interval='15m',
        bar_count=1000,
    ):
    print(coin)
    start, end = _bar_count_to_start_end(bar_count, interval)
    result = info.candles_snapshot(coin, interval, start, end)
    _candles = candles.CandleList.from_response(result)
    _candles.to_csv(file_name=f'{coin}_{interval}_{bar_count}.csv')
    return _candles.to_df()


# fetch_coins_by_names(top_n_coins)