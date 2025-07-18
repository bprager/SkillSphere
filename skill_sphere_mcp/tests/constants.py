"""Test constants."""

from http import HTTPStatus

# HTTP Status Codes
HTTP_OK = HTTPStatus.OK
HTTP_BAD_REQUEST = HTTPStatus.BAD_REQUEST
HTTP_NOT_FOUND = HTTPStatus.NOT_FOUND
HTTP_UNPROCESSABLE_ENTITY = HTTPStatus.UNPROCESSABLE_ENTITY

# Test Constants
DEFAULT_TEST_LIMIT = 2
DEFAULT_TEST_TOP_K = 5
MAX_TEST_TOP_K = 100

class AsyncIterator:
    def __init__(self, items):
        self._items = items
        self._index = 0
    def __aiter__(self):
        self._index = 0
        return self
    async def __anext__(self):
        if self._index >= len(self._items):
            raise StopAsyncIteration
        item = self._items[self._index]
        self._index += 1
        return item
