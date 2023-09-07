import struct
import fdb
import os
import socket

from datetime import datetime
from copy import deepcopy
from crc16ccc import crc16_chk, reverse_CRC16
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
FB_HOST = os.environ.get("FB_HOST")
FB_DATABASE = os.environ.get("FB_DATABASE")
FB_USER = os.environ.get("FB_USER")
FB_PASSWORD = os.environ.get("FB_PASSWORD")
CHARSET = os.environ.get("CHARSET")

connection = {'host': FB_HOST,
              'database': FB_DATABASE,
              'user': FB_USER,
              'password': FB_PASSWORD,
              'charset': CHARSET
              }


def printer(message, typeof):
    res_str = ''
    for element in [hex(i) for i in message]:  # для печати посылки без лишних символов в консоль
        if len(element.split('x')[1]) < 2:
            res_str += '0'
        res_str += element.split('x')[1]
        res_str += ' '

    print(f"{typeof}: \n{res_str}")
    return res_str


def get_datetime() -> dict:
    time_now = datetime.now()
    data = dict(year=time_now.year - 2000,
                month=time_now.month,
                day=time_now.day,
                hour=time_now.hour,
                minute=time_now.minute,
                second=time_now.second)

    return data


def test_cmd(choose: int):
    if choose == 1:
        byte_cmd = [0x55, 0x81, 0x00, 0x0A, 0x00, 0x01, 0x00, 0x33]
    elif choose == 2:
        byte_cmd = [0x55, 0x81, 0x00, 0x12, 0x00, 0x40, 0x00, 0x11, 0x00, 0x04, 0x00, 0x02, 0x00, 0x04, 0x00, 0x01]
    elif choose == 3:
        byte_cmd = [0x55, 0x81, 0x00, 0x12, 0x00, 0x42, 0x00, 0x11, 0x00, 0x04, 0x00, 0x00, 0x00, 0x04, 0x00, 0x01]
    elif choose == 4:
        byte_cmd = [0x55, 0x81, 0x00, 0x12, 0x00, 0x52, 0x00, 0x11, 0x00, 0x04, 0x00, 0x03, 0x00, 0x01, 0x00, 0x01]
    elif choose == 5:
        byte_cmd = [0x55, 0x81, 0x00, 0x12, 0x00, 0x80, 0x00, 0x11, 0x00, 0x04, 0x00, 0x01, 0x00, 0x04, 0x00, 0x01]
    elif choose == 6:
        byte_cmd = [0x55, 0x81, 0x00, 0x12, 0x00, 0x81, 0x00, 0x11, 0x00, 0x04, 0x00, 0x03, 0x00, 0x04, 0x00, 0x01]
    elif choose == 7:
        byte_cmd = [0x55, 0x81, 0x00, 0x10, 0x00, 0x85, 0x00, 0x11, 0x00, 0x04, 0x00, 0x01, 0x00, 0x17]
    else:
        return
    byte_cmd += reverse_CRC16(crc16_chk(byte_cmd))  # составляю и добавляю ЦРЦ во всю посылку

    printer(byte_cmd, "Request")

    return byte_cmd


