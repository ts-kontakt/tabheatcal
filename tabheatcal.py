#!/usr/bin/python
# coding=utf-8'
#
# Copyright (c)  Tomasz Sługocki ts.kontakt@gmail.com
# This code is licensed under Apache 2.0
import calendar
import datetime
import json
import math
import os
import re
import subprocess
import sys

import numpy as np

import assets

strftime = datetime.datetime.strftime

TEMPLATE = "_template.html"
EMPTY_CELL = "empty"

WEEKDAYS_NAMES = calendar.day_name
WEEKDAYS_ORDER = (6, 0, 1, 2, 3, 4, 5, )


def get_distance(x, y):
    try:
        return math.sqrt((x - y) ** 2)
    except ValueError:
        return 0


def minify(htmlcode):
    htmlcode = htmlcode.replace("\n", "")
    htmlcode = re.sub("\\s{2,}", " ", htmlcode)
    htmlcode = htmlcode.replace("> <", "><")
    return htmlcode


def open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])


def set_days(year, starting_month=1, end_month=12):
    mcal = calendar.Calendar()
    weekdays_obj = {
        6: [],
        0: [],
        1: [],
        2: [],
        3: [],
        4: [],
        5: [],
    }
    for month in range(starting_month, end_month + 1):
        month_days = mcal.monthdatescalendar(year, month)
        for row in month_days:
            for date in row:
                if date.month == month:
                    # strftime(date, "%b %d")
                    weekdays_obj[date.weekday()].append(date)
    return weekdays_obj


def year_table(current_year, start_month=1, end_month=12, color_object=None):
    def make_cell(inner_html, style="", rel="", id=""):
        if style:
            style = f'style="{style}"'
        if rel:
            rel = f'rel="{rel}"'
        if id:
            id = f'id="{id}"'
        attributes = " ".join((style, rel, id))
        return f"<td {attributes} >{inner_html}</td>"

    def make_row(inner_html):
        return f"<tr>{inner_html}</tr>"

    left_border = "border-left:black 1px solid;"
    left_top_border = "border-left:black 1px solid;border-top:black 1px solid;"
    top_border = "border-top:gray 1px solid;"

    weekdays_data = set_days(
        current_year, starting_month=start_month, end_month=end_month
    )
    first_day_of_year = datetime.date(current_year, start_month, 1)

    if first_day_of_year.weekday() != 6:
        for i in range(0, first_day_of_year.weekday() + 1):
            weekdays_data[WEEKDAYS_ORDER[i]].insert(0, EMPTY_CELL)

    bottom_table_headers, table_rows = [], []
    for weekday in WEEKDAYS_ORDER:
        table_cells = []
        previous_month = None
        bottom_column_span = 0

        for date_item in weekdays_data[weekday]:
            if date_item != EMPTY_CELL:
                is_empty = False
                date_string_key = strftime(date_item, "%Y-%m-%d")
                background_color = color_object.get(date_string_key, {}).get(
                    "color", "white"
                )
                date_display_string = color_object.get(date_string_key, {}).get(
                    "info", date_string_key
                )
                current_month = date_item.month
                current_day = date_item.day
            else:
                background_color = ""
                is_empty = True
                date_display_string = ""
                current_month = 0
                previous_month = None
                current_day = 0
            css_color_styles = (
                f"background:{background_color};color:{background_color};"
            )

            cell_style = css_color_styles
            if previous_month != current_month and is_empty != True:
                if current_day == 1:
                    cell_style = left_top_border + css_color_styles
                else:
                    cell_style = left_border + css_color_styles

            if weekday == 6:
                cell_style += top_border

            cell_inner_html = "."
            if is_empty:
                cell_inner_html = "@"
                cell_style = "border:white 1px solid;"

            table_cell = make_cell(
                cell_inner_html, style=cell_style, rel=date_display_string
            )

            saturday_first_day = (
                weekday == 5
                and current_month != start_month
                and previous_month != current_month
            )

            if saturday_first_day:
                if previous_month:
                    month_name = strftime(
                        datetime.datetime(current_year, previous_month, 1), "%b"
                    )
                else:
                    month_name = "__"

                bottom_header_string = f'<td colspan="{bottom_column_span}"><span class="bott_cal_th">{month_name}</span></td>'

                # for years starting with  Sunday we need add extra th row
                if first_day_of_year.weekday() == 6 and previous_month == 1:
                    bottom_header_string = (
                        '<th style="color:gray;" scope="row">_</th> '
                        + bottom_header_string
                    )

                bottom_table_headers.append(bottom_header_string)
                bottom_column_span = 0

            bottom_column_span += 1

            table_cells.append(table_cell)
            previous_month = current_month

        table_header_row = f'<th scope="row">{WEEKDAYS_NAMES[weekday]}</th>'
        if weekday in (5, 6):
            table_header_row = (
                f'<th style="color:gray;" scope="row">{WEEKDAYS_NAMES[weekday]}</th>'
            )

        table_rows.append(make_row(table_header_row + "".join(table_cells)))

    bottom_header_string = f'<td colspan="{
        bottom_column_span
    }"><span class="bott_cal_th">{strftime(date_item, "%b")}</span></td>'

    bottom_table_headers.append(bottom_header_string)

    first_month_separator = '<th scope="row"></th>'
    if first_day_of_year.weekday() == 6:
        first_month_separator = ""

    table_rows.append(make_row(first_month_separator + "".join(bottom_table_headers)))
    html_head = f'<h3 class="year_cal">{current_year}</h3>'
    html_table = f"""{html_head}
    <table summary='Heat calendar'
        class="cal_heat" border="0" cellpadding="0" cellspacing="0">
        {chr(10).join(table_rows)}

        </table>

    """
    return html_table


