# tabheatcal - Heatmap visualization with easy value inspection

Tabheatcal is a python module that lets you create a nice looking heat map calendar with the ability to inspect individual values.
You can also easily add comments to particularly important events.

As you can see in the example below - the visualizations are exceptionally elegant ;-) <br>
<i>(everything is based on old html/css tables)</i>


<p align="left">
<img src="tabheatcal.gif"   width="550" style="max-width: 100%;max-height: 100%;">
</p>

The basic function requires three arguments:

* a list of dates (python datetime objects),
* a list of numeric values ​​to reflect in the color palette
* a list of labels to display on mouseover

```python
#first generate an raw html calendar
html = tabheatcal.table_html(dates, values, labels)

#create a full interactive page
tabheatcal.create_page(html, title="SP500 daily calendar heat", output="SP500.html")
```




See working examples:
<p>

<a href="https://html-preview.github.io/?url=https://github.com/ts-kontakt/tabheatcal/blob/master/NASDAQ.html" target="_blank">
NASDAQ Composite (^IXIC) daily calendar heat</a>
</p>
<p>
<a href="https://html-preview.github.io/?url=https://github.com/ts-kontakt/tabheatcal/blob/master/transactions" target="_blank">
Tesla daily transactions</a>
</p>

Result is easy to publish in an interactive form - the generated page is a regular separate html file

Full working python code for above.

```python
from html import escape
import pandas as pd
import yfinance as yf
ticker_symbol = "^IXIC"

# Valid periods: "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
df = yf.download(ticker_symbol, period="3y")

df["p_chng"] = df["Close"].pct_change() * 100
dates = [pd.to_datetime(date).date() for date in df.index.values]
values = df.p_chng.values.tolist()
labels = [
    "%+.2f %%" % val if not math.isnan(val) else "n/d" for val in df.p_chng.values
]
# Mark some important events
tariffs_day = datetime.date(2025, 4, 3)
tariffs_delayed = datetime.date(2025, 4, 9)
labels[dates.index(tariffs_day)] += "; <i>Tariffs announced!</i>"
labels[dates.index(tariffs_delayed)] += escape(
    ';tweet: <i class="emph">"THIS IS A GREAT TIME TO BUY!!! DJT"</i>'
)

html = table_html(dates, values, labels)
create_page(
    html,
    title=f"NASDAQ Composite (^IXIC) daily calendar heat",
    output="NASDAQ.html",
    startfile=True,
)
```
