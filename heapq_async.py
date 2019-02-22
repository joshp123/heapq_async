import logging
from heapq import heapify, heappop, heapreplace, merge as stdlib_merge

log = logging.getLogger(__name__)


async def merge(*iterables, key=None, reverse=False):
    """This is a reimplementation of the stdlib heapq.merge function, with a
    few minor tweaks to allow it to work with async generators.

    I basically copy-pasted the implementation directly from cpython:
    https://github.com/python/cpython/blob/master/Lib/heapq.py

    The only important changes are:
        - __next__ calls replaced with __anext__
        - catching StopIteration should also catch StopAsyncIteration
        - for loops on the fast case when only a single iterator remains
          reaplced with async for loops.
    """
    # Try naive implementation first I guess
    try:
        for line in stdlib_merge(*iterables, key, reverse):
            yield line
    except TypeError:
        log.debug(
            "Couldn't fall back to naive implementation. Using async version.",
            exc_info=True,
        )

    h = []
    h_append = h.append
    if reverse:
        raise NotImplementedError
    else:
        _heapify = heapify
        _heappop = heappop
        _heapreplace = heapreplace
        direction = 1

    if key is None:
        for order, it in enumerate(iterables):
            try:
                next = it.__anext__
                h_append([await next(), order * direction, next])
            except (StopIteration, StopAsyncIteration):
                pass
        _heapify(h)
        while len(h) > 1:
            try:
                while True:
                    value, order, next = s = h[0]
                    yield value
                    s[0] = next()  # raises StopIteration when exhausted
                    _heapreplace(h, s)  # restore heap condition
            except (StopIteration, StopAsyncIteration):
                _heappop(h)  # remove empty iterator
        if h:
            # fast case when only a single iterator remains
            value, order, next = h[0]
            yield value
            async for item in next.__self__:
                yield item
        return

    for order, it in enumerate(iterables):
        try:
            next = it.__anext__
            value = await next()
            h_append([key(value), order * direction, value, next])
        except (StopIteration, StopAsyncIteration):
            pass
    _heapify(h)
    while len(h) > 1:
        try:
            while True:
                key_value, order, value, next = s = h[0]
                yield value
                value = await next()
                s[0] = key(value)
                s[2] = value
                _heapreplace(h, s)
        except (StopIteration, StopAsyncIteration):
            _heappop(h)
    if h:
        key_value, order, value, next = h[0]
        yield value
        async for item in next.__self__:
            yield item
