from gsmtpd import SMTPServer
from gevent import monkey
monkey.patch_all()


class Server(SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data):
        print(peer, mailfrom, rcpttos, len(data))

if __name__ == '__name__':
    s = Server(("127.1", 4000))
    s.serve_forever()
