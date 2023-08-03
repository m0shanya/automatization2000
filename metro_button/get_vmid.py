import fdb as firebirdsql
from flask import Flask
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
FB_HOST = os.environ.get("FB_HOST")
FB_DATABASE = os.environ.get("FB_DATABASE")
FB_USER = os.environ.get("FB_USER")
FB_PASSWORD = os.environ.get("FB_PASSWORD")

firebird_connection_config = {
    'host': FB_HOST,
    'database': FB_DATABASE,
    'user': FB_USER,
    'password': FB_PASSWORD
}

app = Flask(__name__)


@app.route('/', methods=['GET'])
def get_first_missing_id():
    with firebirdsql.connect(**firebird_connection_config) as con:
        cur = con.cursor()

        query = '''
            SELECT MIN(M_SWVMID+1) AS first_missing_id
            FROM (
                SELECT DISTINCT t1.M_SWVMID
                FROM SL3VMETERTAG t1
                LEFT JOIN SL3VMETERTAG t2 ON t1.M_SWVMID+1 = t2.M_SWVMID
                WHERE t2.M_SWVMID IS NULL
            ) AS subquery
        '''
        cur.execute(query)
        result = cur.fetchone()
        first_missing_id = result[0]

        response = {
            'first_missing_id': str(first_missing_id),
            'FB_HOST': FB_HOST,
            'FB_DATABASE': FB_DATABASE,
            'FB_USER': FB_USER,
            'FB_PASSWORD': FB_PASSWORD
        }

        query_add = f'INSERT INTO SL3VMETERTAG(M_SWVMID) VALUES ({first_missing_id})'
        cur.execute(query_add)

        return response


if __name__ == '__main__':
    app.run(port=8012)
