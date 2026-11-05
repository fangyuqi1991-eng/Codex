# YouTube 当前热门前 10

用 Python 标准库调用 YouTube Data API v3 的 `videos.list(chart=mostPopular)`，
默认地区为美国（US），最多返回 10 条，保留 API 榜单顺序。
输出包含获取时间（UTC）、标题、频道、发布时间、累计播放量和视频链接。
播放量仅作信息展示，不用于重新排序；API 返回不足 10 条时保留实际数量。

这是 YouTube 官方 API 的地区热门榜单，不是全站实时热度排名，
也不是历史累计播放量前 10。榜单内容及类别由 YouTube 当前规则决定。

## 运行

需要 Python 3.10 或更高版本，无第三方依赖。

1. 在 Google Cloud 项目中启用 **YouTube Data API v3**，创建具有相应 API 权限的密钥。
2. 在云环境设置中安全配置 `YOUTUBE_API_KEY`，允许 HTTPS 访问 `www.googleapis.com`。
   在本地使用时，通过环境变量提供密钥。不要把密钥写入代码、命令行参数或提交记录。
3. 执行：

```sh
cd /workspace/Codex
python3 youtube_top10.py --region US --output output/top10.json
```

API 调用需要有效密钥和可用配额。网络拒绝、权限或配额错误会以非零状态退出，
不会生成模拟榜单。`output/` 不提交到 Git。

## 验证

```sh
python3 -m unittest discover -s tests -v
```

测试使用模拟响应验证解析和错误处理，不能替代真实 API 连接验证。
