from JumpScale import j
from email.parser import Parser
from email.utils import getaddresses, parsedate_to_datetime
import mimetypes

from .gsmtpd import SMTPServer
from gevent import monkey
monkey.patch_all()


class Server(SMTPServer):

    def __init__(self, localaddr, redis=None):
        super(Server, self).__init__(localaddr)
        self._parser = Parser()
        self._rediscl = redis if redis else j.core.db

    def _parse_mail(self, data):
        """
        Parse data from email and return a model Email object
        """
        msg = self._parser.parsestr(data)
        email = j.data.models.cockpit_event.Email()
        email.subject = msg['subject']
        tos = msg.get_all('to', [])
        ccs = msg.get_all('cc', [])
        froms = msg.get_all('from', [])
        name, addr = getaddresses(froms)[0]
        email.sender = addr
        email.to = [addr for name, addr in getaddresses(tos)]
        email.cc = [addr for name, addr in getaddresses(ccs)]
        email.epoch = int(parsedate_to_datetime(msg['Date']).timestamp())
        self._extract_content(email, msg)

        return email

    def _extract_content(self, email, msg):
        """
        email: model object create from j.data.models.cockpit_event.Email
        msg: msg object from email.Parser()
        """
        out_dir = j.sal.fs.getTmpDirPath()

        counter = 1
        for part in msg.walk():
            # multipart/* are just containers
            if part.get_content_maintype() == 'multipart':
                continue

            if part.get_content_maintype() == 'text':
                # TODO: convert html to md.
                # more check on content type for text
                email.body += part.get_payload()

            filename = part.get_filename()
            if not filename:
                ext = mimetypes.guess_extension(part.get_content_type())
                if not ext:
                    # Use a generic bag-of-bits extension
                    ext = '.bin'
                filename = 'part-%03d%s' % (counter, ext)

            # TODO:upload to store instead of local fs
            out_file = j.sal.fs.joinPaths(out_dir, filename)
            j.sal.fs.writeFile(out_file, part.get_payload())

            email.attachments[j.sal.fs.getBaseName(filename)] = out_file
            counter += 1

    def process_message(self, peer, mailfrom, rcpttos, data):
        email = self._parse_mail(data)
        self.send_event(email.to_json())
        # TODO save email to a store

    def send_to_store(self, email, store):
        raise NotImplementedError()

    def send_event(self, payload):
        self._rediscl.publish('email', payload)


if __name__ == '__main__':
    s = Server(("127.1", 25))
    s.serve_forever()
    # messagefile = '/opt/code/mail2.txt'
    # with open(messagefile) as fp:
    #     msg = Parser().parse(fp)
    #
    # # msg = Parser().parsestr(data)
    #
    # email = j.data.models.cockpit_event.Email()
    # email.subject = msg['subject']
    # tos = msg.get_all('to', [])
    # ccs = msg.get_all('cc', [])
    # froms = msg.get_all('from', [])
    # name, addr = getaddresses(froms)[0]
    # email.sender = addr
    # email.to = [addr for name, addr in getaddresses(tos)]
    # email.cc = [addr for name, addr in getaddresses(ccs)]
    # email.epoch = int(parsedate_to_datetime(msg['Date']).timestamp())
    # out_dir = j.sal.fs.getTmpDirPath()
    #
    # counter = 1
    # for part in msg.walk():
    #     # multipart/* are just containers
    #     if part.get_content_maintype() == 'multipart':
    #         continue
    #
    #     # @TODO: check filename doens't try to erase important filename. e.g: ../../../etc/passwd
    #     if part.get_content_maintype() == 'text':
    #         email.body += part.get_payload()
    #     filename = part.get_filename()
    #     if not filename:
    #         ext = mimetypes.guess_extension(part.get_content_type())
    #         if not ext:
    #             # Use a generic bag-of-bits extension
    #             ext = '.bin'
    #         filename = 'part-%03d%s' % (counter, ext)
    #     counter += 1
    #     out_file = j.sal.fs.joinPaths(out_dir, filename)
    #     j.sal.fs.writeFile(out_file, part.get_payload())
    #     email.attachments[j.sal.fs.getBaseName(filename)] = out_file
    #
