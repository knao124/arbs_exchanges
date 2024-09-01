import numpy as np

from crypto_exchanges.entity.orderbook import OrderbookItem


def _get_effective_price(
    orderbook_items: list[OrderbookItem],
    target_volume: float,
) -> float:
    """指定したvolumeをtakeする際の取得価格の平均を計算する

    Args:
        orderbook_items (list[OrderbookItem]): orderbookのask or bidのlist
        target_volume (float): 取得するvolume

    Returns:
        float: 取得価格の平均
    """
    total_price = 0.0
    rest_volume = target_volume
    for item in orderbook_items:
        volume = item.volume
        price = item.price

        if rest_volume > volume:
            # 残りのvolumeよりitemのvolumeのほうが小さい場合は、そのまま加重
            total_price += price * volume
            rest_volume -= volume
        else:
            # 残りのvolumeよりitemのvolumeのほうが大きい場合は、残りのvolumeで加重
            total_price += price * rest_volume
            rest_volume = 0

        # rest_volumeが0になったら、加重平均の分母で割る
        if rest_volume == 0:
            total_price /= target_volume
            break
    if total_price == 0.0:
        return np.nan
    return total_price
