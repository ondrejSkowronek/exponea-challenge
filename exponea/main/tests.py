from django.test import SimpleTestCase
from django.urls import reverse
from aioresponses import aioresponses
import json
from urllib.parse import urlencode, urlparse, parse_qs


EXPONEA_URL = "https://exponea-engineering-assignment.appspot.com/api/work"


def build_url(base_url, get_params=None):
    """Builds URL with GET parameters"""
    if urlparse(base_url).query:
        get_params.update(parse_qs(urlparse(base_url).query))
        base_url = base_url.split("?")[0]
    return "?".join([base_url, urlencode(get_params, doseq=True)]) if get_params else base_url


class TaskTestCase(SimpleTestCase):

    def test_missing_timeout(self):
        response = self.client.get(reverse("all"))
        self.assertEqual(response.status_code, 400)

    def test_first(self):
        with aioresponses() as m:
            for i in range(3):
                m.get(EXPONEA_URL, status=200, payload={"time": 300})

            response = self.client.get(build_url(reverse("first"), {"timeout": 300}))
            response_json = json.loads(response.content)
            self.assertEqual(response_json, [{"time": 300}])
            self.assertEqual(response.status_code, 200)

    def test_all(self):
        with aioresponses() as m:
            m.get(EXPONEA_URL, status=200, payload={"time": 500})
            m.get(EXPONEA_URL, status=200, payload={"time": 400})
            m.get(EXPONEA_URL, status=200, payload={"time": 300})

            response = self.client.get(build_url(reverse("all"), {"timeout": 300}))
            response_json = json.loads(response.content)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                sorted(response_json, key=lambda item: item["time"]), [{"time": 300}, {"time": 400}, {"time": 500}]
            )

    def test_invalid_task(self):
        with aioresponses() as m:
            m.get(EXPONEA_URL, status=200, payload={"time": 500})
            m.get(EXPONEA_URL, status=400, payload={"time": 400})
            m.get(EXPONEA_URL, status=200, payload={"time": 300})

            response = self.client.get(build_url(reverse("all"), {"timeout": 300}))
            response_json = json.loads(response.content)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(sorted(response_json, key=lambda item: item["time"]), [{"time": 300}, {"time": 500}])

    def test_all_invalid_tasks(self):
        with aioresponses() as m:
            m.get(EXPONEA_URL, status=400, payload={"time": 500})
            m.get(EXPONEA_URL, status=400, payload={"time": 400})
            m.get(EXPONEA_URL, status=400, payload={"time": 300})

            response = self.client.get(build_url(reverse("all"), {"timeout": 300}))
            response_json = json.loads(response.content)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response_json, {"error": "All requests were unsuccessful"})

    def test_within_timeout_tasks_failed(self):
        with aioresponses() as m:
            m.get(EXPONEA_URL, status=400, payload={"time": 500})
            m.get(EXPONEA_URL, status=400, payload={"time": 400})
            m.get(EXPONEA_URL, status=400, payload={"time": 300})

            response = self.client.get(build_url(reverse("within-timeout"), {"timeout": 300}))
            response_json = json.loads(response.content)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_json, [])

    def test_within_timeout(self):
        with aioresponses() as m:
            m.get(EXPONEA_URL, status=200, payload={"time": 500})
            m.get(EXPONEA_URL, status=200, payload={"time": 400})
            m.get(EXPONEA_URL, status=200, payload={"time": 300})

            response = self.client.get(build_url(reverse("all"), {"timeout": 300}))
            response_json = json.loads(response.content)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                sorted(response_json, key=lambda item: item["time"]), [{"time": 300}, {"time": 400}, {"time": 500}]
            )
