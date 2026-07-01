from app.core.worker import get_rq_connection


def run_worker():
    # This file is intended to be used as an entrypoint in Docker: it imports get_rq_connection
    # to ensure the connection is initialized, and then relies on `rq worker` CLI to start.
    conn, q = get_rq_connection()
    print("RQ worker runner initialized. Use `rq worker` to start the worker connected to this Redis instance.")


if __name__ == "__main__":
    run_worker()
