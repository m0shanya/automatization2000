from main import *
from flask import Flask, render_template, request

app = Flask(__name__)


def data_list() -> dict:
    result = {}
    result["commands"] = ["Срез 30 мин E+", "Срез 30 мин E-", "Срез 30 мин R+", "Срез 30 мин R-"]
    with fdb.connect(**connection) as con:
        cur = con.cursor()
        query_for_vmid = f"""SELECT M_SVMETERNAME FROM SL3VMETERTAG ORDER BY M_SVMETERNAME """
        cur.execute(query_for_vmid)
        result["vmid"] = [vmid[0] for vmid in cur.fetchall()]

        query_for_date = f"""SELECT DISTINCT M_SDTDATE FROM L2HALF_HOURLY_ENERGY WHERE M_SWCMDID=13
        ORDER BY M_SDTDATE DESC"""
        cur.execute(query_for_date)
        result["date"] = [date[0].strftime("%Y-%m-%d") for date in cur.fetchall()]

        return result


@app.route("/", methods=["GET", "POST"])
def main_view():
    data = data_list()
    if request.method == 'POST':
        appended = request.form
        print(appended)
        time_list = [request.form["start_date"], request.form["end_date"]]
        vmid_list = [request.form["selected_items"]]
        dates = get_date(time_list)
        values = get_data(vmid_list, time_list, request.form["command"])
        do_write(values, dates, vmid_list, request.form["command"])
    return render_template("main_view.html", commands=data["commands"], dates=data["date"], vmids=data["vmid"])


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
