import asyncio

from memory_profiler import profile, memory_usage, CodeMap
from threading import Thread
from threading import settrace as threading_settrace
from sys import settrace
from asyncio import iscoroutinefunction, coroutine, wait
import psutil
import os
import time
import inspect
import sys
import numpy as np
from functools import wraps
from memory_profiler import choose_backend, choose_backend, partial, LineProfiler, show_results, tracemalloc, \
    has_tracemalloc
from concurrent.futures import ThreadPoolExecutor

_TWO_20 = float(2 ** 20)


def get_full_name(frame):
    code = frame.f_code

    # Stores all the parts of a human readable name of the current call
    full_name_list = []

    # Work out the module name
    module = inspect.getmodule(code)
    # print(module)
    # print(module.__name__)
    # print(module.__file__)
    if module:
        module_name = module.__name__
        module_path = module.__file__ if hasattr(module, '__file__') else ''

        if module_name == '__main__':
            module_name = ''
    else:
        module_name = ''
        module_path = ''

    if module_name:
        full_name_list.append(module_name)

    # Work out the class name
    try:
        class_name = frame.f_locals['self'].__class__.__name__
        full_name_list.append(class_name)
    except (KeyError, AttributeError):
        class_name = ''

    # Work out the current function or method
    func_name = code.co_name
    if func_name == '?':
        func_name = '__main__'
    full_name_list.append(func_name)

    # Create a readable representation of the current call
    full_name = '.'.join(full_name_list)
    return full_name, module_path


class ProfileMem:
    def __init__(self, **kw):
        include_children = kw.get('include_children', False)
        backend = kw.get('backend', 'psutil')
        self.code_map = CodeMap(
            include_children=include_children, backend=backend)
        self.enable_count = 0
        self.max_mem = kw.get('max_mem', None)
        self.prevlines = []
        self.backend = 'psutil'
        # self.backend = choose_backend(kw.get('backend', None))
        self.prev_lineno = None

    def _get_memory(self, pid, backend, timestamps=False):
        # .. low function to get memory consumption ..
        if pid == -1:
            pid = os.getpid()
        # int(memory_usage(-1, 0)[0] * 1000000)

        def ps_util_tool():
            # .. cross-platform but but requires psutil ..
            process = psutil.Process(pid)
            try:
                # avoid using get_memory_info since it does not exists
                # in psutil > 2.0 and accessing it will cause exception.
                meminfo_attr = 'memory_info' if hasattr(process, 'memory_info') \
                    else 'get_memory_info'
                mem = getattr(process, meminfo_attr)()[0] / _TWO_20
                if timestamps:
                    return mem, time.time()
                else:
                    return mem
            except psutil.AccessDenied:
                pass
                # continue and try to get this from ps
        tool = {'psutil': ps_util_tool, }
        return tool[backend]()

    def trace_memory_usage(self, frame, event, arg):
        """Callback for sys.settrace"""
        # if frame.f_code in self.code_map:
        if frame.f_code is not None:
            # if event == 'call':
            #     self.add_function(frame.f_code)
            #     # "call" event just saves the lineno but not the memory
            #     self.prevlines.append(frame.f_lineno)
            if event == 'line':
                show_results(self)
                template = '{0:>6} {1:>12} {2:>12}  {3:>10}'
                mem, t = self._get_memory(-1, 'psutil', timestamps=True)
                full_name, path = get_full_name(frame)
                tmp = template.format(frame.f_lineno, mem, path, full_name)
                print(tmp)
                # trace needs current line and previous line
                # self.code_map.trace(frame.f_code, self.prevlines[-1], self.prev_lineno)
                # # saving previous line
                # self.prev_lineno = self.prevlines[-1]
                # self.prevlines[-1] = frame.f_lineno

            # elif event == 'return':
            #     lineno = self.prevlines.pop()
            #     self.code_map.trace(frame.f_code, lineno, self.prev_lineno)
            #     self.prev_lineno = lineno


        # if self._original_trace_function is not None:
        #     self._original_trace_function(frame, event, arg)

        return self.trace_memory_usage

    def __enter__(self):
        self.enable()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disable()

    async def __aenter__(self):
        self.enable()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.disable()

    def enable(self):
        self._original_trace_function = sys.gettrace()
        if self.max_mem is not None:
            pass
            # sys.settrace(self.trace_max_mem)
            # threading_settrace(self.trace_max_mem)
        else:
            sys.settrace(self.trace_memory_usage)
            threading_settrace(self.trace_memory_usage)

    def disable(self):
        sys.settrace(self._original_trace_function)
        threading_settrace(self._original_trace_function)


def mem_profiler(func):
    if iscoroutinefunction(func):
        @wraps(func)
        async def f(*args, **kwargs):
            async with ProfileMem():
                await func(*args, **kwargs)
    else:
        @wraps(func)
        def f(*args, **kwds):
            with ProfileMem():
                return func(*args, **kwds)
    return f

# @mem_profiler
# @profile
async def run():
    await create_array()


# @profile
@mem_profiler
async def create_array():
    a = [1] * 10000
    b = [1] * 10
    d = [1] * 100
    fgg = np.ones(500)
    c = a
    k = b
    f = b
    del a
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=2)
    await loop.run_in_executor(executor, create_another_array)
    return


def create_another_array():
    a = [1] * 1000
    b = a
    return

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

