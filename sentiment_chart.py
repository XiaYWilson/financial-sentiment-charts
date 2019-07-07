# %%
from textblob import TextBlob
import pandas as pd
import pymysql
import numpy as np
import pyecharts.options as opts
from pyecharts.charts import Line


class MySQL:
    def __init__(self, table):
        # Connect to MySQL
        self._conn = pymysql.connect(
            host='localhost',  # mysql server address
            port=3306,  # port num
            user='root',  # username
            passwd='root',  # password
            db='finance',
            charset='utf8mb4',
        )
        self._cur = self._conn.cursor()
        self._table = table

    def __del__(self):
        self._conn.close()

    def search(self):
        sql = 'select time, sentiment from ' + self._table
        df = pd.read_sql(sql, con=self._conn)
        return df


def line_smooth(index, data, name) -> Line:
    # for i in data:
    #     if i.
    c = (
        Line()
        .add_xaxis(index)
        .add_yaxis("Sentiment value", data, is_smooth=True, is_connect_nones=True)
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(is_scale=True),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1))),
            datazoom_opts=[opts.DataZoomOpts(pos_bottom="-2%")],
            title_opts=opts.TitleOpts(title="Sentiment Analysis : " + name)
        )
    )
    return c


def gen_sentiment_chart(table):
    df = MySQL(table).search()
    df['time'] = pd.to_datetime(df['time'])
    df = df.set_index('time')
    df = df.resample('w').mean()
    df = df.fillna(0)
    data = np.around(np.array(df), decimals=2).tolist()
    index = df.index.tolist()
    sentiment_chart = line_smooth(index, data, table)
    return sentiment_chart, df.index[0].to_pydatetime(), df.index[-1].to_pydatetime()


if __name__ == "__main__":
    c, startdate, enddate = gen_sentiment_chart("mmm")
    c.render()
    print(c.dump_options())