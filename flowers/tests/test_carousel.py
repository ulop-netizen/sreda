"""DRY tests for carousel support: no network, ThreadsClient._post is stubbed."""
import unittest

from src.threads_client import ThreadsClient, ThreadsError


def make_client():
    c = ThreadsClient("U1", "tok", publish_delay=0)
    calls = []

    def fake_post(path, params):
        calls.append((path, dict(params)))
        return {"id": f"id{len(calls)}"}

    c._post = fake_post
    return c, calls


def test_carousel_flow():
    c, calls = make_client()
    pid = c.post("hi\n239 zł — розы\nВаршава", image_urls=["https://x/a.jpg", "https://x/b.jpg"])
    assert [p for p, _ in calls] == ["U1/threads", "U1/threads", "U1/threads", "U1/threads_publish"]
    assert calls[0][1] == {"media_type": "IMAGE", "image_url": "https://x/a.jpg", "is_carousel_item": "true"}
    assert calls[1][1]["image_url"] == "https://x/b.jpg"
    assert "text" not in calls[0][1]
    assert calls[2][1] == {"media_type": "CAROUSEL", "children": "id1,id2", "text": "hi\n239 zł — розы\nВаршава"}
    assert calls[3][1] == {"creation_id": "id3"}
    assert pid == "id4"


def test_single_image_unchanged():
    c, calls = make_client()
    c.post("t", image_url="https://x/a.jpg")
    assert calls[0][1] == {"media_type": "IMAGE", "image_url": "https://x/a.jpg", "text": "t"}
    assert len(calls) == 2


def test_one_item_list_is_single_image():
    c, calls = make_client()
    c.post("t", image_urls=["https://x/a.jpg"])
    assert calls[0][1]["media_type"] == "IMAGE" and len(calls) == 2


def test_carousel_limits():
    c, _ = make_client()
    for bad in (["https://x/a.jpg"], [f"https://x/{i}.jpg" for i in range(21)]):
        try:
            c.post_carousel("t", bad)
        except ThreadsError:
            continue
        raise AssertionError("expected ThreadsError")


class CarouselTest(unittest.TestCase):
    def test_all(self):
        test_carousel_flow(); test_single_image_unchanged()
        test_one_item_list_is_single_image(); test_carousel_limits()
