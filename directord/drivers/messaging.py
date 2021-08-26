#   Copyright 2021 Red Hat, Inc.
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

import subprocess
import struct
import time

from oslo_config import cfg
import oslo_messaging
from oslo_messaging.rpc import dispatcher
from oslo_messaging.rpc.server import expose

from directord import utils
from directord import drivers


class Driver(drivers.BaseDriver):

    def __init__(self, interface, args, encrypted_traffic_data, bind_address):
        super(Driver, self).__init__(
            args=args,
            encrypted_traffic_data=encrypted_traffic_data,
            bind_address=bind_address,
        )
        self.mode = getattr(args, "mode", None)
        # A reference to the interface object (either the Client or Server)
        self.interface = interface
        self.bind_address = bind_address
        self.conf = cfg.CONF
        self.conf.transport_url = 'amqp://{}:5672//'.format(self.bind_address)
        self.log.info("Bind address: {}".format(self.bind_address))
        self.transport = oslo_messaging.get_rpc_transport(self.conf)

    def run(self):
        if self.mode == "server":
            self.qdrouterd()
            msg_server = "server"
        else:
            msg_server = "client"

        target = oslo_messaging.Target(topic='heartbeat', server='server1')
        endpoints = [self]
        server = oslo_messaging.get_rpc_server(
            self.transport, target, endpoints, executor='threading',
            access_policy=dispatcher.ExplicitRPCAccessPolicy)
        self.log.info("Starting messaging server.")
        server.start()
        while True:
            time.sleep(1)

    def qdrouterd(self):
        self.log.info("Starting qdrouterd.")
        proc = subprocess.run(['qdrouterd', '-d'], check=True)

    def send(self, method, topic, message_parts):
        target = oslo_messaging.Target(topic=topic)
        client = oslo_messaging.RPCClient(self.transport, target)
        return client.call({}, method, message_parts=message_parts)

    @expose
    def heartbeat(self, context, message_parts):
        self.log.info("message_parts: {}".format(message_parts))
        self.log.info("message_parts len: {}".format(len(message_parts)))
        (
            identity,
            iD,
            control,
            command,
            data,
            info,
            stderr,
            stdout,
        ) = message_parts
        self.log.info("MODE: {}".format(self.mode))
        self.log.info("RPC call: heartbeat")
        self.log.info("message_parts: {}".format(message_parts))
        self.log.info("first control: {}".format(control))
        self.log.info("info: %s" % info)
        if control in [ self.heartbeat_ready,
                        self.heartbeat_notice,
        ]:
            print("CONTROL YESSSS")
        if info:
            info = struct.pack("<f", info)
        self.interface.process_heartbeat(identity.encode(), control.encode(),
                data, info)

    def process_message_parts(self, message_parts):
        if self.mode == 'client':
            message_parts.insert(0, None)
        return message_parts

    def send_heartbeat(self, identity=None, control=None, data=None, info=None):
        method = 'heartbeat'
        topic = 'heartbeat'
        message_parts = self.build_message_parts(
            identity=identity, control=control, data=data, info=info)
        return self.send(method, topic, message_parts)

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

        message_parts = self.build_message_parts(
            identity, msg_id, control, command, data, info, stderr, stdout)
        return socket.send_multipart(message_parts)

    def build_message_parts(
        self,
        identity=None,
        msg_id=None,
        control=None,
        command=None,
        data=None,
        info=None,
        stderr=None,
        stdout=None,
    ):
        if not msg_id:
            msg_id = utils.get_uuid().encode()

        if not control:
            control = self.nullbyte

        if not command:
            command = self.nullbyte

        if not data:
            data = self.nullbyte

        if not info:
            info = 0
        else:
            info = struct.unpack("<f", info)[0]

        if not stderr:
            stderr = self.nullbyte

        if not stdout:
            stdout = self.nullbyte

        message_parts = [msg_id, control, command, data, info, stderr, stdout]

        if self.mode == 'client' and not identity:
            identity = self.identity
        if identity:
            message_parts.insert(0, identity)

        return message_parts

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
