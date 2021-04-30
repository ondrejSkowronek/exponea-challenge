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
        response = self.client.get(reverse('all'))
        self.assertEqual(response.status_code, 400)

    def test_timeout(self):
        with aioresponses() as m:
            m.get(EXPONEA_URL, status=200, payload={'time': 500})
            m.get(EXPONEA_URL, status=200, payload={'time': 400})
            m.get(EXPONEA_URL, status=200, payload={'time': 300})

            response = self.client.get(build_url(reverse('all'), {'timeout': 300}))
            response_json = json.loads(response.content)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_json, [{'time': 500}, {'time': 400}, {'time': 300}])

    def test_invalid_task(self):
        with aioresponses() as m:
            m.get(EXPONEA_URL, status=200, payload={'time': 500})
            m.get(EXPONEA_URL, status=400, payload={'time': 400})
            m.get(EXPONEA_URL, status=200, payload={'time': 300})
            response = self.client.get(build_url(reverse('all'), {'timeout': 300}))
            response_json = json.loads(response.content)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_json, [{'time': 500}, {'time': 300}])
            print(response_json)
