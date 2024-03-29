# -*- coding: utf-8 -*-
from collections import OrderedDict
import json
from oursql import IntegrityError
import uuid
import time
from .sqlutils import get_connection, Constants, build_where, hash_password,build_set


def xstr(s):
    return '' if s is None else str(s)


def str2bool(s):
    return xstr(s).upper() == 'TRUE'


class UserDAO:

    MILLIS_IN_HOUR = 3600000

    def __init__(self):
        pass

    def artist_info(self, artist_id):
        """
        Retrieves artist info based on the supplied ID
        :param artist_id:
        :return:
        """
        conn = get_connection()
        with conn.cursor(try_plain_query=True) as cursor:
            cursor.execute("SELECT AP.ARTIST_ID,AP.NAME,AP.THUMBNAIL,AP.AVATAR_URL,"
                           " AP.WEBSITE,AP.FACEBOOK_ID,AP.TWITTER_ID,AP.YOUTUBE_ID,AP.SOUNDCLOUD_ID,"
                           " AP.ITUNES_URL,AP.TICKETMASTER_URL,AP.MERCHANDISE_URL,"
                           " AP.PAYPAL_EMAIL,AP.HOMETOWN,AP.BIOGRAPHY,"
                           " AG.GENRE FROM FANMOBI.ARTIST_PROFILES AP "
                           "LEFT JOIN FANMOBI.ARTIST_GENRES AG "
                           "ON AP.ARTIST_ID = AG.ARTIST_ID "
                           "WHERE AP.ARTIST_ID =?", [artist_id])
            response = """
            {
                   'artists': [
                   """
            matches = []
            genres = []
            processed_first = False
            for row in cursor:
                if not processed_first:
                    current = '{'
                    current += "'id': \"" + xstr(row[0]) + '\", '
                    current += "'name': \"" + xstr(row[1]) + '\", '
                    current += "'avatar-url-thumb': \"" + xstr(row[2]) + '\", '
                    current += "'avatar-url': \"" + xstr(row[3]) + '\", '
                    current += "'website': \"" + xstr(row[4]) + '\", '
                    current += "'facebook-id': \"" + xstr(row[5]) + '\", '
                    current += "'twitter-id': \"" + xstr(row[6]) + '\", '
                    current += "'youtube-id': \"" + xstr(row[7]) + '\", '
                    current += "'soundcloud-id': \"" + xstr(row[8]) + '\", '
                    current += "'itunes-url': \"" + xstr(row[9]) + '\", '
                    current += "'ticket-url': \"" + xstr(row[10]) + '\", '
                    current += "'merch-url': \"" + xstr(row[11]) + '\", '
                    current += "'paypal-email': \"" + xstr(row[12]) + '\", '
                    current += "'hometown': \"" + xstr(row[13]) + '\", '
                    current += "'bio': \"" + xstr(row[14]) + '\", '
                    processed_first = True
                if row[15]:
                    genres.append(row[15])
            current += "'genres': \"["+', '.join(genres)+"]\""
            current += '}'
            matches.append(current)
            response += current

        response += """
                    ]
                }
                        """
        response = response.replace("'", '"')
        print('Response: ' + response)
        response = json.loads(response)
        return response

    def in_radius(self, radius=0.0, longitude=0.0, latitude=0.0):
        """
           Determines all of the artists within the radius of the specified
           latitude and longitude
        :param radius:
        :param longitude:
        :param latitude:
        :return:
        """
        conn = get_connection()
        with conn.cursor(try_plain_query=True) as cursor:
            cursor.execute("SELECT AP.ARTIST_ID,AP.NAME,AP.THUMBNAIL,"
                           "UNIX_TIMESTAMP(AL.LOGGED), AL.SHOW_START,AL.SHOW_END FROM "
                           + Constants.SCHEMA_NAME.value+"."+Constants.ARTIST_LOCATIONS.value + " AS AL, "
                           + Constants.SCHEMA_NAME.value+"."+Constants.ARTIST_PROFILE.value + " AS AP "
                           + " WHERE AP.ARTIST_ID = AL.ARTIST_ID AND AL.ARTIST_ID IN( "
                           + """select `artist_id`
                            from(
                                SELECT
                                    artist_id,
                                    (
                                        6373 *
                                        acos(
                                            cos( radians( ? ) ) *
                                            cos( radians( ? ) ) *
                                            cos(
                                                radians( ? ) - radians(? )
                                            ) +
                                            sin(radians(? )) *
                                            sin(radians(?))
                                        )
                                    ) distance
                                FROM """ + Constants.SCHEMA_NAME.value+"."+Constants.ARTIST_PROFILE.value
                           + """
                                HAVING
                                    distance < ?
                                ORDER BY
                                    distance
                                ) x ) """,
                           (float(latitude), float(latitude), float(longitude), float(longitude), float(latitude), float(latitude), float(radius)))
            response = """
            {
                   'artists': [
                   """
            matches = []
            for row in cursor:
                now = int(time.time())
                """
                For an artist to have a “current broadcast point,” a couple things need to line up:
                1. The last logged location update for that artist needs to be more recent than an hour
                       before show start.
                 2. The current time needs to be between show start and show end.
                """

                if row[4] and row[5]:
                    during_show = (int(row[4]) <= now <= row[5])
                    last_logged = (now + self.MILLIS_IN_HOUR >= row[4])
                else:
                    during_show = False
                    last_logged = False

                broadcasting = during_show and last_logged
                current = '{'
                current += "'id': \"" + xstr(row[0]) + '\", '
                current += "'name': \"" + xstr(row[1]) + '\", '
                current += "'avatar-url-thumb': \"" + xstr(row[2]) + '\", '
                current += "'currently-broadcasting': boolean" + str(str2bool(broadcasting)).lower() + "boolean"
                current += '}'
                matches.append(current)
            response += ', '.join(matches)

        response += """
                    ]
                }
                        """
        response = response.replace("'", '"')
        response = response.replace("boolean", '')
        print('Response: ' + response)
        response = json.loads(response)
        return response

    def update_location(self, latitude, longitude, artist_id, show_start, show_end=None):
        """
        Updates a logged in artist's location
        :param latitude:
        :param longitude:
        :param artist_id:
        :param show_start: the timestamp that represents when this show starts
        :param show_end: optional parameter
        :return:
        """
        conn = get_connection()
        with conn.cursor(try_plain_query=True) as cursor:
            cursor.execute("INSERT INTO " + Constants.SCHEMA_NAME.value+"."+Constants.ARTIST_LOCATIONS.value +
                           "(latitude,longitude,show_start,show_end,artist_id) VALUES(?,?,?,?,?)",
                           (latitude, longitude, show_start, show_end, artist_id))


    def connected_to(self, user_id=None, is_artist=False):
        """
        Retrieves the users connected to the supplied user ID
        :param user_id:
        :return:
        """
        conn = get_connection()
        with conn.cursor(try_plain_query=True) as cursor:
            if is_artist:
                response = """
            {
                   'followers': [
                   """
                cursor.execute("SELECT USERNAME,FACEBOOK_ID,TWITTER_ID FROM "
                               + Constants.SCHEMA_NAME.value+"."+Constants.USERS.value
                               + " where ID IN ( SELECT USER FROM " + Constants.SCHEMA_NAME.value
                               + "." + Constants.USER_CONNECTIONS.value + " WHERE CONNECTED_TO = ?"
                               + ")", [int(user_id)])
                matches = []
                for row in cursor:
                    current = '{'
                    current += "'email': \"" + xstr(row[0]) + '\", '
                    current += "'facebook-id': \"" + xstr(row[1]) + '\", '
                    current += "'twitter-id': \"" + xstr(row[2]) + "\""
                    current += '}'
                    matches.append(current)
                response += ', '.join(matches)
            else:
                response = """
            {
                   'artists': [
                   """
                cursor.execute("SELECT ARTIST_ID,NAME,THUMBNAIL,ALLOWS_MESSAGES FROM "
                               + Constants.SCHEMA_NAME.value+"."+Constants.ARTIST_PROFILE.value
                               + " AP LEFT JOIN " + Constants.SCHEMA_NAME.value+"."+Constants.USERS.value
                               + " USER ON AP.artist_id = USER.id WHERE USER.ID IN ( SELECT USER FROM " + Constants.SCHEMA_NAME.value
                               + "." + Constants.USER_CONNECTIONS.value + " WHERE CONNECTED_TO = ?"
                               + ")", [int(user_id)])

                matches = []
                for row in cursor:
                    current = '{'
                    current += "'id': \"" + xstr(row[0]) + '\", '
                    current += "'name': \"" + xstr(row[1]) + '\", '
                    current += "'avatar-url-thumb': \"" + xstr(row[2]) + '\", '
                    current += "'allows-messages': boolean" + str(str2bool(row[3])).lower() + "boolean"
                    current += '}'
                    matches.append(current)
                response += ', '.join(matches)

        response += """
                ]
            }
                    """
        response = response.replace("'", '"')
        response = response.replace("boolean", '')
        print('Response: ' + response)
        response = json.loads(response)
        return response

    def link(self, user_id=None, artist_id=None, disconnect=False):
        """
          Creates a bi-directional link between user and artist.  If disconnect is True
          instead removes the bi-directional link.
        :param user_id:
        :param artist_id:
        :param disconnect - should a link be removed
        :return:
        """
        conn = get_connection()
        with conn.cursor(try_plain_query=True) as cursor:
            if not disconnect:
                try:
                    cursor.execute("INSERT INTO " + Constants.SCHEMA_NAME.value+"."+Constants.USER_CONNECTIONS.value +
                                   "(user,connected_to) VALUES(?,?)", (user_id, artist_id))

                    cursor.execute("INSERT INTO " + Constants.SCHEMA_NAME.value+"."+Constants.USER_CONNECTIONS.value +
                                   "(user,connected_to) VALUES(?,?)", (artist_id, user_id))
                except IntegrityError:
                    print("Duplicate key")
            else:
                try:
                    criteria = {"user": user_id, "connected_to": artist_id}
                    cursor.execute("DELETE FROM " + Constants.SCHEMA_NAME.value+"."+Constants.USER_CONNECTIONS.value +
                                   build_where(criteria), (criteria.values()))
                    criteria["user"] = artist_id
                    criteria["connected_to"] = user_id
                    cursor.execute("DELETE FROM " + Constants.SCHEMA_NAME.value+"."+Constants.USER_CONNECTIONS.value +
                                   build_where(criteria), (criteria.values()))
                except IntegrityError:
                    print("Failed link removal")

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
            return {"authenticated": False, "token": None}
        with conn.cursor(try_plain_query=True) as cursor:
            criteria = {"username": email_address}
            cursor.execute("SELECT SALT FROM " + Constants.SCHEMA_NAME.value+"."+Constants.USERS.value
                           + build_where(criteria), criteria.values())
            for row in cursor:
                if not row[0]:
                    return False
                salt = row[0]
                hashed = hash_password(password=password, salt=salt)
                authed = self.user_exists(email_address=email_address, password=hashed['hashed_password'])['exists']
                token = None
                if authed:
                    token = uuid.uuid4()
                    self.upsert(cookie=token, email_address=email_address)
                return {"authenticated": authed,
                        "token": token}
        return {"authenticated": False, "token": None}


    def user_exists(self, auth_token=None, email_address=None, password=None, facebook_id=None, twitter_id=None,
                    user_id=None, unique_id=None):
        """
           Determines if this user exists or not based on supplied criteria
        :param auth_token: - since the auth token is a UUID this should be guaranteed unique
        :param email_address:
        :param facebook_id:
        :param twitter_id:
        :param user_id:
        :parama unique_id: the UUID of the user
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
        elif auth_token:
            criteria['cookie'] = auth_token
        elif unique_id:
            criteria['unique_id'] = unique_id
        if len(criteria) > 0:
            with conn.cursor(try_plain_query=True) as cursor:
                print(criteria.values())
                print(build_where(criteria))
                cursor.execute("SELECT COUNT(1), ID FROM fanmobi.users"
                               + build_where(criteria), criteria.values())
                for row in cursor:
                    print(row)
                    if row[0] > 0:
                            return {"exists": True, "id": row[1]}
        return {"exists": False, "id": -1}

    def upsert(self, unique_id=None, cookie=None, email_address=None, password=None, facebook_id=None, twitter_id=None, logout=False):
        """
          Updates or inserts a new record depending on if the user was found
        :param email_address:
        :param password:
        :param facebook_id:
        :param twitter_id:
        :param logout - Should log out this user
        :return: The user ID affected by this operation
        """
        conn = get_connection()
        with conn.cursor(try_plain_query=True) as cursor:
            # existence_check = self.user_exists(auth_token=cookie, email_address=email_address,
            #                                    facebook_id=facebook_id, twitter_id=twitter_id)
            existence_check = self.user_exists(unique_id=unique_id)
            print(existence_check)
            if not existence_check['exists']:
                hashed = hash_password(password)
                cursor.execute("INSERT INTO fanmobi.users "
                               + "(username, password, salt, facebook_id, twitter_id, unique_id) VALUES(?,?,?,?,?,?)"
                               , (email_address, hashed['hashed_password'], hashed['salt'], facebook_id, twitter_id,
                                  unique_id))
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
                if cookie:
                    criteria['cookie'] = cookie
                if unique_id:
                    criteria['unique_id'] = unique_id
                set_clause = build_set(criteria)
                criteria['ID'] = user_id
                if logout:
                    criteria['cookie'] = None
                cursor.execute("UPDATE fanmobi.users "
                               + set_clause + " " + build_where({"ID": None}),
                               criteria.values())
        return user_id

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
