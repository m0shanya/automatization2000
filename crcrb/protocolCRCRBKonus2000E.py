import struct
from datetime import datetime

from crc16ccc import crc16_chk, reverse_CRC16

command = {
    'get_type_USPD': [0xD0],
    'get_supported_device': [0xD1],
    'get_meter_device': [0xD2],
    'get_character_of_kanal': [0xD3],
    'get_instant_values': [0x00, 0xF1],

}

# start_device = []
start_device = [0x00, 0x01]
# count_device = []
count_device = [0x00, 0x01]
packet_length = [0x00, 0x18] #0x0A


def write_message(command):
    # data_message = [0x55, 0x81] + packet_length + command + start_device + count_device + [0x01, 0x23]
    data_message = [0x55, 0x81] + packet_length + command + start_device + count_device + [0x00, 0x00, 0xff, 0xff, 0xf7, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01]
    CRC = reverse_CRC16(crc16_chk(data_message))
    data_message += CRC
    print(data_message)
    return data_message


def config_USPD(response_from_uspd): #00D0
    print('Length_packet- ', int.from_bytes(response_from_uspd[2:4], 'big'))
    print('Type_of_USPD- ', response_from_uspd[6:38].decode('cp1251'))
    print('Name and adress_of_USPD- ', response_from_uspd[38:70].decode('cp1251'))

    print('Fab_number_USPD- ', int.from_bytes(response_from_uspd[70:74], 'big'))
    print('Ver. PO- ', int.from_bytes(response_from_uspd[74:76], 'big'))
    print('Count meter chanel- ', int.from_bytes(response_from_uspd[76:78], 'big'))

    print(f'Count of Group- ', int.from_bytes(response_from_uspd[78:80], 'big'))
    print('Tarif zone- ', int.from_bytes(response_from_uspd[80:82], 'big'))
    print('Max_type_meters- ', int.from_bytes(response_from_uspd[82:84],'big'))
    print('Connect device- ', int.from_bytes(response_from_uspd[84:86],'big'))
    print('Max length- ', int.from_bytes(response_from_uspd[89:90],'big'))


def list_of_suppported_device(response_from_uspd): #00D1
    print(f'Length_of_packet -', int.from_bytes(response_from_uspd[2:4], 'big'))
    print(f'Code_of_device | Name_of_device ')
    for i in range(32):
        print(int.from_bytes(response_from_uspd[i*18+6:i*18+8], 'big'), f'             |', response_from_uspd[i*18+8:i*18+23].decode('cp1251'))


def character_of_connected_device(response_from_uspd): #00D2
    print(f'Command- ', hex(int.from_bytes(response_from_uspd[5:6], 'big')))
    for i in range(3):
        # print(f'Command- ', hex(int.from_bytes(response_from_uspd[5:6], 'big')))
        print(f'Ndev- ', (int.from_bytes(response_from_uspd[i*64+6:i*64+8], 'big')))
        print(f'Code_device- ', int.from_bytes(response_from_uspd[i*64+8:i*64+10], 'big'))
        print(f'Factory_number- ', int.from_bytes(response_from_uspd[i*64+10:i*64+14], 'big'))
        print(f'Network_address- ', int.from_bytes(response_from_uspd[i*64+14:i*64+16], 'big'))
        print(f'Count_of_programming_channel- ', int.from_bytes(response_from_uspd[i*64+16:i*64+18], 'big'))
        print(f'Data_deep_in_day- ', int.from_bytes(response_from_uspd[i*64+18:i*64+20], 'big'))
        # print(f'Kpr- ', int(response_from_uspd[i*64+24]))
        # print(f'KT- ', response_from_uspd[i*64+21:i*64+28])
        # print(f'KMB- ', bin(int.from_bytes(response_from_uspd[i*64+28:i*64+30], 'big')))
        # print(f'STR name- ', response_from_uspd[i*52+38:i*52+70])
        print(f'STR name- ', {i}, response_from_uspd[i*64+38:i*64+70].decode('cp1251'))
    # print(f'Text- ', str(response_from_uspd[38:70]))


def get_character_of_chanel(response_from_uspd): #00D3
    print(f'Command- ', hex(int.from_bytes(response_from_uspd[5:6], 'big')))
    for i in range(4):
        print(f'Number_of_chanel_USPD - ', (int.from_bytes(response_from_uspd[i*52+6:i*52+8], 'big')))
        print(f'Number_of_device (Ndev) - ', int.from_bytes(response_from_uspd[i*52+8:i*52+10], 'big'))
        print(f'Number IK - ', int.from_bytes(response_from_uspd[i*52+10:i*52+12], 'big'))
        print(f'Ktr- ', int.from_bytes(response_from_uspd[i*52+12:i*52+16], 'big'))
        print(f'Kpr- ', int.from_bytes(response_from_uspd[i*52+16:i*52+20], 'big'))
        print(f'Kp- ', response_from_uspd[i*52+20:i*52+24])
        print(f'Pm- ', response_from_uspd[i*52+24])
        print(f'KMB- ', bin(response_from_uspd[i*52+25]))
        print(f'STR name- ', response_from_uspd[i*52+26:i*52+57])
        print(f'STR name- ', i, response_from_uspd[i*52+26:i*52+57].decode('cp1251'))
        print(' ')


def get_character_of_group(response_from_uspd):
    print(f'STR name- ', response_from_uspd[137:175])
    print(f'STR name- ', response_from_uspd[138:175].decode('cp1251'))


def instant_values(response):
    print(f'{datetime.now().time().strftime("%H:%M:%S")}: A_plus_phA: {struct.unpack(">f", response[6:10])[0]:0.4f} kW*h')
    print(f'{datetime.now().time().strftime("%H:%M:%S")}: A_plus_phB: {struct.unpack(">f", response[10:14])[0]:0.4f} kW*h')
    print(f'{datetime.now().time().strftime("%H:%M:%S")}: A_plus_phC: {struct.unpack(">f", response[14:18])[0]:0.4f} kW*h')
    print(f'{datetime.now().time().strftime("%H:%M:%S")}: A_plus_Summ: {struct.unpack(">f", response[18:22])[0]:0.4f} kW*h')


print(type(write_message(command['get_instant_values'])))
print(list(map(hex, write_message(command['get_instant_values']))))

instant_values(
    b'\xc3\x81\x00L\x00\xf1B\xccV\x04B\xcf\\(B\xc6\xb8RC\x98\x9a\x9fA\x14\x9b\xa6AHr\xafA7+\x01B\x05\x0eUE\xb9MtE\xb9\xab\x98E\xb8\x03M\x00\x00\x00\x00A\x9f\xe1\x84A\x9a\xdbqBH\x00\x00\x00\x15\n\x02\t\x16\x00\x01\x92c'
)
