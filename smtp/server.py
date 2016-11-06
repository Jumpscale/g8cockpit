from email.parser import Parser
from email.utils import getaddresses, parsedate_to_datetime
import mimetypes
import tempfile
from os import path
import asyncore

from smtpd import SMTPServer


class Server(SMTPServer):

    def __init__(self, localaddr, remoteaddr, ays_client):
        super(Server, self).__init__(localaddr, remoteaddr)
        self._parser = Parser()
        self._ayscl = ays_client

    def _parse_mail(self, data):
        """
        Parse data from email and return a model Email object
        """
        msg = self._parser.parsestr(data)

        tos = msg.get_all('to', [])
        ccs = msg.get_all('cc', [])
        froms = msg.get_all('from', [])
        name, addr = getaddresses(froms)[0]

        email = {
            'sender': addr,
            'subject': msg['subject'],
            'to': [addr for name, addr in getaddresses(tos)],
            'cc': [addr for name, addr in getaddresses(ccs)],
            'epoch': int(parsedate_to_datetime(msg['Date']).timestamp()),
        }

        self._extract_content(email, msg)

        return email

    def _extract_content(self, email, msg):
        """
        email: dict containing the email detail
        msg: msg object from email.Parser()
        """
        out_dir = tempfile.mkdtemp()

        email['body'] = ''
        email['attachments'] = {}

        counter = 1
        for part in msg.walk():
            # multipart/* are just containers
            if part.get_content_maintype() == 'multipart':
                continue

            if part.get_content_type() == 'text/html':
                # TODO: convert html to md.
                # more check on content type for text
                email['body'] += part.get_payload()

            filename = part.get_filename()
            if not filename:
                ext = mimetypes.guess_extension(part.get_content_type())
                if not ext:
                    # Use a generic bag-of-bits extension
                    ext = '.bin'
                filename = 'part-%03d%s' % (counter, ext)

            # TODO:upload to store instead of local fs
            out_file = path.join(out_dir, filename)
            with open(out_file, "w") as f:
                f.write(part.get_payload())

            email['attachments'][path.basename(filename)] = out_file
            counter += 1

    def process_message(self, peer, mailfrom, rcpttos, data):
        email = self._parse_mail(data)
        self.send_event(email)
        # TODO save email to a store

    def send_to_store(self, email, store):
        raise NotImplementedError()

    def send_event(self, payload):
        self._ayscl.send_event('email', payload)

    def start(self):
        print("start listening on %s:%s" % self.addr)
        asyncore.loop()


if __name__ == '__main__':
    from JumpScale import j
    ayscl = j.clients.atyourservice.getFromConfig('/optvar/cfg/ays/ays.conf')
    s = Server(("0.0.0.0", 25), None, ayscl)
    s.start()
