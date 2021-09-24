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

import json
import logging
import os

import tenacity
import zmq
import zmq.auth as zmq_auth
from zmq.auth.thread import ThreadAuthenticator

from directord import drivers
from directord import logger
from directord import utils


class Driver(drivers.BaseDriver):
    def __init__(
        self,
        args,
        encrypted_traffic_data=None,
        connection_string=None,
        interface=None,
    ):
        """Initialize the Driver.

        :param args: Arguments parsed by argparse.
        :type args: Object
        :param encrypted_traffic: Enable|Disable encrypted traffic.
        :type encrypted_traffic: Boolean
        :param connection_string: Connection string used to provide connection
                                  instructions to the driver.
        :type connection_string: String.
        :param interface: The interface instance (client/server)
        :type interface: Object
        """

        self.args = args
        self.encrypted_traffic_data = encrypted_traffic_data
        self.connection_string = connection_string
        if self.encrypted_traffic_data:
            self.encrypted_traffic = self.encrypted_traffic_data.get("enabled")
            self.secret_keys_dir = self.encrypted_traffic_data.get(
                "secret_keys_dir"
            )
            self.public_keys_dir = self.encrypted_traffic_data.get(
                "public_keys_dir"
            )
        else:
            self.encrypted_traffic = False
            self.secret_keys_dir = None
            self.public_keys_dir = None

        self.ctx = zmq.Context().instance()
        self.poller = zmq.Poller()
        super(Driver, self).__init__(
            args=args,
            encrypted_traffic_data=self.encrypted_traffic_data,
            connection_string=self.connection_string,
            interface=interface,
        )

    def __copy__(self):
        return Driver(
            args=self.args,
            encrypted_traffic_data=self.encrypted_traffic_data,
            connection_string=self.connection_string,
        )

    def _socket_context(self, socket_type):
        """Create socket context and return a bind object.

        :param socket_type: Set the Socket type, typically defined using a ZMQ
                            constant.
        :type socket_type: Integer
        :returns: Object
        """

        bind = self.ctx.socket(socket_type)
        # NOTE(cloudnull): STUPID SOLUTION. We should have
        #                  a more intelligent HWM solution.
        try:
            bind.sndhwm = bind.rcvhwm = 0
        except AttributeError:
            bind.hwm = 0

        bind.set_hwm(0)
        bind.setsockopt(zmq.SNDHWM, 0)
        bind.setsockopt(zmq.RCVHWM, 0)
        if socket_type == zmq.ROUTER:
            bind.setsockopt(zmq.ROUTER_MANDATORY, 1)
        return bind

    def _socket_bind(
        self, socket_type, connection, port, poller_type=zmq.POLLIN
    ):
        """Return a socket object which has been bound to a given address.

        When the socket_type is not PUB or PUSH, the bound socket will also be
        registered with self.poller as defined within the Interface
        class.

        :param socket_type: Set the Socket type, typically defined using a ZMQ
                            constant.
        :type socket_type: Integer
        :param connection: Set the Address information used for the bound
                           socket.
        :type connection: String
        :param port: Define the port which the socket will be bound to.
        :type port: Integer
        :param poller_type: Set the Socket type, typically defined using a ZMQ
                            constant.
        :type poller_type: Integer
        :returns: Object
        """

        bind = self._socket_context(socket_type=socket_type)
        auth_enabled = self.args.shared_key or self.args.curve_encryption

        if auth_enabled:
            self.auth = ThreadAuthenticator(self.ctx, log=self.log)
            self.auth.start()
            self.auth.allow()

            if self.args.shared_key:
                # Enables basic auth
                self.auth.configure_plain(
                    domain="*", passwords={"admin": self.args.shared_key}
                )
                bind.plain_server = True  # Enable shared key authentication
                self.log.info("Shared key authentication enabled.")
            elif self.args.curve_encryption:
                server_secret_file = os.path.join(
                    self.secret_keys_dir, "server.key_secret"
                )
                for item in [
                    self.public_keys_dir,
                    self.secret_keys_dir,
                    server_secret_file,
                ]:
                    if not os.path.exists(item):
                        raise SystemExit(
                            "The required path [ {} ] does not exist. Have"
                            " you generated your keys?".format(item)
                        )
                self.auth.configure_curve(
                    domain="*", location=self.public_keys_dir
                )
                try:
                    server_public, server_secret = zmq_auth.load_certificate(
                        server_secret_file
                    )
                except OSError as e:
                    self.log.error(
                        "Failed to load certificates: %s, Configuration: %s",
                        str(e),
                        vars(self.args),
                    )
                    raise SystemExit("Failed to load certificates")
                else:
                    bind.curve_secretkey = server_secret
                    bind.curve_publickey = server_public
                    bind.curve_server = True  # Enable curve authentication
        bind.bind(
            "{connection}:{port}".format(
                connection=connection,
                port=port,
            )
        )

        if socket_type not in [zmq.PUB]:
            self.poller.register(bind, poller_type)

        return bind

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(TimeoutError),
        wait=tenacity.wait_fixed(5),
        before_sleep=tenacity.before_sleep_log(
            logger.getLogger(name="directord"), logging.WARN
        ),
    )
    def _socket_connect(
        self, socket_type, connection, port, poller_type=zmq.POLLIN
    ):
        """Return a socket object which has been bound to a given address.

        > A connection back to the server will wait 10 seconds for an ack
          before going into a retry loop. This is done to forcefully cycle
          the connection object to reset.

        :param socket_type: Set the Socket type, typically defined using a ZMQ
                            constant.
        :type socket_type: Integer
        :param connection: Set the Address information used for the bound
                           socket.
        :type connection: String
        :param port: Define the port which the socket will be bound to.
        :type port: Integer
        :param poller_type: Set the Socket type, typically defined using a ZMQ
                            constant.
        :type poller_type: Integer
        :returns: Object
        """

        bind = self._socket_context(socket_type=socket_type)

        if self.args.shared_key:
            bind.plain_username = b"admin"  # User is hard coded.
            bind.plain_password = self.args.shared_key.encode()
            self.log.info("Shared key authentication enabled.")
        elif self.args.curve_encryption:
            client_secret_file = os.path.join(
                self.secret_keys_dir, "client.key_secret"
            )
            server_public_file = os.path.join(
                self.public_keys_dir, "server.key"
            )
            for item in [
                self.public_keys_dir,
                self.secret_keys_dir,
                client_secret_file,
                server_public_file,
            ]:
                if not os.path.exists(item):
                    raise SystemExit(
                        "The required path [ {} ] does not exist. Have"
                        " you generated your keys?".format(item)
                    )
            try:
                client_public, client_secret = zmq_auth.load_certificate(
                    client_secret_file
                )
                server_public, _ = zmq_auth.load_certificate(
                    server_public_file
                )
            except OSError as e:
                self.log.error(
                    "Error while loading certificates: %s. Configuration: %s",
                    str(e),
                    vars(self.args),
                )
                raise SystemExit("Failed to load keys.")
            else:
                bind.curve_secretkey = client_secret
                bind.curve_publickey = client_public
                bind.curve_serverkey = server_public

        if socket_type == zmq.SUB:
            bind.setsockopt_string(zmq.SUBSCRIBE, self.identity)
        else:
            bind.setsockopt_string(zmq.IDENTITY, self.identity)

        self.poller.register(bind, poller_type)
        bind.connect(
            "{connection}:{port}".format(
                connection=connection,
                port=port,
            )
        )

        self.log.info("Socket connected to [ %s ].", connection)
        return bind

    def socket_send(
        self,
        socket,
        identity=None,
        msg_id=None,
        control=None,
        command=None,
        data=None,
        info=None,
        stderr=None,
        stdout=None,
        nonblocking=False,
    ):
        """Send a message over a ZM0 socket.

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
        :param nonblocking: Enable non-blocking send.
        :type nonblocking: Boolean
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

        if identity:
            message_parts.insert(0, identity)

        if nonblocking:
            flags = zmq.NOBLOCK
        else:
            flags = 0

        self.log.debug("socket_send: {}".format(message_parts))
        return socket.send_multipart(message_parts, flags=flags)

    @staticmethod
    def socket_recv(socket, nonblocking=False):
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
        :param nonblocking: Enable non-blocking receve.
        :type nonblocking: Boolean
        """

        if nonblocking:
            flags = zmq.NOBLOCK
        else:
            flags = 0

        return socket.recv_multipart(flags=flags)

    def job_recv(self):
        """Receive a job message."""

        message_parts = Driver.socket_recv(socket=self.bind_job)
        if len(message_parts) == 7:
            message_parts.insert(0, b"")
        (
            identity,
            msg_id,
            control,
            _,
            data,
            info,
            stderr,
            stdout,
        ) = message_parts
        return (
            identity.decode(),
            msg_id.decode(),
            control,
            _,
            data.decode(),
            info.decode(),
            stderr.decode(),
            stdout.decode(),
        )

    def job_connect(self):
        """Connect to a job socket and return the socket.

        :returns: Object
        """

        self.log.debug("Establishing Job connection.")
        return self._socket_connect(
            socket_type=zmq.DEALER,
            connection=self.connection_string,
            port=self.args.job_port,
        )

    def job_init(self):
        """Initialize the heartbeat socket

        For server mode, this is a bound local socket.
        For client mode, it is a connection to the server socket.

        :returns: Object
        """
        if self.args.mode == "server":
            self.bind_job = self.job_bind()
        else:
            self.bind_job = self.job_connect()
        return self.bind_job

    def job_check(self, constant):
        """Check if the driver is ready to respond to a job request

        :param constant: Constant time used to poll for new jobs.
        :type constant: Integer
        :returns: Boolean
        """
        if self.bind_job and self.bind_check(
            bind=self.bind_job, constant=constant
        ):
            return True
        else:
            return False

    def job_ack_send(self, job_id):
        """Send job ack

        :param job_id: Job Id
        :type job_id: String
        """
        self.socket_send(
            socket=self.bind_job,
            msg_id=job_id.encode(),
            control=self.job_ack,
        )

    def job_send(self, identity, command, data="", info=""):
        """Send job.

        :param identity: Client identity
        :type identity: String
        :param command: Job command
        :type command: String
        :param data: Job data
        :type data: Dictionary
        """
        # We don't need identity.encode() here because the keys in self.workers
        # are encoded already.
        self.socket_send(
            socket=self.bind_job,
            identity=identity,
            command=command.encode(),
            data=data.encode(),
            info=info.encode(),
        )

    def backend_connect(self):
        """Connect to a backend socket and return the socket.

        :returns: Object
        """

        self.log.debug("Establishing backend connection.")
        bind = self._socket_connect(
            socket_type=zmq.DEALER,
            connection=self.connection_string,
            port=self.args.backend_port,
        )
        bind.set_hwm(16)
        self.log.debug(
            "Identity [ %s ] backend connect hwm state [ %s ]",
            self.identity,
            bind.get_hwm(),
        )
        return bind

    def heartbeat_connect(self):
        """Connect to a heartbeat socket and return the socket.

        :returns: Object
        """

        self.log.debug("Establishing Heartbeat connection.")
        return self._socket_connect(
            socket_type=zmq.DEALER,
            connection=self.connection_string,
            port=self.args.heartbeat_port,
        )

    def heartbeat_bind(self):
        """Bind an address to a heartbeat socket and return the socket.

        :returns: Object
        """

        return self._socket_bind(
            socket_type=zmq.ROUTER,
            connection=self.connection_string,
            port=self.args.heartbeat_port,
        )

    def heartbeat_reset(self, bind_heatbeat=None):
        """Reset the connection on the heartbeat socket.

        Returns a new ttl after reconnect.

        :param bind_heatbeat: heart beat bind object.
        :type bind_heatbeat: Object
        :returns: Tuple
        """

        if bind_heatbeat:
            self.poller.unregister(bind_heatbeat)
            self.log.debug("Unregistered heartbeat.")
            bind_heatbeat.close()
            self.log.debug("Heartbeat connection closed.")

        return (
            self.get_heartbeat(interval=self.args.heartbeat_interval),
            self.heartbeat_connect(),
        )

    def job_bind(self):
        """Bind an address to a job socket and return the socket.

        :returns: Object
        """

        return self._socket_bind(
            socket_type=zmq.ROUTER,
            connection=self.connection_string,
            port=self.args.job_port,
        )

    def backend_bind(self):
        """Bind an address to a backend socket and return the socket.

        :returns: Object
        """

        bind = self._socket_bind(
            socket_type=zmq.ROUTER,
            connection=self.connection_string,
            port=self.args.backend_port,
        )
        bind.set_hwm(16)
        self.log.debug(
            "Identity [ %s ] backend connect hwm state [ %s ]",
            self.identity,
            bind.get_hwm(),
        )
        return bind

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

        socks = dict(self.poller.poll(interval * constant))
        return socks.get(bind) == zmq.POLLIN

    def key_generate(self, keys_dir, key_type):
        """Generate certificate.

        :param keys_dir: Full Directory path where a given key will be stored.
        :type keys_dir: String
        :param key_type: Key type to be generated.
        :type key_type: String
        """

        zmq_auth.create_certificates(keys_dir, key_type)

    def create_proxy(front, back):
        """Create proxy bind.

        Bind two interfaces into a proxy.

        :param front: Frontend interface.
        :type front: Object
        :param back: Backend interface.
        :type back: Object
        """

        return zmq.proxy(frontend=front, backend=back)

    def heartbeat_send(
        self, identity=None, host_uptime=None, agent_uptime=None, version=None
    ):
        """Send a heartbeat.

        :param identity: Sender identity (uuid)
        :type identity: String
        :param host_uptime: Sender uptime
        :type host_uptime: String
        :param agent_uptime: Sender agent uptime
        :type agent_uptime: String
        :param version: Sender directord version
        :type version: String
        """
        self.socket_send(
            socket=self.bind_job,
            control=self.heartbeat_notice,
            data=json.dumps(
                {
                    "version": version,
                    "host_uptime": host_uptime,
                    "agent_uptime": agent_uptime,
                }
            ).encode(),
        )
