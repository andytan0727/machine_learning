import requests
import json
from fake_useragent import UserAgent
import pandas as pd
import time
import datetime
from threading import Thread

headers = {'User-Agent': UserAgent(verify_ssl=False).random}
url = "https://bangumi.bilibili.com/review/web_api/short/list?media_id=102392&folded=0&page_size=21&sort=0"

cols = ['author', 'score', 'disliked', 'likes', 'liked',
        'ctime', 'content']
data = pd.DataFrame(index=range(17535), columns=cols)


def get_requests(start, stop, url, stepsize=21):
    j = start
    # list_comments = json_comment['result']['list']
    list_comments = []

    while j < stop:
        if j == 0:
            response = requests.get(url, headers=headers).text
            list_comments.extend(json.loads(response)['result']['list'])
            j += stepsize
            continue

        url_ex = '{}&cursor={}'.format(
            url, list_comments[-1]['cursor'])
        response = requests.get(url_ex, headers=headers).text
        list_comments.extend(json.loads(response)['result']['list'])

        # time.sleep(0.5)
        j += stepsize
        print('finished fetching {} comments. Getting next...'.format(j))

    return list_comments


def get_comments(start, stop, list_comments):
    j = start

    while j <= stop:
        for comment in list_comments:
            data.loc[j, 'author'] = comment['author']['uname']
            data.loc[j, 'score'] = comment['user_rating']['score']
            data.loc[j, 'disliked'] = comment['disliked']
            data.loc[j, 'likes'] = comment['likes']
            data.loc[j, 'liked'] = comment['liked']
            data.loc[j, 'ctime'] = comment['ctime']
            data.loc[j, 'content'] = comment['content']
            j += 1


def getDate(x):
    x = time.gmtime(x)
    return pd.Timestamp(datetime.datetime(x[0], x[1], x[2], x[3], x[4], x[5]))


if __name__ == '__main__':
    list_comments = get_requests(0, 17535, url)
    # print(len(list_comments))

    data_threads = []
    thread_counter = 0 
    for i in range(0, len(list_comments), 21):
        data_thread = Thread(target=get_comments, args=(
            i, i + 20, list_comments[i:i + 21]))
        data_threads.append(data_thread)
        data_thread.start()
        thread_counter += 1
        print('Thread-{} started.'.format(thread_counter))

    for data_thread in data_threads:
        data_thread.join()

    data = data.fillna(0)
    data['date'] = data.ctime.apply(lambda x: getDate(x))
    data.to_csv('bilibili_working_cell.csv', index=False)
