# technical_library

可以获取昨日的大中厂技术资讯并通过飞书机器人推送，历史资讯保存于文件夹`archive`，通过修改`config.json`文件可自定义信息源和机器人的webhook。

### 安装步骤

```sh
  git clone https://github.com/alwaysday1/technical_library.git
  cd technical_library && ./install.sh
```

### 本地运行

```python3 ./bot.py```

1. 可编辑文件 `config.json`，启用所需的订阅源。
2. 订阅源可以通过网站添加，如 [RSSHub](https://docs.rsshub.app/)、[Top 50 Game Development RSS Feeds](https://blog.feedspot.com/game_development_rss_feeds/)
3. 机器人webhook可通过飞书开放平台文档[自定义机器人指南](https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN)配置。
