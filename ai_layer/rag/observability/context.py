import threading


_context = threading.local()


def get_trace_id():
    return getattr(_context, "trace_id", None)


class TraceContext:
    def __init__(self, trace_id: str):
        _context.trace_id = trace_id

    def __enter__(self):
        return self

    def __exit__(self, *args):
        _context.trace_id = None