def get_colorkey(colors, divisions, values=[], labels=[]):
    assert len(colors) > divisions
    step = int(len(colors) / divisions)
    assert sum(values)
    max_val = np.nanmax(values)
    min_val = np.nanmin(values)
    max_label = labels[values.index(max_val)]
    min_label = labels[values.index(min_val)]
    max_label = max_label.split(";")[0]
    min_label = min_label.split(";")[0]
    val_range = get_distance(min_val, max_val)
    ticks = 9
    tick_step = val_range / float(ticks)
    current = max_val
    height, width, float_style = 2, 20, "None"
    css = f"""
    <style type="text/css">
    div.color_key {{
        font-size:1px;height:{height}px;width:{width}px;
        margin:0px 0px 0px 0px;padding: 0px 0px 0px 0px;
        display:block;float:{float_style};
    }}
    div.colorkey_tick {{
      font-weight:700;
      position:absolute;
      font-size:12px;
    }}
    </style>
    """
    tick_html = (
        f' <div class="colorkey_tick" style="top:-0.5em;right:0;">{max_label}</div>'
    )
    mid_val = val_range / 2.0
    mid_label = 0
    for v, label in sorted(zip(values, labels), reverse=True):
        if v < mid_val:
            mid_label = labels[values.index(v)]
            break
    tick_html += f"""<div class="colorkey_tick"
            style="top:49%;right:0;"> {mid_label}</div>"""
    for i in range(ticks - 1):
        current -= tick_step
        get_distance(current, max_val) / float(val_range)
    tick_html += f"""<div class="colorkey_tick"
            style="bottom:-0.5em;right:0;">
            {min_label}</div>"""
    data = {"max": max_val, "min": min_val, "rng": val_range}
    json_str = json.dumps(data, separators=(",", ":"))
    script = f'\n<script type="text/javascript"> var COLOR_KEY={json_str};</script>'
    divs = ""
    for i, color in enumerate(reversed(colors)):
        if i % step == 0:
            div = f'<div id="legend_wrapper" class="color_key" style="background:{color};">.</div>'
            divs += div
    html = f"""{css}{script}
        <div style="text-align:left;width:75px;position:relative;">
        <div id="color_key_wrapper"> {divs} </div>
         {tick_html}
         </div>
        """
    return html


def get_colors_data(values, dates, palette, to_display):
    def reject_outliers(data, m=4):
        return data[abs(data - np.mean(data)) < m * np.std(data)]

    stats_data = np.array(values)
    stats_data = stats_data[np.logical_not(np.isnan(stats_data))]
    stats_data = reject_outliers(stats_data, m=4)

    max_ret = np.nanmax(stats_data)
    min_ret = np.nanmin(stats_data)

    overall_rng = get_distance(min_ret, max_ret)

    palette_len = len(palette)
    colors_dict = {}
    for i, elem in enumerate(values):
        day = strftime(dates[i], "%Y-%m-%d")

        num_str = to_display[i]

        final_str = "%s;%s" % (day, num_str)
        if math.isnan(elem):
            colors_dict[day] = {"color": "white", "info": final_str}
        else:
            distance_min = get_distance(min_ret, elem) / overall_rng
            if elem < min_ret:
                distance_min = 0.0
            colors_position = int(distance_min * palette_len)
            if colors_position >= palette_len:
                colors_position = palette_len - 1

            colors_dict[day] = {"color": palette[colors_position], "info": final_str}
    # stop5
    return colors_dict


