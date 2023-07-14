import json
from datetime import datetime, timedelta
from pathlib import Path

import feedparser
import requests

# 初始化配置文件
feedTitle = '每日技术资讯'
SeedTime = '11:00'
today = datetime.now().strftime("%Y-%m-%d")

# 获取当前日期和星期几
current_date = datetime.now()
date_str = current_date.strftime('%Y-%m-%d')
weekday_str = current_date.strftime('%A')

# 计算昨天的日期
yesterday = datetime.now() - timedelta(days=1)
yesterday_str = yesterday.strftime('%Y-%m-%d')

# 将英文星期几名称映射到中文星期几名称
weekday_mapping = {
    'Monday': '周一',
    'Tuesday': '周二',
    'Wednesday': '周三',
    'Thursday': '周四',
    'Friday': '周五',
    'Saturday': '周六',
    'Sunday': '周日'
}


def init_config():
    global root_path
    root_path = Path(__file__).absolute().parent
    config_path = root_path.joinpath('config.json')
    with open(config_path) as f:
        conf = json.load(f)
    return conf


def init_rss(conf):
    rss_list = []
    enabled = [{k: v} for k, v in conf.items() if v['enabled']]
    for rss in enabled:
        print(rss)
        (key, value), = rss.items()
        rss_list.append(value["RSS_FEED_URL"])
    return rss_list


def parse_rss(feeds):
    chinese_weekday_str = weekday_mapping[weekday_str]
    # 初始化消息内容列表
    Local_list = []
    feishuType_list = [
        [
            {
                "tag": "text",
                "text": f"▶  {feedTitle}({date_str}-{chinese_weekday_str}) ◀\n\n"
            }
        ]
    ]
    counter = 0
    for feedURL in feeds:
        # 解析 RSS 源
        feed = feedparser.parse(feedURL)
        # print(feed)
        # 遍历 RSS 源中的每篇文章
        if 'title' in feed.feed.keys():
            rssTitle = feed.feed.title
        else:
            rssTitle = ''
            print(feedURL, "没有找到'title'属性，请检查RSS源")
        counter += 1
        print(counter, "/", len(feeds), "正在解析：", rssTitle)
        feishuType_list.append([
            {
                "tag": "text",
                "text": f"{rssTitle}\n"
            }])
        content = {}

        # 初始化一个变量来记录昨天是否有更新
        has_updates = False

        for entry in feed.entries:
            pub_date = entry.get('published_parsed', None)
            # print(pub_date)
            if pub_date:
                pub_date_str = datetime(*pub_date[:6]).strftime('%Y-%m-%d')
                # 将文章信息添加到消息内容列表
                # 检查文章发布日期是否为昨天
                # print(pub_date_str, yesterday_str)
                if pub_date_str == yesterday_str:
                    # 提取文章标题、摘要和链接
                    title = entry.title
                    link = entry.link
                    content[title] = link
                    feishuType_list.append([
                        {
                            "tag": "text",
                            "text": f"【{title}】{pub_date_str} "
                        },
                        {
                            "tag": "a",
                            "text": "点击查看",
                            "href": link
                        }
                    ])
                    # 标记为有更新
                    has_updates = True
                # else:
                #   print("昨天没有更新")

        # 如果昨天没有更新，添加一个默认字段
        if not has_updates:
            feishuType_list.pop()
        else:
            feishuType_list.append([
                {
                    "tag": "text",
                    "text": f"\n"
                }])
            Local_list.append({rssTitle: content})
    return feishuType_list, Local_list


def update_today(data: list = []):
    """更新today"""
    root_path = Path(__file__).absolute().parent
    today_path = root_path.joinpath('today.md')
    archive_path = root_path.joinpath(f'archive/{today.split("-")[0]}/{today}.md')

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with open(today_path, 'w+') as f1, open(archive_path, 'w+') as f2:
        content = f'# 每日技术资讯（{today}）\n\n'
        for item in data:
            (feed, value), = item.items()
            content += f'- {feed}\n'
            for title, url in value.items():
                content += f'  - [{title}]({url})\n'
        f1.write(content)
        f2.write(content)


def bot(content):
    # 构建飞书机器人的消息格式
    payload = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh-CN": {
                    "content": content
                }
            }
        }
    }
    WEBHOOK_URL = conf["feishuBot"]["WEBHOOK_URL"]
    # 发送消息给飞书机器人
    response = requests.post(WEBHOOK_URL, json=payload)
    return response


def checkResp(response):
    # 检查发送结果
    if response.status_code == 200:
        res = "成功发送富文本消息"
    else:
        res = "成功发送富文本失败"
    print(res)


if __name__ == '__main__':
    conf = init_config()
    feeds = init_rss(conf['rss'])
    feishuType_list, Local_list = parse_rss(feeds)
    update_today(Local_list)
    response = bot(feishuType_list)
    checkResp(response)
