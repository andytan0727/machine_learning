"""
Created on Fri Oct 19 20:30:56 2018
@author: hzp0625
modified by: Andy Tan 27 Oct 2018
"""
import pandas as pd
from pyecharts import Pie, Line, Scatter
import os
import numpy as np
import jieba
import jieba.analyse
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# ,size=20指定本机的汉字字体位置
font = FontProperties(fname=r'c:\windows\fonts\simsun.ttc')

data = pd.read_csv('bilibili_working_cell.csv')

"""
描述性分析
"""

del data['ctime']
del data['liked']
# 评分

scores = data['score'].groupby(data['score']).count()
pie1 = Pie("Rating", title_pos='center', width=900)
pie1.add(
    "Rating",
    ['One Star', 'Two Stars', 'Three Stars', 'Four Stars', 'Five Stars'],
    scores.values,
    # radius=[40, 75],
    center=[50, 50],
    is_random=True,
    #    radius=[30, 75],
    is_legend_show=False,
    is_label_show=True,
)
pie1.render('rating.html')

data['dates'] = data.loc[:, 'date'].apply(lambda x: pd.Timestamp(x).date())
data['time'] = data.loc[:, 'date'].apply(
    lambda x: pd.Timestamp(x).time().hour
)


num_date = data['author'].groupby(data['dates']).count()

# 评论数时间分布
chart = Line("评论数时间分布")
# chart.use_theme('dark')
chart.add('评论数时间分布', num_date.index, num_date.values, is_fill=True, line_opacity=0.2,
          area_opacity=0.4, symbol=None)
chart.render('评论时间分布.html')

# 好评字数分布
datalikes = data.loc[data['likes'] > 5]
datalikes['num'] = datalikes['content'].apply(lambda x: len(x))
chart = Scatter("likes")
chart.use_theme('dark')
chart.add('likes', np.log(datalikes.likes), datalikes.num, is_visualmap=True,
          xaxis_name='log(评论字数)')
chart.render('好评字数分布.html')


# 评论每日内的时间分布
num_time = data.loc[:, 'author'].groupby(data['time']).count()

# 时间分布

chart = Line("评论日内时间分布")
chart.use_theme('dark')
chart.add("评论数", x_axis=num_time.index.values, y_axis=num_time.values,
          is_label_show=True,
          mark_point_symbol='diamond', mark_point_textcolor='#40ff27',
          line_width=2)
chart.render('评论日内时间分布.html')


# 时间分布
chart = Line("评论数时间分布")
chart.use_theme('dark')
chart.add('评论数时间分布', num_date.index, num_date.values, is_fill=True, line_opacity=0.2,
          area_opacity=0.4, symbol=None)
chart.render('评论时间分布.html')

# 评分时间分布
datascore = data.score.groupby(data['dates']).mean()
chart = Line("评分时间分布")
chart.use_theme('dark')
chart.add('评分', datascore.index,
          datascore.values,
          line_width=2)
chart.render('评分时间分布.html')


"""
评论分析
"""

texts = ';'.join(data['content'].tolist())
cut_text = " ".join(jieba.cut(texts))
# TF_IDF
keywords = jieba.analyse.extract_tags(
    cut_text, topK=500, withWeight=True, allowPOS=('a', 'e', 'n', 'nr', 'ns'))
text_cloud = dict(keywords)
pd.DataFrame(keywords).to_excel('TF_IDF关键词前500.xlsx')

# bg = plt.imread("血小板.jpg")
wc = WordCloud(  # FFFAE3
    background_color="white",  # 设置背景为白色，默认为黑色
    width=1200,
    height=720,
    # mask=bg,
    # random_state=2,
    max_font_size=500,
    font_path=r"c:\windows\fonts\msyh.ttc",
).generate_from_frequencies(text_cloud)

plt.imshow(wc)
plt.axis("off")
plt.show()
wc.to_file("词云.png")
