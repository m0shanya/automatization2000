'''Расчет CRC16 с полиномом 0xA001 с перестановкой байт.
    Используется для работы с приборами учета СС301, УСПД "КОНУС-2000Е".
    В качестве параметра передается на вход строка, для которой надо рассчитать CRC.
    На выходе список (list) из двух байт. '''
import sys

d = [0x00, 0x03, 0x01, 0x00, 0x00, 0x00]


def crc16_chk(data):
    reg_crc = 0xFFFF
    i = 0
    length = len(data)
    while length:

        reg_crc = reg_crc ^ data[i]

        for j in range(8):
            if (reg_crc & 0x01):
                reg_crc = (reg_crc >> 1) ^ 0xA001  # polynom CRC-16 0xA001 0x8005
            else:
                reg_crc = (reg_crc >> 1)
        length = length - 1
        i += 1
    return reg_crc


def reverse_CRC16(mes):
    CRC = mes
    reverse_CRC_Hi = CRC & 0xFF
    reverse_CRC_Lo = CRC >> 8
    reverse_CRC = [reverse_CRC_Hi, reverse_CRC_Lo]

    return reverse_CRC  # разворачивает CRC для протокола CRC RB


def CRC16(mes):
    CRC = mes
    CRC_Hi = CRC & 0xFF
    CRC_Lo = CRC >> 8
    CRC = [CRC_Lo, CRC_Hi]

    return CRC
