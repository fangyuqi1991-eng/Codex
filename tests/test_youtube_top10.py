import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse

from youtube_top10 import fetch_chart


class ChartTests(unittest.TestCase):
    def test_preserves_chart_order_and_parameters(self):
        items = [{"id": video_id, "snippet": {
            "title": "测试 " + video_id, "channelTitle": "频道",
            "publishedAt": "2026-01-01T00:00:00Z",
        }, "statistics": {"viewCount": views}}
            for video_id, views in [("first", "10"), ("second", "100")]]
        with patch("youtube_top10.urlopen", return_value=io.BytesIO(
                json.dumps({"items": items}).encode())) as request:
            result = fetch_chart("US", "test-key")
        query = parse_qs(urlparse(request.call_args.args[0]).query)
        self.assertEqual(query["chart"], ["mostPopular"])
        self.assertEqual(query["regionCode"], ["US"])
        self.assertEqual(query["maxResults"], ["10"])
        self.assertEqual([v["view_count"] for v in result["videos"]], [10, 100])
        self.assertEqual(result["videos"][0]["rank"], 1)
        self.assertEqual(result["videos"][1]["url"],
                         "https://www.youtube.com/watch?v=second")

    def test_http_error_does_not_expose_key(self):
        with patch("youtube_top10.urlopen", side_effect=HTTPError(
                "https://example.com?key=secret", 403, "secret", {}, None)):
            with self.assertRaisesRegex(RuntimeError, "HTTP 403") as error:
                fetch_chart("US", "secret")
        self.assertNotIn("secret", str(error.exception))

    def test_empty_or_invalid_response_fails(self):
        for payload in ({"items": []}, {"items": [{}]}, {"error": {}}):
            with self.subTest(payload=payload):
                with patch("youtube_top10.urlopen", return_value=io.BytesIO(
                        json.dumps(payload).encode())):
                    with self.assertRaises(RuntimeError):
                        fetch_chart("US", "test-key")


if __name__ == "__main__":
    unittest.main()
