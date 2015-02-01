from sqlutils import get_connection, Constants, build_where,hash_password


class UserDAO:

    def __init__(self):
        pass

    def insert(self, email_address=None, password=None, facebook_id=None, twitter_id=None):
        conn = get_connection()
        with conn.cursor(try_plain_query=True) as cursor:
            hashed = hash_password(password)
            cursor.execute("INSERT INTO " + Constants.SCHEMA_NAME.value+"."+Constants.USERS.value
                           + "(username, password, salt, facebook_id, twitter_id) VALUES(?,?,?,?,?)"
                           , (email_address, hashed['hashed_password'], hashed['salt'], facebook_id, twitter_id))

    def delete(self):
        pass

    def update(self):
        pass

    def find(self, criteria=None):
        conn = get_connection()
        with conn.cursor(try_plain_query=True) as cursor:
            cursor.execute("select * from " + Constants.SCHEMA_NAME.value+"."+Constants.USERS.value
                           + build_where(criteria), criteria.values())
            print()

            for row in cursor:
                print(row)


def main():
    dao = UserDAO()
    dict = {"username": 'test@test.com'}
   # dao.find(dict)
   # dao.insert('t@t.com', 'password', 'uuu', 'aaa')

if __name__ == '__main__':
    main()
