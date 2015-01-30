from enum import Enum
import hashlib
import uuid


class SQLUtils():
    """
        Common functions that other SQL related operations can use
    """
    def __init__(self):
        pass

    def get_salt(self):
        """
            Generates a salt that can be used for passwords
        :return:  The generated salt
        """
        return uuid.uuid4().hex

    def hash_password(self, password=None):
        """
            Attempts to hash a password
        :return: The hashed password as well as the associated salt
        """
        mapping = {'hashed_password': '', 'salt': ''}
        if password:
            salt = self.get_salt()
            hashed_password = hashlib.sha512(password + salt).hexdigest()
            mapping['hashed_password'] = hashed_password
            mapping['salt'] = salt
        return mapping

    class Constants(Enum):
        """
            Holds constants that are database related.  This prevents magic string from appearing
            everywhere
        """
        SCHEMA_NAME = "fanmobi"
