from collections import OrderedDict
from .sqlutils import get_connection, Constants, build_where, hash_password,build_set


class UserDAO:

    def __init__(self):
        pass

    def login(self, email_address=None, password=None):
        """
           Determines whether the user sucessfully logged in with an email address
           and password
        :param email_address:
        :param password:
        :return: True if the credentials are valid, False otherwise
        """
        conn = get_connection()
        if not (email_address or password):
            return False
        with conn.cursor(try_plain_query=True) as cursor:
            criteria = {"username": email_address}
            cursor.execute("SELECT SALT FROM " + Constants.SCHEMA_NAME.value+"."+Constants.USERS.value
                           + build_where(criteria), criteria.values())
            for row in cursor:
                if not row[0]:
                    return False
                salt = row[0]
                hashed = hash_password(password=password, salt=salt)
                return self.user_exists(email_address=email_address, password=hashed['hashed_password'])['exists']
        return False

    def user_exists(self, email_address=None, password=None, facebook_id=None, twitter_id=None, user_id=None):
        """
           Determines if this user exists or not based on supplied criteria
        :param email_address:
        :param facebook_id:
        :param twitter_id:
        :param user_id:
        :return:
        """
        conn = get_connection()
        criteria = {}
        if email_address:
            criteria['username'] = email_address
            if password:
                criteria['password'] = password
        elif facebook_id:
            criteria['facebook_id'] = facebook_id
        elif twitter_id:
            criteria['twitter_id'] = twitter_id
        elif user_id:
            criteria['id'] = user_id
        if len(criteria) > 0:
            with conn.cursor(try_plain_query=True) as cursor:
                print(criteria.values())
                print(build_where(criteria))
                cursor.execute("SELECT COUNT(1), ID FROM " + Constants.SCHEMA_NAME.value+"."+Constants.USERS.value
                               + build_where(criteria), criteria.values())
                for row in cursor:
                    print(row)
                    if row[0] > 0:
                            return {"exists": True, "id": row[1]}
        return {"exists": False, "id": -1}

    def upsert(self, email_address=None, password=None, facebook_id=None, twitter_id=None):
        """
          Updates or inserts a new record depending on if the user was found
        :param email_address:
        :param password:
        :param facebook_id:
        :param twitter_id:
        :return: The user ID affected by this operation
        """
        conn = get_connection()
        with conn.cursor(try_plain_query=True) as cursor:
            existence_check = self.user_exists(email_address, facebook_id, twitter_id)
            print(existence_check)
            if not existence_check['exists']:
                hashed = hash_password(password)
                cursor.execute("INSERT INTO " + Constants.SCHEMA_NAME.value+"."+Constants.USERS.value
                               + "(username, password, salt, facebook_id, twitter_id) VALUES(?,?,?,?,?)"
                               , (email_address, hashed['hashed_password'], hashed['salt'], facebook_id, twitter_id))
                user_id = cursor.lastrowid
            else:
                user_id = existence_check['id']
                criteria = OrderedDict()
                if email_address:
                    criteria['username'] = email_address
                if facebook_id:
                    criteria['facebook_id'] = facebook_id
                if twitter_id:
                    criteria['twitter_id'] = twitter_id
                set_clause = build_set(criteria)
                criteria['ID'] = user_id
                cursor.execute("UPDATE " + Constants.SCHEMA_NAME.value+"."+Constants.USERS.value
                               + set_clause + " " + build_where({"ID": None}),
                               criteria.values())
        return user_id

    def delete(self):
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
    #dao.user_exists(email_address='test@test.com')
   # dao.find(dict)
    dao.upsert(email_address='t@t.com', password=None,facebook_id='UPDATED', twitter_id='aaa')

if __name__ == '__main__':
    main()
