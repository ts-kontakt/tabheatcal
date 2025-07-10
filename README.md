# tabheatcal - Heatmap Calendar Visualization with Interactive Value Inspection

Tabheatcal is a Python module that creates elegant heatmap calendars with interactive value inspection capabilities. Perfect for visualizing time-series data like stock prices, transaction volumes, or any daily metrics over time.

## Features

- **Interactive Heatmaps**: Hover over any day to see detailed information
- **Custom Color Palettes**: Choose from various color schemes (RdYlGn, Blues, etc.)
- **Event Annotations**: Add custom comments to highlight important dates
- **Multi-Year Support**: Automatically handles datasets spanning multiple years
- **Standalone HTML Output**: Generate self-contained HTML files for easy sharing

![Example visualization](https://github.com/ts-kontakt/tabheatcal/blob/main/tabheatcal.gif?raw=true)

*The visualizations use hand-crafted HTML and CSS with table-based layouts for maximum compatibility.*

## Quick Start

The basic function requires three arguments:

- **dates**: List of Python datetime objects
- **values**: List of numeric values to visualize with colors
- **labels**: List of labels to display on mouseover

```python
import tabheatcal

# Generate raw HTML calendar
html = tabheatcal.table_html(dates, values, labels)

# Create full interactive page
tabheatcal.create_page(html, title="My Data Heatmap", output="output.html")
```

## Complete Example: Stock Market Data

```python
import datetime
import math
from html import escape
import pandas as pd
import yfinance as yf
import tabheatcal

# Download stock data
ticker_symbol = "^IXIC"  # NASDAQ Composite
df = yf.download(ticker_symbol, period="3y")

# Calculate daily percent changes
df["p_chng"] = df["Close"].pct_change() * 100

# Prepare data for visualization
dates = [pd.to_datetime(date).date() for date in df.index.values]
values = df.p_chng.values.tolist()
labels = ["%+.2f %%" % val if not math.isnan(val) else "n/d" for val in df.p_chng.values]

# Add event annotations
tariffs_day = datetime.date(2025, 4, 3)
tariffs_delayed = datetime.date(2025, 4, 9)
labels[dates.index(tariffs_day)] += "; <i>Tariffs announced!</i>"
labels[dates.index(tariffs_delayed)] += escape(
    ';tweet: <i class="emph">"THIS IS A GREAT TIME TO BUY!!! DJT"</i>'
)

# Generate visualization
html = tabheatcal.table_html(dates, values, labels)
tabheatcal.create_page(
    html,
    title="NASDAQ Composite (^IXIC) Daily Percent Change",
    output="NASDAQ.html",
    startfile=True
)
```

## API Reference

### `table_html(dates, values, labels, palette="RdYlGn")`

The table_html() function returns raw HTML that can be embedded directly into web frameworks without creating separate files:

**Parameters:**
- `dates` (list): List of datetime.date objects
- `values` (list): Numeric values for color mapping
- `labels` (list): Hover labels for each date
- `palette` (str): Color palette name (default: "RdYlGn")

**Returns:** HTML string containing the heatmap table

### `create_page(html, title, output="output.html", startfile=True)`

Creates a complete HTML page with the heatmap.

**Parameters:**
- `html` (str): HTML table from `table_html()`
- `title` (str): Page title
- `output` (str): Output filename (default: "output.html")
- `startfile` (bool): Whether to open the file automatically (default: True)

## Color Palettes

Available color palettes include:
- `RdYlGn` (Red-Yellow-Green) - Default, good for showing positive/negative changes
- `Blues` - Blue gradient, good for showing intensity/volume
- `Spectral` - Spectral color scheme with smooth transitions
- `Spectral1` - Reverse spectral color scheme
- Custom palettes can be added to the `assets.py` file

**Note:** The module automatically detects and handles outliers in your data using statistical methods (values beyond 4 standard deviations from the mean). However, for very noisy datasets, it's recommended to normalize or preprocess your data before visualization to ensure optimal color mapping and visual clarity.

## Live Examples
Note: The interactive features (hover tooltips, etc.) may not work in GitHub's HTML preview due to JavaScript restrictions. Download the HTML files and open them locally for full functionality.
<p>
<a href="https://html-preview.github.io/?url=https://github.com/ts-kontakt/tabheatcal/blob/master/NASDAQ.html" target="_blank">
📈 NASDAQ Composite (^IXIC) Daily Calendar Heat</a>
</p>

Using Polygon API for Financial Data
Here's an example showing daily transaction volume.


<p>
<a href="https://html-preview.github.io/?url=https://github.com/ts-kontakt/tabheatcal/blob/master/transactions.html" target="_blank">
📊 Tesla Daily Transactions Volume</a>
</p>

## Demo

Run the included demo to see the module in action:

```python
import tabheatcal
tabheatcal.demo()  # Creates a demo with random data
```

## Dependencies

- `numpy` - For numerical operations
- `jinja2` - For HTML templating
- `pandas` - For data manipulation (in examples)
- `yfinance` - For stock data (in examples)

## Installation

```bash
pip install numpy jinja2
```

For the examples, also install:
```bash
pip install pandas yfinance
```

## Output

The generated HTML files are:
- **Self-contained**: No external dependencies
- **Interactive**: Hover effects and tooltips
- **Responsive**: Works across different screen sizes
- **Shareable**: Easy to host or embed

## Advanced Usage

### Custom Event Annotations

```python
# Add custom styling to specific dates
special_date_index = dates.index(datetime.date(2025, 1, 15))
labels[special_date_index] += "; <b>Important Event!</b>"
```

### Multiple Years

The module automatically handles datasets spanning multiple years, displaying them in reverse chronological order (most recent first).

### Data Preprocessing

The module includes automatic outlier detection (removing values beyond 4 standard deviations from the mean) and handles NaN values gracefully. For very noisy datasets with extreme outliers, consider preprocessing your data:

```python
import numpy as np

# Example: Cap extreme values at 95th/5th percentiles
def normalize_data(values):
    values = np.array(values)
    p95, p5 = np.nanpercentile(values, [95, 5])
    return np.clip(values, p5, p95)

# Apply normalization before visualization
normalized_values = normalize_data(values)
html = tabheatcal.table_html(dates, normalized_values, labels)
```

This ensures optimal color mapping and visual clarity across the entire dataset.


## Author

Copyright (c) Tomasz Sługocki
