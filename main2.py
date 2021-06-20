from concurrent.futures import ThreadPoolExecutor
import numpy as np
import asyncio
from time import sleep
from pympler.asizeof import asizeof
from memory_profiler import profile


executor = ThreadPoolExecutor(max_workers=2)
loop = asyncio.get_event_loop()


@profile
async def create_array1():
	# a = [1] * 10000
	# b = [1] * 10
	# # d = [1] * 100
	# fgg = np.ones(5000000)
	# print('create_array {}'.format(asizeof(fgg)))
	# await asyncio.sleep(1)
	# a = fgg
	# loop = asyncio.get_event_loop()
	# executor = ThreadPoolExecutor(max_workers=2)
	r = await loop.run_in_executor(executor, create_another_array1)
	# print(r)
	return

async def create_array2():
	# a = [1] * 10000
	# b = [1] * 10
	# d = [1] * 100
	# fgg = np.ones(30000000)
	# print('create_array2 {}'.format(asizeof(fgg)))
	# await asyncio.sleep(0.3)
	# a = fgg
	# loop = asyncio.get_event_loop()

	r = await loop.run_in_executor(executor, create_another_array2)
	return

# @profile
def create_another_array2():
	fgg1 = np.ones(20000000)
	sleep(2)
	print('create_another_array2-1')
	fgg2 = np.ones(20000000)
	sleep(1)
	print('create_another_array2-2 {}'.format(asizeof(fgg2)))
	return fgg1

# @profile
def create_another_array1():
	fgg1 = np.ones(20000000)
	sleep(1)
	print('create_another_array1-1 {}'.format(asizeof(fgg1)))
	fgg = np.ones(20000000)
	sleep(2)
	print('create_another_array1-2 {}'.format(asizeof(fgg1)))
	return fgg


# @profile
async def run():
	# вариант 1 - последовательное выполнение
	# r1 = await asyncio.create_task(create_array1(), name='task1')
	# r2 = await asyncio.create_task(create_array2(), name='task2')

	# # вариант 2 - конкурентное выполнение
	# r1 = asyncio.create_task(create_array1(), name='task1')
	# r2 = asyncio.create_task(create_array2(), name='task2')
	# r1 = await r1
	# r2 = await r2

	# # вариант 3 - последовательное
	# create_another_array1()
	# create_another_array2()

	# # вариант 4 - еще конкурентное
	r1 = asyncio.create_task(create_array1(), name='task1')
	r2 = asyncio.create_task(create_array2(), name='task2')
	r = await asyncio.gather(r1, r2)


if __name__ == '__main__':
	loop.run_until_complete(run())

	# # вариант 5 - еще конкурентное
	# loop.create_task(create_array1(), name='task1')
	# loop.create_task(create_array2(), name='task2')
	# loop.run_forever()
