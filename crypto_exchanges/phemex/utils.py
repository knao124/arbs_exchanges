def default_sub_type(symbol: str):
    # linear or spot -> settle curreyncy is USD
    if ":USD" in symbol or "u" in symbol or "s" in symbol:
        return "linear"

    # BTC coin margin
    return "inverse"
