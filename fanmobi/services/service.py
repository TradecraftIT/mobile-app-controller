import tornado.escape as escape
import tornado.ioloop
import tornado.web
from fanmobi.dao import user
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


class ArtistLogoutHandler(tornado.web.RequestHandler):
    def put(self):
        data = escape.json_decode(self.request.body)
        dao = user.UserDAO()
        dao.upsert(cookie=data['auth-token'],logout=True)


class ArtistLoginHandler(tornado.web.RequestHandler):
    def put(self):
        data = escape.json_decode(self.request.body)
        dao = user.UserDAO()
        if not data or not dao.login(email_address=data['email'], password=data['password']):
            self.write("{ \"message\": \"Email and password don't match.\"} ")
        else:
            if not self.get_secure_cookie("mycookie"):
                cookie = str(uuid.uuid4())
                self.set_secure_cookie("mycookie", cookie)
                self.write("{ \"auth-token\": \""+str(self.get_secure_cookie("mycookie"))+"\"} ")
            else:
                self.write("{ \"auth-token\": \""+str(self.get_secure_cookie("mycookie"))+"\"} ")
        dao.upsert(email_address=data['email'], cookie=str(self.get_secure_cookie("mycookie")))


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
    (r"/artists/[0-9]+/connected", FollowerHandler),
    (r"/user/", UserHandler),
    (r"/user/connected", UserHandler),
], cookie_secret="YOU_NEED_A_VALUE_HERE")

if __name__ == "__main__":
    application.listen(10000)
    tornado.ioloop.IOLoop.instance().start()