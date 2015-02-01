import tornado.escape as escape
import tornado.ioloop
import tornado.web
from fanmobi.dao import user


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
    (r"/user/", UserHandler)
])

if __name__ == "__main__":
    application.listen(10000)
    tornado.ioloop.IOLoop.instance().start()