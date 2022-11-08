import asyncio
from concurrent.futures import ProcessPoolExecutor
from functools import partial

executor = ProcessPoolExecutor()

async def execute_in_another_process(fn, *args, **kwargs):
    loop = asyncio.get_running_loop()
    pfunc = partial(fn, *args, **kwargs)
    return await loop.run_in_executor(executor, pfunc)