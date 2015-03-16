from enum import Enum
import hashlib
import oursql
import uuid


def get_connection():
    return oursql.connect(host='localhost', port=3306, user='ts',
                          passwd='example', db='fanmobi')


def build_where(criteria=None):
    """
      Generates a where clause with holders e.g.
      where foo=? and bar=?
    :param criteria:
    :return:
    """
    to_return = ""
    if criteria:
        to_return = " WHERE "
        delimeter = " = ? AND "
        to_return += delimeter.join(criteria.keys())
        to_return += " = ?"
    return to_return


def build_set(criteria=None):
    """
       Builds a SET clause with holders e.g.
       set foo=?,bar=?
    :param criteria:
    :return:
    """
    to_return = ""
    if criteria:
        to_return = " SET "
        delimeter = " = ? , "
        to_return += delimeter.join(criteria.keys())
        to_return += " = ?"
    return to_return

def get_salt():
    """
        Generates a salt that can be used for passwords
    :return:  The generated salt
    """
    return uuid.uuid4().hex


def hash_password(password=None, salt=None):
    """
        Attempts to hash a password
    :return: The hashed password as well as the associated salt
    """
    mapping = {'hashed_password': None, 'salt': None}
    if password:
        if not salt:
            salt = get_salt()
        hashed_password = hashlib.sha512(password.encode('UTF-8') + salt.encode('UTF-8')).hexdigest()
        mapping['hashed_password'] = hashed_password
        mapping['salt'] = salt
    return mapping


class Constants(Enum):
    """
        Holds constants that are database related.  This prevents magic string from appearing
        everywhere
    """
    ARTIST_PROFILE = "artist_profiles"
    SCHEMA_NAME = "fanmobi"
    USERS = "users"
    USER_CONNECTIONS = "user_connections"
    ARTIST_LOCATIONS = "artist_locations"
