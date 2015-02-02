import tornado.escape as escape
import tornado.ioloop
import tornado.web
from fanmobi.dao import user
import uuid


class ArtistLogoutHandler(tornado.web.RequestHandler):
    def put(self):
        self.clear_cookie("mycookie")


class ArtistLoginHandler(tornado.web.RequestHandler):
    def put(self):
        data = escape.json_decode(self.request.body)
        dao = user.UserDAO()
        print(data)
        if not data or not dao.login(email_address=data['email'], password=data['password']):
            self.write("{ \"message\": \"Email and password don't match.\"} ")
        else:
            if not self.get_secure_cookie("mycookie"):
                cookie = str(uuid.uuid4())
                self.set_secure_cookie("mycookie", cookie)
                self.write("{ \"auth-token\": \""+str(self.get_secure_cookie("mycookie"))+"\"} ")
            else:
                self.write("{ \"auth-token\": \""+str(self.get_secure_cookie("mycookie"))+"\"} ")
        print(self.get_secure_cookie("mycookie"))


class UserHandler(tornado.web.RequestHandler):
    """
       Responsible for handling the User API calls
    """

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
    (r"/user/", UserHandler)
], cookie_secret="YOU_NEED_A_VALUE_HERE")

if __name__ == "__main__":
    application.listen(10000)
    tornado.ioloop.IOLoop.instance().start()