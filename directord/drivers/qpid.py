#   Copyright Peznauts <kevin@cloudnull.com>. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import proton
from proton import handlers
from proton import reactor

from directord import utils
from directord import drivers


class Server(handlers.MessagingHandler):
    def __init__(self, url, log):
        super(Server, self).__init__()
        self.log = log
        self.url = url
        self.senders = {}

    def on_start(self, event):
        print("Listening on", self.url)
        self.log.info("Listening on", self.url)
        self.container = event.container
        self.acceptor = event.container.listen(self.url)

    def on_link_opening(self, event):
        if event.link.is_sender:
            if event.link.remote_source and event.link.remote_source.dynamic:
                event.link.source.address = str(uuid.uuid4())
                self.senders[event.link.source.address] = event.link
            elif event.link.remote_target and event.link.remote_target.address:
                event.link.target.address = event.link.remote_target.address
                self.senders[event.link.remote_target.address] = event.link
            elif event.link.remote_source:
                event.link.source.address = event.link.remote_source.address
        elif event.link.remote_target:
            event.link.target.address = event.link.remote_target.address

    def on_message(self, event):
        print("Received", event.message)
        sender = self.senders.get(event.message.reply_to)
        if not sender:
            print("No link for reply")
            return
        sender.send(Message(address=event.message.reply_to, body=event.message.body.upper(),
                            correlation_id=event.message.correlation_id))


class Driver(drivers.BaseDriver):
    proto = "amqp"
    port = 5672

    def __init__(self, args, encrypted_traffic_data, bind_address):
        super(Driver, self).__init__(
            args=args,
            encrypted_traffic_data=encrypted_traffic_data,
            bind_address=bind_address,
        )

    def run(self):
        self.server = Server(self.bind_address, self.log)
        self.container = reactor.Container(server)
        self.container.run()

    def socket_send(
        self,
        socket=None,
        identity=None,
        msg_id=None,
        control=None,
        command=None,
        data=None,
        info=None,
        stderr=None,
        stdout=None,
    ):
        """Send a direct message over Qpid

        The message specification for server is as follows.

            [
                b"Identity"
                b"ID",
                b"ASCII Control Characters",
                b"command",
                b"data",
                b"info",
                b"stderr",
                b"stdout",
            ]

        The message specification for client is as follows.

            [
                b"ID",
                b"ASCII Control Characters",
                b"command",
                b"data",
                b"info",
                b"stderr",
                b"stdout",
            ]

        All message information is assumed to be byte encoded.

        All possible control characters are defined within the Interface class.
        For more on control characters review the following
        URL(https://donsnotes.com/tech/charsets/ascii.html#cntrl).

        :param socket: ZeroMQ socket object.
        :type socket: Object
        :param identity: Target where message will be sent.
        :type identity: Bytes
        :param msg_id: ID information for a given message. If no ID is
                       provided a UUID will be generated.
        :type msg_id: Bytes
        :param control: ASCII control charaters.
        :type control: Bytes
        :param command: Command definition for a given message.
        :type command: Bytes
        :param data: Encoded data that will be transmitted.
        :type data: Bytes
        :param info: Encoded information that will be transmitted.
        :type info: Bytes
        :param stderr: Encoded error information from a command.
        :type stderr: Bytes
        :param stdout: Encoded output information from a command.
        :type stdout: Bytes
        """

        if not msg_id:
            msg_id = utils.get_uuid().encode()

        if not control:
            control = self.nullbyte

        if not command:
            command = self.nullbyte

        if not data:
            data = self.nullbyte

        if not info:
            info = self.nullbyte

        if not stderr:
            stderr = self.nullbyte

        if not stdout:
            stdout = self.nullbyte

        message_parts = [msg_id, control, command, data, info, stderr, stdout]
        message = proton.Message(body=message_parts)
        sender = self.server.senders.get(identity)
        if not sender:
            sender = self.container.create_sender(identity)
            self.server.senders[identity] = sender

        sender.send(Message)

    @staticmethod
    def socket_recv(socket):
        """Receive a message over a ZM0 socket.

        The message specification for server is as follows.

            [
                b"Identity"
                b"ID",
                b"ASCII Control Characters",
                b"command",
                b"data",
                b"info",
                b"stderr",
                b"stdout",
            ]

        The message specification for client is as follows.

            [
                b"ID",
                b"ASCII Control Characters",
                b"command",
                b"data",
                b"info",
                b"stderr",
                b"stdout",
            ]

        All message parts are byte encoded.

        All possible control characters are defined within the Interface class.
        For more on control characters review the following
        URL(https://donsnotes.com/tech/charsets/ascii.html#cntrl).

        :param socket: ZeroMQ socket object.
        :type socket: Object
        """

        pass

    def job_connect(self):
        """Connect to a job socket and return the socket.

        :returns: Object
        """

        pass

    def transfer_connect(self):
        """Connect to a transfer socket and return the socket.

        :returns: Object
        """

        pass

    def heartbeat_connect(self):
        """Connect to a heartbeat socket and return the socket.

        :returns: Object
        """

        pass

    def heartbeat_bind(self):
        """Bind an address to a heartbeat socket and return the socket.

        :returns: Object
        """

        pass

    def job_bind(self):
        """Bind an address to a job socket and return the socket.

        :returns: Object
        """

        pass

    def transfer_bind(self):
        """Bind an address to a transfer socket and return the socket.

        :returns: Object
        """

        pass

    def bind_check(self, bind, interval=1, constant=1000):
        """Return True if a bind type contains work ready.

        :param bind: A given Socket bind to identify.
        :type bind: Object
        :param interval: Exponential Interval used to determine the polling
                         duration for a given socket.
        :type interval: Integer
        :param constant: Constant time used to poll for new jobs.
        :type constant: Integer
        :returns: Object
        """

        pass

    def key_generate(self, keys_dir, key_type):
        """Generate certificate.

        :param keys_dir: Full Directory path where a given key will be stored.
        :type keys_dir: String
        :param key_type: Key type to be generated.
        :type key_type: String
        """

        pass
