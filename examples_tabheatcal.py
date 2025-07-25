import datetime
import math

import pandas as pd

import tabheatcal as tabh


def read_crime_csv( encoding='utf-8'):
    """reads from https://messerinzidenz.de"""
    import numpy as np
    try:
        df = pd.read_csv('https://messerinzidenz.de/csv',
                         sep=';',
                         quotechar='"',
                         skipinitialspace=True,
                         na_values=['', 'NULL', 'null'])

        df.columns = df.columns.str.strip().str.replace('"', '')

        string_cols = [
            'bundesland', 'id', 'link', 'location', 'similarEntry', 'suspect', 'title', 'victim'
        ]
        for col in string_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.replace('"',
                                                                      '').replace('nan', np.nan)

        numeric_cols = ['hidden', 'latitude', 'longitude', 'timeOfCrimeHourOffset', 'wounded']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        date_cols = ['date', 'timeOfCrime']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        return df

    except Exception as e:
        print(f"Error: {e}")
        return None


def create_crime_heatmap(df, output_file="crime_heatmap.html", title="Daily Crime Incidents"):
    daily_counts = df.groupby(df['date'].dt.date).size().reset_index(name='count')

    dates = [pd.to_datetime(date) for date in daily_counts['date']]
    values = daily_counts['count'].tolist()
    labels = [f"{val} incidents" for val in values]

    html = tabh.table_html(dates, values, labels, palette='Blues')
    
    info = """
      <small>This visualization uses data from <a href="https://messerinzidenz.de" target="_blank">messerinzidenz.de</a> and presents a daily 
            heatmap of knife incidents in Germany. The data presented is sad and concerning, 
            highlighting the prevalence of such crimes.</small>  
    """
    html = info + html
    tabh.create_page(html, title=title, output=output_file, startfile=True)
    

def create_crime_heatmap_by_state(df, state, output_file=None, title=None):
    state_df = df[df['bundesland'] == state]
    daily_counts = state_df.groupby(state_df['date'].dt.date).size().reset_index(name='count')

    dates = [pd.to_datetime(date) for date in daily_counts['date']]
    values = daily_counts['count'].tolist()
    labels = [f"{val} incid." for val in values]

    if not output_file:
        output_file = f"{state}_crime_heatmap.html"
    if not title:
        title = f"Daily Crime Incidents in {state}"

    html = tabh.table_html(dates, values, labels, palette='Blues')
    tabh.create_page(html, title=title, output=output_file, startfile=True)

def test_crime_heatmap():
    df = read_crime_csv( encoding='utf-8')
    create_crime_heatmap(df, output_file="crime_heatmap.html", title="Daily Crime Incidents")
    # create_crime_heatmap_by_state(df, 'Bayern', output_file="crime_heatmap.html", title="Daily Crime Incidents")

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
    tabh.create_page(html,
                     title=f"{ticker} Daily Transactions: A Heatmap Calendar Visual",
                     output=f"transactions.html")


if __name__ == "__main__":
    test_crime_heatmap()
    test_yfinance()
    test_polygon()
