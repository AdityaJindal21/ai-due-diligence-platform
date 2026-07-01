from __future__ import annotations

import os
from typing import Callable, Any

try:
    import redis
    from rq import Queue
    from rq.job import Job
except Exception:
    redis = None
    Queue = None
    Job = None

_rq_conn = None
_queue = None


def get_rq_connection():
    global _rq_conn, _queue
    if _rq_conn is None:
        redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")
        if redis is None:
            raise RuntimeError("redis package not available")
        _rq_conn = redis.from_url(redis_url)
        _queue = Queue("default", connection=_rq_conn)
    return _rq_conn, _queue


def enqueue(func: Callable[..., Any], *args, job_timeout: int = 3600) -> str:
    """Enqueue a function into RQ. Returns job id."""
    _, q = get_rq_connection()
    job = q.enqueue(func, *args, job_timeout=job_timeout)
    return job.get_id()


def get_job(job_id: str):
    conn, _ = get_rq_connection()
    return Job.fetch(job_id, connection=conn)
*** End Patch