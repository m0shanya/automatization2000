#!/usr/bin/python3

import sys
import datetime
import socket
import time


def read_tcp(host, port, date):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(5)

        client.connect((host, port))

        time.sleep(0.25)

    except ConnectionError:
        print(f'{datetime.datetime.now().time().strftime("%H:%M:%S.%f")}: Error connection')
        client = None

    except TimeoutError:
        print(f'{datetime.datetime.now().time().strftime("%H:%M:%S.%f")}: Timeout error')
        client = None

    if client is None:
        print(f'{datetime.datetime.now().time().strftime("%H:%M:%S.%f")}: Could not open socket')
        sys.exit(1)

    else:
        with client:
            print(f'{datetime.datetime.now().time().strftime("%H:%M:%S.%f")}: Connection to {host}:{port}')

            client.send(bytes(date))
            print(f'{datetime.datetime.now().time().strftime("%H:%M:%S.%f")}:{date}')
            try:
                time.sleep(0.25)
                response = client.recv(1024)
                print(f'{datetime.datetime.now().time().strftime("%H:%M:%S.%f")}:{response}')
                print(f'{datetime.datetime.now().time().strftime("%H:%M:%S.%f")}:{len(response)}')
            except TimeoutError:
                print(f'{datetime.datetime.now().time().strftime("%H:%M:%S.%f")}: No answer from device')

    print(client)


if __name__ == '__main__':
    ip_address = sys.argv[1]  # str
    ip_port = int(sys.argv[2])  # int
    message = []
    for index_sys_arg in sys.argv[3::]:
        message.append(int(index_sys_arg, 16))

    start_time = datetime.datetime.now()
    read_tcp(ip_address, ip_port, message)
    print(f'Время выполнения программы составило: {datetime.datetime.now() - start_time} сек.')