def choose_vmid(command, insertion):
    if command[6] != 0:
        vmid = ((int(hex(command[6]) + hex(command[7]).split('x')[1], 16) - 1) // 4) + insertion
    else:
        vmid = ((command[7] - 1) // 4) + insertion

    return vmid


def execute_query(query):
    with fdb.connect(**connection) as con:
        cur = con.cursor()

        cur.execute(query)

        result = []
        for data in cur.fetchall():
            result += struct.pack("!f", data[0])
        return result


def another_data(response, data, timer, cmd):
    response = response[0:2]

    if cmd[5] == 0x85:
        response = putting_allen_data(response, data, timer, cmd)
    else:
        if data == [] or None:
            response += [0x00] + [cmd[5]] + [0xff] * 4 * cmd[9] * (cmd[9] // 4) * cmd[13]
        else:
            response += [0x00] + [cmd[5]] + data

    checker = 0x00 if data != [] or None else 0x01
    response += [checker]
    response.extend([struct.pack("!i", timer["minute"])[-1],
                     struct.pack("!i", timer["hour"])[-1],
                     struct.pack("!i", timer["day"])[-1],
                     struct.pack("!i", timer["month"])[-1],
                     struct.pack("!i", timer["year"])[-1]])
    response.append(cmd[14])
    response.append(cmd[15])
    response.insert(2, 0)
    response.insert(3, int(hex(len(response) + 3), 16))
    return response


def putting_allen_data(response, data, timer, cmd):
    response += [0x00] + [cmd[5]]
    data_copy = deepcopy(data)
    for i in range(0, cmd[9] * (cmd[9] // 4) * cmd[11]):
        response.append(struct.pack("!i", timer["second"])[-1])
        response.append(struct.pack("!i", timer["minute"])[-1])
        response.append(struct.pack("!i", timer["hour"])[-1])
        response.append(struct.pack("!i", timer["day"])[-1])
        response.append(struct.pack("!i", timer["month"])[-1])
        response.append(struct.pack("!i", timer["year"])[-1])
        if data == [] or None:
            response += [0xff] * 4
        else:
            response += data_copy[0:4]
            data_copy = data_copy[4:len(data_copy)]

    return response


def get_incday_data(comma, insertion):
    vmid = choose_vmid(comma, insertion)

    date = None
    timer = get_datetime()
    year = timer["year"] + 2000
    month = timer["month"]
    day = timer["day"]

    for i in range(0, 10000):

        if comma[11] == i:
            if day < i:
                month = month - 1
                delta = i - day

                if month == 7 or month == 8:
                    day = 31 - delta
                elif month % 2 == 0:
                    day = 30 - delta
                elif month == 2:
                    day = 28 - delta
                else:
                    day = 31 - delta
            else:
                day = day - i

            if month > 10:
                date = f'{year}-{month}-{day} 00:00:00'
                break
            elif month > 10 and day < 10:
                date = f'{year}-{month}-0{day} 00:00:00'
                break
            elif month < 10 and day < 10:
                date = f'{year}-0{month}-0{day} 00:00:00'
                break
            else:
                date = f'{year}-0{month}-{day} 00:00:00'
                break

    query = f"""SELECT M_SFVALUE FROM L3ARCHDATA WHERE M_SWVMID={vmid} AND M_STIME='{date}' AND
    M_SWTID BETWEEN {comma[12]} and {comma[13] - 1} AND M_SWCMDID BETWEEN 5 AND 8 ORDER BY M_SWCMDID"""

    return execute_query(query)


def get_incmonth_data(comma, insertion):
    vmid = choose_vmid(comma, insertion)
    date = None
    timer = get_datetime()
    year = timer["year"] + 2000
    month = timer["month"]

    for i in range(0, 10000):

        if comma[11] == i:
            if month > 10:
                date = f'{year}-{month - i}-01 00:00:00'
                break
            date = f'{year}-0{month - i}-01 00:00:00'
            break

    query = f"""SELECT M_SFVALUE FROM L3ARCHDATA WHERE M_SWVMID={vmid} AND M_STIME='{date}' AND
    M_SWTID BETWEEN {comma[12]} and {comma[13] - 1} AND M_SWCMDID BETWEEN 9 AND 12 ORDER BY M_SWCMDID"""

    return execute_query(query)


def get_min30_data(comma, insertion):
    numbers = ""
    vmid = choose_vmid(comma, insertion)
    timer = get_datetime()
    year = timer["year"] + 2000
    month = timer["month"]
    day = timer["day"]
    if month > 10:
        date = f'{year}-{month}-{day} 00:00:00'
    elif month > 10 and day < 10:
        date = f'{year}-{month}-0{day} 00:00:00'
    elif month < 10 and day < 10:
        date = f'{year}-0{month}-0{day} 00:00:00'
    else:
        date = f'{year}-0{month}-{day} 00:00:00'

    if comma[13] == 1:
        numbers = f"V{comma[11]}"
    else:
        for i in range(comma[11], comma[11] + comma[13]):
            numbers += f"V{i}, "

        numbers = numbers[0:len(numbers) - 2]

    query = f"""SELECT {numbers} FROM L2HALF_HOURLY_ENERGY WHERE M_SWVMID={vmid} AND M_SDTDATE='{date}' AND
     M_SWCMDID BETWEEN 13 AND 16"""

    return execute_query(query)


def get_month_data(comma, insertion):
    vmid = choose_vmid(comma, insertion)
    date = None
    timer = get_datetime()
    year = timer["year"] + 2000
    month = timer["month"]
    day = timer["day"]

    for i in range(0, 10000):

        if comma[11] == i:
            if day < i:
                month = month - 1
            if month > 10:
                date = f'{year}-{month - i}-01 00:00:00'
                break
            date = f'{year}-0{month - i}-01 00:00:00'
            break

    query = f"""SELECT M_SFVALUE FROM L3ARCHDATA WHERE M_SWVMID={vmid} AND M_STIME='{date}' AND
    M_SWTID BETWEEN {comma[12]} and {comma[13] - 1} AND M_SWCMDID BETWEEN 21 AND 24 ORDER BY M_SWCMDID"""

    return execute_query(query)


def get_day_data(comma, insertion):
    vmid = choose_vmid(comma, insertion)
    date = None
    timer = get_datetime()
    year = timer["year"] + 2000
    month = timer["month"]
    day = timer["day"]

    for i in range(0, 10000):

        if comma[11] == i:
            if day < i:
                month = month - 1
                delta = i - day
                if month == 7 or month == 8:
                    day = 31 - delta
                elif month % 2 == 0:
                    day = 30 - delta
                elif month == 2:
                    day = 28 - delta
                else:
                    day = 31 - delta
            else:
                day = day - i

            if month > 10:
                date = f'{year}-{month}-{day} 00:00:00'
                break
            elif month > 10 and day < 10:
                date = f'{year}-{month}-0{day} 00:00:00'
                break
            elif month < 10 and day < 10:
                date = f'{year}-0{month}-0{day} 00:00:00'
                break
            else:
                date = f'{year}-0{month}-{day} 00:00:00'
                break

    query = f"""SELECT M_SFVALUE FROM L3ARCHDATA WHERE M_SWVMID={vmid} AND M_STIME='{date}' AND
    M_SWTID BETWEEN {comma[12]} and {comma[13] - 1} AND M_SWCMDID BETWEEN 17 AND 20 ORDER BY M_SWCMDID"""

    return execute_query(query)


def get_allen_data(comma, insertion):
    vmid = choose_vmid(comma, insertion)
    timer = get_datetime()
    year = timer["year"] + 2000
    month = timer["month"]
    day = timer["day"]
    hour = timer["hour"]
    minute = timer["minute"]
    second = timer["second"]

    # if month >= 10:
    #     date = f'{year}-{month}-{day} {hour}:{minute}:{second}'
    # elif month > 10 and day < 10:
    #     date = f'{year}-{month}-0{day} {hour}:{minute}:{second}'
    # elif month < 10 and day < 10:
    #     date = f'{year}-0{month}-0{day} {hour}:{minute}:{second}'
    # else:
    #     date = f'{year}-0{month}-{day} {hour}:{minute}:{second}'
    if comma[10] != 0:
        query = f"""SELECT M_SFVALUE, cast (M_STIME as date) FROM L3CURRENTDATA WHERE M_SWVMID={vmid} AND cast (M_STIME as date)='2023-08-29' AND
        M_SWTID BETWEEN {comma[10]} and {comma[11]} AND M_SWCMDID BETWEEN 1 AND 4 ORDER BY M_SWCMDID"""

        return execute_query(query)

    query = f"""SELECT M_SFVALUE, cast (M_STIME as date) FROM L3CURRENTDATA WHERE M_SWVMID={vmid} AND cast (M_STIME as date)='2023-08-29' AND
            M_SWTID={comma[10]} AND M_SWCMDID BETWEEN 1 AND 4 ORDER BY M_SWCMDID"""

    return execute_query(query)


def get_response(cmd):
    data = []
    checker = 0x01
    incoming_data = get_datetime()
    response = [0xc3] + [0x81] + \
               [0x00] + [0x16] + \
               [0x00] + [0x01] + \
               [0x00] + [0x00] + \
               [0x00] + [0x00] + \
               [0x00] + [0x00] + \
               [checker] + \
               [struct.pack("!f", incoming_data["minute"])[1]] + \
               [struct.pack("!f", incoming_data["hour"])[1]] + [struct.pack("!f", incoming_data["day"])[1]] + \
               [struct.pack("!f", incoming_data["month"])[1]] + [struct.pack("!f", incoming_data["year"])[1]] + \
               [0x00] + [0x33]

    timer = get_datetime()
    inner = 0

    for i in range(0, cmd[9] // 4):
        if cmd[5] == 0x01:
            response[6] = struct.pack("!f", timer["second"])[1]
            response[7] = struct.pack("!f", timer["minute"])[1]
            response[8] = struct.pack("!f", timer["hour"])[1]
            response[9] = struct.pack("!f", timer["day"])[1]
            response[10] = struct.pack("!f", timer["month"])[1]
            response[11] = struct.pack("!f", timer["year"])[1]

            if response[7:12] == response[13:18]:
                checker = 0x00
                response[12] = checker

        elif cmd[5] == 0x40:
            data += get_incday_data(cmd, inner)
            inner += 1

        elif cmd[5] == 0x42:
            data += get_incmonth_data(cmd, inner)
            inner += 1

        elif cmd[5] == 0x52:
            data += get_min30_data(cmd, inner)
            inner += 1

        elif cmd[5] == 0x80:
            data += get_month_data(cmd, inner)
            inner += 1

        elif cmd[5] == 0x81:
            data += get_day_data(cmd, inner)
            inner += 1

        elif cmd[5] == 0x85:
            data = get_allen_data(cmd, inner)
            inner += 1

        else:
            return

    response = another_data(response, data, timer, cmd)
    response += reverse_CRC16(crc16_chk(response))
    printer(response, "Response")
    return response


if __name__ == "__main__":
    get_response(test_cmd(7))
    # try:
    #     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #
    #     server.bind(("0.0.0.0", 5009))
    #
    #     server.listen(500)
    #
    #     while True:
    #         client, address = server.accept()
    #         print(address)
    #         response = client.recv(1024)
    #         print(response.hex())
    #         command = []
    #         for i in range(0, len(response), 1):
    #             value = response[i:i + 1].hex()
    #             command.append(int('0x' + value, 16))
    #         print(command)
    #         client.send(bytes(get_response(command)))
    # except Exception as e:
    #     print(e)
