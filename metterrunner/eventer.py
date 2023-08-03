import asyncio
import subprocess
import sys

from multiprocessing import Process
from connection import r

subscriber = r.pubsub()
subscriber.subscribe('event')
loop = asyncio.get_event_loop()


async def read():
    tmp = []
    try:
        for key in r.scan_iter("*.commands"):

            value = r.lrange(key, 0, -1)
            for item in value:
                item = eval(str(item))
                tmp = [item['channel'], item['run']]
                r.lpush(f'{str(item["channel"])}.todo', str(tmp))

    except Exception as error:
        print(error)


def start_command(channel):
    try:
        for key in r.scan_iter(channel):
            for message in r.lrange(key, 0, -1):
                message = eval(str(message))
                command = f"{message[1]} {message[0]}"

                print(f"Run command {command}...")

                ssh = subprocess.Popen(["ssh", "eugen@192.168.1.33", command],
                                       shell=False,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       encoding="utf-8")
                result = ssh.stdout.readlines()

                if result == []:
                    error = ssh.stderr.readlines()
                    print(sys.stderr, "ERROR: %s" % error)
                else:
                    tmp_result = str(result[1]) + str(result[2])
                    print(tmp_result)
                r.lpop(key)

    except Exception as e:
        print(e)


async def processes():
    procs = []
    for key in r.scan_iter("*.todo"):

        proc = Process(target=start_command, args=(key, ))
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()

    print("Process was ended...\n______________")


if __name__ == "__main__":
    tasks = []

    while subscriber.listen():

        for key in r.scan_iter("*.commands"):
            print("______________\nProcess for write is starting...")
            # if message.get('data') != 1:

            tasks = [loop.create_task(read()), loop.create_task(processes())]
            worker = asyncio.wait(tasks)
            loop.run_until_complete(worker)
