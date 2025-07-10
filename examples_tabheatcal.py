import datetime
import math

import tabheatcal as tabh


def test_yfinance():
    from html import escape

    import pandas as pd
    import yfinance as yf

    ticker_symbol = "^IXIC"

    df = yf.download(ticker_symbol, period="3y")

    df["p_chng"] = df["Close"].pct_change() * 100
    dates = [pd.to_datetime(date).date() for date in df.index.values]
    values = df.p_chng.values.tolist()
    labels = ["%+.2f %%" % val if not math.isnan(val) else "n/d" for val in df.p_chng.values]

    # Mark some important events
    tariffs_day = datetime.date(2025, 4, 3)
    tariffs_delayed = datetime.date(2025, 4, 9)
    labels[dates.index(tariffs_day)] += "; <i>Tariffs announced!</i>"
    labels[dates.index(tariffs_delayed)] += escape(
        ';tweet: <i class="emph">"THIS IS A GREAT TIME TO BUY!!! DJT"</i>')

    html = tabh.table_html(dates, values, labels)
    tabh.create_page(
        html,
        title=f"NASDAQ Composite (^IXIC) Daily Percent Change",
        output="NASDAQ.html",
        startfile=True,
    )


def test_polygon():
    millnames = ["", " K", " M", " B", " T"]

    # credits: https://stackoverflow.com/questions/3154460/python-human-readable-large-numbers
    def millify(n):
        n = float(n)
        millidx = max(
            0,
            min(
                len(millnames) - 1,
                int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3)),
            ),
        )

        return "{:.1f}{}".format(n / 10**(3 * millidx), millnames[millidx])

    from polygon import RESTClient
    from pvhelper import pgn_api_key

    #use your api key
    client = RESTClient(pgn_api_key)
    ticker = "TSLA"
    outlist = []
    for a in client.list_aggs(
            ticker=ticker,
            multiplier=1,
            timespan="day",
            from_=datetime.datetime(2023, 1, 1),
            to=datetime.datetime.today(),
    ):
        py_date = datetime.datetime.fromtimestamp(a.timestamp / 1000).date()
        outlist.append([py_date, a.transactions])
    import pandas as pd

    df = pd.DataFrame(outlist, columns=["ptime", "trans"])

    df.set_index("ptime", inplace=True)
    dates = [pd.to_datetime(date) for date in df.index.values]
    values = [int(x) for x in df.trans.values.tolist()]
    labels = [millify(val) if not math.isnan(val) else "n/d" for val in df.trans.values]
    html = tabh.table_html(dates, values, labels, palette='Blues')
    tabh.create_page(html, title=f"{ticker} Daily Transactions: A Heatmap Calendar Visual", output=f"transactions.html")


if __name__ == "__main__":
    test_yfinance()
    test_polygon()
