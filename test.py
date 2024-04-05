import os, argparse
import pandas as pd
from configparser import ConfigParser
import sqlalchemy as db


def get_args():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("--database", help="Database .ini file", default='database.ini')
    arg_parser.add_argument("-d", "--dir", type=str, help='Directory with files (.txt) to process')

    args = arg_parser.parse_args()

    return args.database, args.dir


def get_db_ini(ini_file):
    db_parser = ConfigParser()
    db_parser.read(str(ini_file))

    # get section, default to postgresql
    ini = {}
    if db_parser.has_section('postgresql'):
        params = db_parser.items('postgresql')
        for param in params:
            ini[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format('postgresql', ini_file))

    return ini


def get_db_engine(ini):
    try:
        engine = db.create_engine(
            url="postgresql://{0}:{1}@{2}:{3}/{4}".format(
                ini['user'], ini['password'], ini['host'], ini['port'], ini['database']
            )
        )
        print('Conn successful!')
    except Exception as e:
        print("Connection could not be made due to the following error: \n", e)
        return
    return engine


if __name__ == "__main__":
    db_ini_file, directory_path = get_args()
    db_ini = get_db_ini(ini_file=db_ini_file)
    #print(db_ini)

    engine = get_db_engine(db_ini)
    conn = engine.connect()

    result = conn.execute("SELECT version();")
    for row in result:
        print("Database Version:", row[0])

    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory_path, filename)

            data = pd.read_csv(file_path, delimiter='\t')
            sql = f"INSERT INTO users (name, age) VALUES ({data['ID']}, {data['Name']});"

            conn.execute(sql)



    conn.close()
    engine.dispose()
