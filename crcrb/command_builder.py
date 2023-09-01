from crc16ccc import crc16_chk, reverse_CRC16  # для формирования контрольных символов(CRC*)
from main import read_tcp  # это функция для подключения и отправки сообщения на успд

commands = {
    "day": [0x81],
    "incday": [0x40],
    "allen": [0x85],
    "month": [0x80],
    "incmonth": [0x42],
    "min30": [0x52]
}  # это словарь команд, которые лежат в редисе, и их коды по документации


def append_channel_name(chnls: dict) -> list:  # заполнение списка атрибутов для команды(для каждого сообщения отдельно)
    # chnls = eval(str(chnls))
    pushable = [chnls['cmd'], chnls['vmid'], chnls['ago']]

    return pushable


def start_command(channel: list) -> list:
    """
    формирую байтовую команду для отправки на успд. Некоторые байты захардкожены, надо смотреть листик с договором,
    который лежит в рюкзаке, там я всё расписывал.
    """
    try:
        print("Process is starts...")
        command = []
        ago = 0

        for item in channel:  # кодирую сутки
            # for element in item:
            if channel[2] == 0:
                ago = 0x00
            elif channel[2] == 1:
                ago = 0x01
            else:
                ago = 0x02

            if item in commands.keys():
                command = commands[item]# кодирую команду
            break

        data_message = [0x55] + [0x81] + \
                       [0x00] + [0x12] + \
                       [0x00] + [command[0]] + \
                       [0x00] + [0x00] + \
                       [0x00] + [0x04] + \
                       [0x00] + [ago] + \
                       [0x00] + [0x00] + \
                       [0x00] + [0x04]
        crc = reverse_CRC16(crc16_chk(data_message))  # составляю ЦРЦ
        data_message += crc  # добавляю ЦРЦ во всю посылку

        res_str = ''
        for element in [hex(i) for i in data_message]:  # для печати посылки без лишних символов в консоль
            res_str += element.split('x')[1]
            res_str += ' '

        print(res_str)

        return data_message

    except Exception as e:
        print(e)


def run_cmd(mssg: list):  # подключение к успд и высылка байтовой посылки
    return read_tcp('128.65.22.23', 10001, mssg)


def run(message):  # запуск проги
    channels = append_channel_name(message)

    cmd = start_command(channels)

    run_cmd(cmd)


if __name__ == "__main__":
    run({"channel": "klass_klin", "cmd": "incday", "run": "ss301", "vmid": 21, "ph": 15, "trf": 4, "ki": 30, "ku": 1,
         "ago": 0, "cnt": 1, "overwrite": 0})
