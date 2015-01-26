from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


class Connection:
    """
        Class that allows artists to connect with users.
    """

    def __init__(self):
        pass

    @staticmethod
    def contact_user(users=None):
        """
          Sends an email to the users supplied
        :param users:  The users to email
        :return: void
        """
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        if len(users) > 0:
            from_address = 'a@a.com'
            subject = 'A FanMobi gift from'
            text = 'Some gift text ' \
                   '<a href="https://www.google.com">Connect with me </a>'
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = from_address
            message['TO'] = ','.join(users)
            part = MIMEText(text, 'html')
            message.attach(part)
            server.login(from_address, 'password')
            server.sendmail(from_address, users, message.as_string())
        server.close()


def main():
    connection = Connection()
    connection.contact_user(['a@a.com'])


if  __name__ =='__main__':main()