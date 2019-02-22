# Heapq async

This is a reimplementation of the stdlib heapq.merge function, with a
few minor tweaks to allow it to work with async generators.

I basically copy-pasted the implementation directly from [cpython](https://github.com/python/cpython/blob/master/Lib/heapq.py).

The only important changes are:
  - `__next__` calls replaced with `__anext__`
  - catching `StopIteration` should also catch `StopAsyncIteration`
  - `for` loops on the fast case when only a single iterator remains reaplced with `async for` loops.
