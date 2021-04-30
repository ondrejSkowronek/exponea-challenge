import asyncio
from asyncio import ALL_COMPLETED, FIRST_COMPLETED, CancelledError

from aiohttp import ClientResponseError
from django.shortcuts import render
from django.views.generic import DetailView
from rest_framework.response import Response
from rest_framework.views import APIView
import aiohttp

TEST_SERVER = "https://exponea-engineering-assignment.appspot.com/api/work"


async def get_response(session, timeout):
    async with session.get(TEST_SERVER) as resp:
        try:
            resp.raise_for_status()
        except ClientResponseError:
            # If we want only first task, we need to put to sleep all unsuccessful one,
            # so we get as first only successful one
            # DRAWBACK of this solution is that if all requests fails,
            # wait routine will be delayed until the end of timeout
            if timeout:
                await asyncio.sleep(timeout)
            return None

        return await resp.json()


async def fetch_all_responses(timeout, get_only_first):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for number in range(3):
            tasks.append(asyncio.create_task(get_response(session, timeout=timeout if get_only_first else None)))
        return await asyncio.wait(
            tasks, timeout=timeout, return_when=FIRST_COMPLETED if get_only_first else ALL_COMPLETED
        )


class BaseView(APIView):

    get_only_first = False

    class ValidationError(Exception):
        pass

    def get(self, request, format=None):
        try:
            timeout = self._get_timeout(request)
        except self.ValidationError as e:
            return Response({"error": str(e)}, status=400)

        return self._handle_responses(self._get_responses(timeout))

    def _get_integer_time_value(self, request):
        timeout = request.GET.get("timeout")
        if not timeout:
            raise self.ValidationError("Timeout parameter is missing")

        try:
            return int(timeout)
        except ValueError:
            raise self.ValidationError("Timeout parameter is not integer")

    def _get_timeout(self, request):
        timeout = self._get_integer_time_value(request)
        if timeout <= 0:
            raise self.ValidationError("Timeout integer must be greater than zero")
        return timeout / 1000

    def _get_done_responses(self, done_tasks):
        return [done.result() for done in done_tasks]

    def _build_successful_response(self, responses):
        return Response(responses)

    def _handle_responses(self, responses):
        if responses:
            return self._build_successful_response(responses)
        else:
            return Response({"error": "All requests were unsuccessful"}, status=400)

    def _get_responses(self, timeout):

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop = asyncio.get_event_loop()

        done_tasks, pending_tasks = loop.run_until_complete(fetch_all_responses(timeout, self.get_only_first))
        for pending_task in pending_tasks:
            pending_task.cancel()

        return [response for response in self._get_done_responses(done_tasks) if response is not None]


class AllView(BaseView):
    pass


class WithinTimeoutView(BaseView):
    def _handle_responses(self, responses):
        return self._build_successful_response(responses)


class FirstView(BaseView):

    get_only_first = True

    def _get_done_responses(self, done_tasks):
        if done_tasks:
            return [done_tasks.pop().result()]
        else:
            return []
