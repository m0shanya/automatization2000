import fdb
import pandas as pd
import datetime as dt

connection = {'host': 'localhost',
              'database': '/home/timofey/test.fdb',
              'user': 'SYSDBA',
              'password': 'masterkey',
              'charset': 'WIN1251'
              }

time_dct = {"time": ["00:00-00:30", "00:30-01:00", "01:00-01:30", "01:30-02:00", "02:00-02:30", "02:30-03:00",
                     "03:00-03:30", "03:30-04:00", "04:00-04:30", "04:30-05:00", "05:00-05:30", "05:30-06:00",
                     "06:00-06:30", "06:30-07:00", "07:00-07:30", "07:30-08:00", "08:00-08:30", "08:30-09:00",
                     "09:00-09:30", "09:30-10:00", "10:00-10:30", "10:30-11:00", "11:00-11:30", "11:30-12:00",
                     "12:00-12:30", "12:30-13:00", "13:00-13:30", "13:30-14:00", "14:00-14:30", "14:30-15:00",
                     "15:00-15:30", "15:30-16:00", "16:00-16:30", "16:30-17:00", "17:00-17:30", "17:30-18:00",
                     "18:00-18:30", "18:30-19:00", "19:00-19:30", "19:30-20:00", "20:00-20:30", "20:30-21:00",
                     "21:00-21:30", "21:30-22:00", "22:00-22:30", "22:30-23:00", "23:00-23:30", "23:30-24:00"]}


def changer_command(command_name: str) -> int:
    cmdid = 0
    if command_name == "Срез 30 мин Е+":
        cmdid = 13
    elif command_name == "Срез 30 мин Е-":
        cmdid = 14
    elif command_name == "Срез 30 мин R+":
        cmdid = 15
    else:
        cmdid = 16
    return cmdid


def get_data(numb: list, time: list, cmd_name: str) -> dict:
    dlc = ["-"]
    res = {}

    command_id = changer_command(cmd_name)

    with fdb.connect(**connection) as con:
        for element in numb:
            dates = get_date(time)

            value = []

            cur = con.cursor()

            query_element = f"""SELECT M_SWVMID FROM SL3VMETERTAG 
            WHERE M_SVMETERNAME='{element}'"""
            cur.execute(query_element)
            vmid = cur.fetchone()

            query = f"""SELECT * FROM L2HALF_HOURLY_ENERGY 
            WHERE M_SWCMDID={command_id} AND 
            M_SDTDATE BETWEEN \'{time[0]}\' and \'{time[1]}\' AND M_SWVMID={vmid[0]} ORDER BY M_SDTDATE"""
            cur.execute(query)
            i = 0
            j = 0
            for val in cur.fetchall():

                for item in dates:
                    if i - j > 0:
                        item = dates[i - j]
                    i += 1
                    tmp = item.split("-")
                    if dt.datetime(int(tmp[0]), int(tmp[1]), int(tmp[2])) == val[5]:
                        j += 1
                        dates.remove(item)
                        value += val[6:54]
                        break
                    else:
                        value = value + dlc * 48
                        item = dates[i - j]

            res[f"Датчик {element}"] = value

    return res


def get_date(time: list) -> list:
    start_date = time[0]
    end_date = time[1]
    dates = pd.date_range(
        min(start_date, end_date),
        max(start_date, end_date)
    ).strftime('%Y-%m-%d').tolist()

    return dates


def do_write(val: dict, list_of_dates: list, vmids: list, filename: str):
    prime_values = dict(sorted(security(val, list_of_dates).items()))
    dataframe = pd.DataFrame(prime_values)
    with pd.ExcelWriter(f'{filename}.xlsx', engine="openpyxl", mode="a") as writer:
        dataframe.to_excel(writer, sheet_name=f'{vmids[0]}..{vmids[-1]}',
                           index=False)


def security(dct_of_values: dict, spisok_dat: list):
    spis_of_dates = []
    for item in spisok_dat:
        spis_of_dates = spis_of_dates + [item] * 48

    dct_of_values["date"] = spis_of_dates
    max_len_list = 0
    for val in dct_of_values.values():
        max_len_list = len(val)
        break

    for val in dct_of_values.values():
        max_len = len(val)
        if max_len > max_len_list:
            max_len_list = max_len

    dlc = ["-"]

    for key in dct_of_values.keys():
        if len(dct_of_values[key]) < max_len_list:
            dct_of_values[key] = dct_of_values[key] + dlc * (max_len_list - len(dct_of_values[key]))

    dct_of_values["time"] = time_dct["time"] * int((max_len_list / 48))

    return dct_of_values


# if __name__ == "__main__":
#     time_list = ['2023-02-26 00:00:00', '2023-02-28 00:00:00']
#     vmid_list = ['Office CE301']
#     dates = get_date(time_list)
#     values = get_data(vmid_list, time_list, 'Срез 30 мин E+')
#     do_write(values, dates, vmid_list, 'Срез 30 мин E+')
