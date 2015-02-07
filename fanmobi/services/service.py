from datetime import datetime
from fanmobi.dao import user
import time
import tornado.escape as escape
import tornado.ioloop
import tornado.web
import uuid


class FollowerHandler(tornado.web.RequestHandler):
    def get(self):
        dao = user.UserDAO()
        artist_id = str(self.request.uri).split("/")[2]
        self.write(dao.connected_to(user_id=artist_id, is_artist=True))

    def delete(self):
        data = escape.json_decode(self.request.body)
        dao = user.UserDAO()
        artist_id = str(self.request.uri).split("/")[2]
        dao.link(user_id=data['user-id'], artist_id=artist_id, disconnect=True)

    def put(self):
        data = escape.json_decode(self.request.body)
        dao = user.UserDAO()
        artist_id = str(self.request.uri).split("/")[2]
        dao.link(user_id=data['user-id'], artist_id=artist_id)


class ArtistLocationHandler(tornado.web.RequestHandler):
    def post(self):
        data = escape.json_decode(self.request.body)
        dao = user.UserDAO()
        self.write(dao.in_radius(radius=data['radius'],
                                 longitude=data['longitude'],
                                 latitude=data['latitude']))

    def put(self):
        """
        updates current artist location
        :return:
        """
        auth_token = self.request.headers.get('auth-token')
        data = escape.json_decode(self.request.body)
        dao = user.UserDAO()
        #2012-09-17T21:30:54-0400
        date_start = time.mktime(datetime.strptime(data['next-show-start'], '%Y-%m-%dT%H:%M:%S%z').timetuple())
        date_end = time.mktime(datetime.strptime(data['next-show-end'], '%Y-%m-%dT%H:%M:%S%z').timetuple())
        print(date_end)
        response = dao.user_exists(auth_token=auth_token)
        if response['exists']:
            dao.update_location(latitude=data['latitude'],
                                longitude=data['longitude'],
                                show_start=date_start,
                                show_end=date_end,
                                artist_id=response['id'])
        else:
            self.write("""
            {
            "message": "Invalid auth token"
            }
            """)


class ArtistLogoutHandler(tornado.web.RequestHandler):
    def put(self):
        data = escape.json_decode(self.request.body)
        dao = user.UserDAO()
        dao.upsert(cookie=data['auth-token'], logout=True)


class ArtistLoginHandler(tornado.web.RequestHandler):
    def put(self):
        data = escape.json_decode(self.request.body)
        dao = user.UserDAO()
        cookie = str(uuid.uuid4())
        if not data or not dao.login(email_address=data['email'], password=data['password']):
            self.write("{ \"message\": \"Email and password don't match.\"} ")
        else:
            self.write("{ \"auth-token\": \""+cookie+"\"} ")
        dao.upsert(email_address=data['email'], cookie=cookie)


class UserHandler(tornado.web.RequestHandler):
    """
       Responsible for handling the User API calls
    """

    def post(self):
        """
        Returns all artist to which the user is connected.
        :return:
        """
        data = escape.json_decode(self.request.body)
        print(data)
        dao = user.UserDAO()
        self.write(dao.connected_to(user_id=data['user-id'], is_artist=False))

    def put(self):
        if not self.request.body:
            data = {"email": None, "password": None, "facebook-id": None, "twitter-id": None}
        else:
            data = escape.json_decode(self.request.body)
        dao = user.UserDAO()
        generated_id = dao.upsert(email_address=data['email'], password=data['password'],
                                  facebook_id=data['facebook-id'], twitter_id=data['twitter-id'])
        self.write("{ \"user_id\": \"" + str(generated_id) + "\" }")

application = tornado.web.Application([
    (r"/artist/login", ArtistLoginHandler),
    (r"/artist/logout", ArtistLogoutHandler),
    (r"/artist/update-location", ArtistLocationHandler),
    (r"/artists/radius", ArtistLocationHandler),
    (r"/artists/[0-9]+/connected", FollowerHandler),
    (r"/user/", UserHandler),
    (r"/user/connected", UserHandler),
], cookie_secret="YOU_NEED_A_VALUE_HERE")

if __name__ == "__main__":
    application.listen(10000)
    tornado.ioloop.IOLoop.instance().start()