def table_html(dates, values, labels, colors=assets.RdYlGn):
    """accepts tuple (datetime object, value)"""
    assert dates[0].year

    max_value = np.nanmax(values)
    min_value = np.nanmin(values)

    # print(max_value, min_value)
    # stop
    year_dict = {}
    special_dates = {}

    for i, date in enumerate(dates):
        year_dict[date.year] = 1

        if values[i] == max_value:
            special_dates[date] = "max_value"
        elif values[i] == min_value:
            special_dates[date] = "min_value"

    special_dates[dates[-1]] = "last_value"

    colorkey = get_colorkey(colors, 51, values=values, labels=labels)

    COL_OBJ = get_colors_data(values, dates, colors, to_display=labels)

    table_list = []
    for year in sorted(list(year_dict.keys()), reverse=True):
        table = year_table(year, color_object=COL_OBJ)
        table_list.append(table)

    final_html = """
        <table style="text-align: center;width:auto;" border="0"
            cellpadding="0" cellspacing="0">
            <tr>
              <td id="heat_tables">%s</td>
              <td id="color_wrap" style="vertical-align:top;padding:23px 0px 0px 10px;">%s</td>
            </tr>
        </table>""" % ("\n".join(table_list), colorkey)
    return minify(final_html)


def create_page(html, title, output="output.html", startfile=True):
    assert "<table" in html
    from jinja2 import Environment, FileSystemLoader

    env = Environment(
        loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__)))
    )
    template = env.get_template(TEMPLATE)
    result = template.render({"title": title, "chart_data": html})
    with open(output, "w") as f:
        f.write(result)
    open_file(output)


def test_heatmap():
    from html import escape

    import pandas as pd
    import requests

    def get_prices():
        datetime.datetime.today().strftime("%Y-%m-%d")
        url = "https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23ebf3fb&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1320&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=SP500&scale=left&cosd=2020-06-12&coed=2025-06-12&line_color=%230073e6&link_values=false&line_style=solid&mark_type=none&mw=3&lw=3&ost=-99999&oet=99999&mma=0&fml=a&fq=Daily%2C%20Close&fam=avg&fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date={today}&revision_date={today}&nd=2015-06-15"

        response = requests.get(url, headers={"User-agent": "Mozilla/5.0"}).text
        def parse_date(date_str): return datetime.datetime.strptime(date_str, "%Y-%m-%d")
        data = []
        for row in response.split("\n")[1:]:
            values = row.split(",")
            if len(values) == 2:
                date_str, price_str = values
                try:
                    data.append([parse_date(date_str), float(price_str)])
                except ValueError:
                    pass
        assert data
        return data

    prices = get_prices()
    df = pd.DataFrame(prices, columns=["date", "price"])
    df["p_chng"] = df["price"].pct_change() * 100
    df.set_index("date", inplace=True)
    all_days = pd.date_range(df.index.min(), df.index.max(), freq="D")
    full_df = df.reindex(all_days)
    selected = full_df["2021-01-01":"2025-12-31"]
    # print(selected)
    dates = [pd.to_datetime(date) for date in selected.index.values]
    values = selected.p_chng.values.tolist()
    labels = [
        "%.2f%%" % val if not math.isnan(val) else "n/d"
        for val in selected.p_chng.values
    ]

    # Mark some important events
    labels[dates.index(datetime.datetime(2025, 4, 3))] += "; <i>Tariffs announced!</i>"
    labels[dates.index(datetime.datetime(2025, 4, 9))] += escape(
        ';tweet: <i class="emph">"THIS IS A GREAT TIME TO BUY!!! DJT"</i>'
    )

    html = table_html(dates, values, labels)
    create_page(
        html, title=f"SP500 daily calendar heat", output="SP500.html", startfile=True
    )


if __name__ == "__main__":
    test_heatmap()
