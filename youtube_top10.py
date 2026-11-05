#!/usr/bin/env python3
"""Fetch YouTube's regional mostPopular chart using YouTube Data API v3."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


def fetch_chart(region, api_key):
    query = urlencode({
        "part": "snippet,statistics", "chart": "mostPopular",
        "regionCode": region, "maxResults": 10, "key": api_key,
    })
    try:
        with urlopen("https://www.googleapis.com/youtube/v3/videos?" + query,
                     timeout=30) as response:
            data = json.load(response)
    except HTTPError as exc:
        # Do not log URLs or response bodies, which might expose credentials.
        raise RuntimeError(
            f"YouTube API 返回 HTTP {exc.code}；请检查 API 启用状态、密钥权限和配额。"
        ) from None
    except (URLError, TimeoutError, OSError):
        raise RuntimeError("无法连接 YouTube API；请检查网络白名单和代理。") from None
    except (ValueError, UnicodeError):
        raise RuntimeError("YouTube API 返回无效 JSON。") from None

    try:
        items = data["items"]
        if not isinstance(items, list) or not 1 <= len(items) <= 10:
            raise ValueError()
        videos = [{
            "rank": rank,
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "published_at": item["snippet"]["publishedAt"],
            "view_count": int(item["statistics"]["viewCount"])
                if "viewCount" in item.get("statistics", {}) else None,
            "url": "https://www.youtube.com/watch?v=" + item["id"],
        } for rank, item in enumerate(items, 1)]
    except (KeyError, TypeError, ValueError):
        raise RuntimeError("YouTube API 响应缺少有效的视频榜单。") from None
    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "region": region, "source": "YouTube Data API v3: mostPopular",
        "videos": videos,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", default="US", help="两位地区代码，默认 US")
    parser.add_argument("--output", type=Path, help="可选：同时保存 JSON 文件")
    args = parser.parse_args()
    region = args.region.upper()
    if not re.fullmatch(r"[A-Z]{2}", region):
        parser.error("--region 必须为两位地区代码，例如 US、JP 或 TW")
    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        print("缺少 YOUTUBE_API_KEY，请在环境设置中安全配置，不要提交到 Git。", file=sys.stderr)
        return 1
    try:
        result = fetch_chart(region, key)
        payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(payload, encoding="utf-8")
    except (RuntimeError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(payload, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
