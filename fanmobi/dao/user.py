import pymysql
from sqlutils import SQLUtils


def get_connection():
    return pymysql.connect(host='localhost', port=3306, user='root', passwd='', db='mysql')


class UserDAO:

    def __init__(self):
        pass

    def insert(self):
        pass

    def delete(self):
        pass

    def update(self):
        pass

    def find(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("select * from " + SQLUtils.Constants.SCHEMA_NAME.value+".users")
        print()

        for row in cursor:
            print(row)

        cursor.close()
        conn.close()


def main():
    dao = UserDAO()
    dao.find()


if __name__ == '__main__':
    main()
