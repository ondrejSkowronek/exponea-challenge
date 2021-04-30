import asyncio

from aiohttp import ClientResponseError
from django.shortcuts import render
from django.views.generic import DetailView
from rest_framework.response import Response
from rest_framework.views import APIView
import aiohttp

TEST_SERVER = 'https://exponea-engineering-assignment.appspot.com/api/work'


async def get_response(session):
    async with session.get(TEST_SERVER) as resp:
        try:
            resp.raise_for_status()
        except ClientResponseError:
            return None
        return await resp.json()


async def fetch_all_responses(timeout):
    timeout = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = []
        for number in range(3):
            tasks.append(asyncio.ensure_future(get_response(session)))
        return await asyncio.gather(*tasks)


class BaseView(APIView):

    class ValidationError(Exception):
        pass

    def _get_integer_time_value(self, request):
        timeout = request.GET.get('timeout')
        if not timeout:
            raise self.ValidationError('Timeout parameter is missing')

        try:
            return int(timeout)
        except ValueError:
            raise self.ValidationError('Timeout parameter is not integer')

    def _get_timeout(self, request):
        timeout = self._get_integer_time_value(request)
        if timeout <= 0:
            raise self.ValidationError('Timeout integer must be greater than zero')
        return timeout

    def _get_responses(self, timeout):

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop = asyncio.get_event_loop()

        return [response for response in loop.run_until_complete(fetch_all_responses(timeout)) if response is not None]


class AllView(BaseView):

    def get(self, request, format=None):
        try:
            timeout = self._get_timeout(request)
        except self.ValidationError as e:
            return Response({'error': str(e)}, status=400)

        responses = self._get_responses(timeout)
        return Response(responses)


class FirstView(BaseView):

    def get(self, request, format=None):
        timeout = (request.GET.get('timeout'))
        if not timeout:
            return Response({'error': 'Timeout is missing'}, status=400)
        responses = self._get_responses()

        return Response(responses)




