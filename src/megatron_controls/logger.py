import os
import asyncio
from datetime import datetime
from bluesky.utils import make_decorator

def ts_periodic_logging_wrapper(plan, signals, log_file_path, period=1):

    stop = asyncio.Event()

    async def logging_coro():
        while not stop.is_set():
            is_new_file = False
            if not os.path.isfile(log_file_path):
                dir, _ = os.path.split(log_file_path)
                os.makedirs(dir, exist_ok=True)
                is_new_file = True

            timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

            with open(log_file_path, "at") as f:
                if is_new_file:
                    s = ",".join([f'"{_}"' for _ in signals.keys()])
                    f.write(f"Timestamp,{s}\n")
                s = ",".join([f"{_.value}" for _ in signals.values()])
                f.write(f"{timestamp},{s}\n")

            await asyncio.sleep(period)

    class StartStopLogging(object):

        def __enter__(self):
            print("Starting periodic logging")
            asyncio.ensure_future(logging_coro())

        def __exit__(self, *args):
            print("Stopping periodic logging")
            stop.set()

    def _inner():
        with StartStopLogging():
            yield from plan

    return (yield from _inner())


ts_periodic_logging_decorator = make_decorator(ts_periodic_logging_wrapper)
