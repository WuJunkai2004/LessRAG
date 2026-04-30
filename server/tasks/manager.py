import asyncio
import traceback
from typing import Callable, Coroutine

from server.utils.logger import log


class TaskManager:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.worker_task = None

    async def add_task(self, func: Callable[..., Coroutine], *args, **kwargs):
        """添加一个任务到队列"""
        await self.queue.put((func, args, kwargs))
        log("task").info(f"Task added: {func.__name__}")

    async def _worker(self):
        """后台消费者"""
        log("task").info("Task worker started.")
        while True:
            func, args, kwargs = await self.queue.get()
            try:
                log("task").info(f"Executing task: {func.__name__} with args: {args}")
                await func(*args, **kwargs)
                log("task").info(f"Task completed: {func.__name__}")
            except Exception as e:
                log("task").error(f"Task failed: {func.__name__}. Error: {e}")
                log("task").error(traceback.format_exc())
            finally:
                self.queue.task_done()

    def start_worker(self):
        """启动后台 Worker"""
        if self.worker_task is None:
            self.worker_task = asyncio.create_task(self._worker())

    async def stop_worker(self):
        """停止后台 Worker"""
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
            log("task").info("Task worker stopped.")


# 单例导出
task_manager = TaskManager()
