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


import unittest

from collections import namedtuple
from unittest import mock
from unittest.mock import patch

from directord import main
from directord import tests


class TestMain(tests.TestBase):
    def setUp(self):
        super().setUp()
        self.maxDiff = 20000
        self.args = tests.FakeArgs()
        self.systemdinstall = main.SystemdInstall()
        parse_driver_args_se = lambda x, y, z: x
        mock_parse_driver_args = mock.Mock()
        mock_parse_driver_args.side_effect = parse_driver_args_se
        main._parse_driver_args = mock_parse_driver_args

    def test__args_default(self):
        self.assertRaises(
            SystemExit,
            main._args,
            [""],
        )

    def test__args_orchestrate(self):
        args, _ = main._args(["orchestrate", "file1 file2"])
        self.assertDictEqual(
            vars(args),
            {
                "config_file": None,
                "check": False,
                "datastore": "memory",
                "debug": False,
                "driver": "zmq",
                "finger_print": False,
                "force_async": False,
                "job_port": 5555,
                "backend_port": 5556,
                "ignore_cache": False,
                "heartbeat_interval": 60,
                "identity": None,
                "socket_group": "0",
                "socket_path": "/var/run/directord.sock",
                "stream": False,
                "cache_path": "/var/cache/directord",
                "mode": "orchestrate",
                "wait": False,
                "target": None,
                "orchestrate_files": ["file1 file2"],
                "poll": False,
                "restrict": None,
            },
        )

    def test__args_run(self):
        args, _ = main._args(["exec", "--verb", "RUN", "command1"])
        self.assertDictEqual(
            vars(args),
            {
                "config_file": None,
                "check": False,
                "datastore": "memory",
                "debug": False,
                "driver": "zmq",
                "job_port": 5555,
                "backend_port": 5556,
                "heartbeat_interval": 60,
                "identity": None,
                "socket_group": "0",
                "socket_path": "/var/run/directord.sock",
                "stream": False,
                "cache_path": "/var/cache/directord",
                "mode": "exec",
                "verb": "RUN",
                "wait": False,
                "target": None,
                "exec": ["command1"],
                "force_async": False,
                "poll": False,
            },
        )

    def test__args_copy(self):
        args, _ = main._args(["exec", "--verb", "COPY", "file1 file2"])
        self.assertDictEqual(
            vars(args),
            {
                "config_file": None,
                "check": False,
                "datastore": "memory",
                "debug": False,
                "driver": "zmq",
                "job_port": 5555,
                "backend_port": 5556,
                "heartbeat_interval": 60,
                "identity": None,
                "socket_group": "0",
                "socket_path": "/var/run/directord.sock",
                "stream": False,
                "cache_path": "/var/cache/directord",
                "mode": "exec",
                "verb": "COPY",
                "wait": False,
                "target": None,
                "exec": ["file1 file2"],
                "force_async": False,
                "poll": False,
            },
        )

    def test__args_add(self):
        args, _ = main._args(["exec", "--verb", "ADD", "file1 file2"])
        self.assertDictEqual(
            vars(args),
            {
                "config_file": None,
                "check": False,
                "datastore": "memory",
                "debug": False,
                "driver": "zmq",
                "job_port": 5555,
                "backend_port": 5556,
                "heartbeat_interval": 60,
                "identity": None,
                "socket_group": "0",
                "socket_path": "/var/run/directord.sock",
                "stream": False,
                "cache_path": "/var/cache/directord",
                "mode": "exec",
                "verb": "ADD",
                "wait": False,
                "target": None,
                "exec": ["file1 file2"],
                "force_async": False,
                "poll": False,
            },
        )

    def test__args_arg(self):
        args, _ = main._args(["exec", "--verb", "ARG", "key value"])
        self.assertDictEqual(
            vars(args),
            {
                "config_file": None,
                "check": False,
                "datastore": "memory",
                "debug": False,
                "driver": "zmq",
                "job_port": 5555,
                "backend_port": 5556,
                "heartbeat_interval": 60,
                "identity": None,
                "socket_group": "0",
                "socket_path": "/var/run/directord.sock",
                "stream": False,
                "cache_path": "/var/cache/directord",
                "mode": "exec",
                "verb": "ARG",
                "wait": False,
                "target": None,
                "exec": ["key value"],
                "force_async": False,
                "poll": False,
            },
        )

    def test__args_env(self):
        args, _ = main._args(["exec", "--verb", "ENV", "key value"])
        self.assertDictEqual(
            vars(args),
            {
                "config_file": None,
                "check": False,
                "datastore": "memory",
                "debug": False,
                "driver": "zmq",
                "job_port": 5555,
                "backend_port": 5556,
                "heartbeat_interval": 60,
                "identity": None,
                "socket_group": "0",
                "socket_path": "/var/run/directord.sock",
                "stream": False,
                "cache_path": "/var/cache/directord",
                "mode": "exec",
                "verb": "ENV",
                "wait": False,
                "target": None,
                "exec": ["key value"],
                "force_async": False,
                "poll": False,
            },
        )

    def test__args_workdir(self):
        args, _ = main._args(["exec", "--verb", "WORKDIR", "/path"])
        print(vars(args))
        self.assertDictEqual(
            vars(args),
            {
                "config_file": None,
                "check": False,
                "datastore": "memory",
                "debug": False,
                "driver": "zmq",
                "job_port": 5555,
                "backend_port": 5556,
                "heartbeat_interval": 60,
                "identity": None,
                "socket_group": "0",
                "socket_path": "/var/run/directord.sock",
                "stream": False,
                "cache_path": "/var/cache/directord",
                "mode": "exec",
                "verb": "WORKDIR",
                "wait": False,
                "target": None,
                "exec": ["/path"],
                "force_async": False,
                "poll": False,
            },
        )

    def test__args_cachefile(self):
        args, _ = main._args(["exec", "--verb", "CACHEFILE", "/path"])
        self.assertDictEqual(
            vars(args),
            {
                "config_file": None,
                "check": False,
                "datastore": "memory",
                "debug": False,
                "driver": "zmq",
                "job_port": 5555,
                "backend_port": 5556,
                "heartbeat_interval": 60,
                "identity": None,
                "socket_group": "0",
                "socket_path": "/var/run/directord.sock",
                "stream": False,
                "cache_path": "/var/cache/directord",
                "mode": "exec",
                "verb": "CACHEFILE",
                "wait": False,
                "target": None,
                "exec": ["/path"],
                "force_async": False,
                "poll": False,
            },
        )

    def test__args_cacheevict(self):
        args, _ = main._args(["exec", "--verb", "CACHEEVICT", "all"])
        self.assertDictEqual(
            vars(args),
            {
                "config_file": None,
                "check": False,
                "datastore": "memory",
                "debug": False,
                "driver": "zmq",
                "job_port": 5555,
                "backend_port": 5556,
                "heartbeat_interval": 60,
                "identity": None,
                "socket_group": "0",
                "socket_path": "/var/run/directord.sock",
                "stream": False,
                "cache_path": "/var/cache/directord",
                "mode": "exec",
                "verb": "CACHEEVICT",
                "wait": False,
                "target": None,
                "exec": ["all"],
                "force_async": False,
                "poll": False,
            },
        )

    def test__args_query(self):
        args, _ = main._args(["exec", "--verb", "QUERY", "var"])
        self.assertDictEqual(
            vars(args),
            {
                "config_file": None,
                "check": False,
                "datastore": "memory",
                "debug": False,
                "driver": "zmq",
                "job_port": 5555,
                "backend_port": 5556,
                "heartbeat_interval": 60,
                "identity": None,
                "socket_group": "0",
                "socket_path": "/var/run/directord.sock",
                "stream": False,
                "cache_path": "/var/cache/directord",
                "mode": "exec",
                "verb": "QUERY",
                "wait": False,
                "target": None,
                "exec": ["var"],
                "force_async": False,
                "poll": False,
            },
        )

    def test__args_server(self):
        args, _ = main._args(["server"])
        self.assertDictEqual(
            vars(args),
            {
                "config_file": None,
                "datastore": "memory",
                "debug": False,
                "driver": "zmq",
                "job_port": 5555,
                "backend_port": 5556,
                "heartbeat_interval": 60,
                "identity": None,
                "socket_group": "0",
                "socket_path": "/var/run/directord.sock",
                "cache_path": "/var/cache/directord",
                "mode": "server",
            },
        )

    def test__args_client(self):
        args, _ = main._args(["client"])
        self.assertDictEqual(
            vars(args),
            {
                "config_file": None,
                "datastore": "memory",
                "debug": False,
                "driver": "zmq",
                "job_port": 5555,
                "backend_port": 5556,
                "heartbeat_interval": 60,
                "identity": None,
                "socket_group": "0",
                "socket_path": "/var/run/directord.sock",
                "cache_path": "/var/cache/directord",
                "machine_id": None,
                "mode": "client",
                "identity": None,
            },
        )

    def test__args_manage_list_nodes(self):
        args, _ = main._args(["manage", "--list-nodes"])
        self.assertDictEqual(
            vars(args),
            {
                "config_file": None,
                "datastore": "memory",
                "debug": False,
                "driver": "zmq",
                "dump_cache": False,
                "export_jobs": None,
                "export_nodes": None,
                "filter": None,
                "job_info": None,
                "job_port": 5555,
                "analyze_job": None,
                "analyze_parent": None,
                "analyze_all": False,
                "backend_port": 5556,
                "heartbeat_interval": 60,
                "identity": None,
                "socket_group": "0",
                "socket_path": "/var/run/directord.sock",
                "cache_path": "/var/cache/directord",
                "list_jobs": False,
                "list_nodes": True,
                "mode": "manage",
                "purge_jobs": False,
                "purge_nodes": False,
            },
        )

    def test__args_manage_list_jobs(self):
        args, _ = main._args(["manage", "--list-jobs"])
        self.assertDictEqual(
            vars(args),
            {
                "config_file": None,
                "datastore": "memory",
                "debug": False,
                "driver": "zmq",
                "dump_cache": False,
                "export_jobs": None,
                "export_nodes": None,
                "filter": None,
                "job_info": None,
                "job_port": 5555,
                "analyze_job": None,
                "analyze_parent": None,
                "analyze_all": False,
                "backend_port": 5556,
                "heartbeat_interval": 60,
                "identity": None,
                "socket_group": "0",
                "socket_path": "/var/run/directord.sock",
                "cache_path": "/var/cache/directord",
                "list_jobs": True,
                "list_nodes": False,
                "mode": "manage",
                "purge_jobs": False,
                "purge_nodes": False,
            },
        )

    def test__args_manage_purge_jobs(self):
        args, _ = main._args(["manage", "--purge-jobs"])
        self.assertDictEqual(
            vars(args),
            {
                "config_file": None,
                "datastore": "memory",
                "debug": False,
                "driver": "zmq",
                "dump_cache": False,
                "export_jobs": None,
                "export_nodes": None,
                "filter": None,
                "job_info": None,
                "job_port": 5555,
                "analyze_job": None,
                "analyze_parent": None,
                "analyze_all": False,
                "backend_port": 5556,
                "heartbeat_interval": 60,
                "identity": None,
                "socket_group": "0",
                "socket_path": "/var/run/directord.sock",
                "cache_path": "/var/cache/directord",
                "list_jobs": False,
                "list_nodes": False,
                "mode": "manage",
                "purge_jobs": True,
                "purge_nodes": False,
            },
        )

    def test__args_manage_purge_nodes(self):
        args, _ = main._args(["manage", "--purge-nodes"])
        self.assertDictEqual(
            vars(args),
            {
                "config_file": None,
                "datastore": "memory",
                "debug": False,
                "driver": "zmq",
                "dump_cache": False,
                "export_jobs": None,
                "export_nodes": None,
                "filter": None,
                "job_info": None,
                "job_port": 5555,
                "analyze_job": None,
                "analyze_parent": None,
                "analyze_all": False,
                "backend_port": 5556,
                "heartbeat_interval": 60,
                "identity": None,
                "socket_group": "0",
                "socket_path": "/var/run/directord.sock",
                "cache_path": "/var/cache/directord",
                "list_jobs": False,
                "list_nodes": False,
                "mode": "manage",
                "purge_jobs": False,
                "purge_nodes": True,
            },
        )

    def test__args_manage_job_info(self):
        args, _ = main._args(["manage", "--job-info", "xxxx"])
        self.assertDictEqual(
            vars(args),
            {
                "config_file": None,
                "datastore": "memory",
                "debug": False,
                "driver": "zmq",
                "dump_cache": False,
                "export_jobs": None,
                "export_nodes": None,
                "filter": None,
                "job_info": "xxxx",
                "job_port": 5555,
                "analyze_job": None,
                "analyze_parent": None,
                "analyze_all": False,
                "backend_port": 5556,
                "heartbeat_interval": 60,
                "identity": None,
                "socket_group": "0",
                "socket_path": "/var/run/directord.sock",
                "cache_path": "/var/cache/directord",
                "list_jobs": False,
                "list_nodes": False,
                "mode": "manage",
                "purge_jobs": False,
                "purge_nodes": False,
            },
        )

    def test__args_manage_export_jobs(self):
        args, _ = main._args(["manage", "--export-jobs", "xxxx"])
        self.assertDictEqual(
            vars(args),
            {
                "config_file": None,
                "datastore": "memory",
                "debug": False,
                "driver": "zmq",
                "dump_cache": False,
                "export_jobs": "xxxx",
                "export_nodes": None,
                "filter": None,
                "job_info": None,
                "job_port": 5555,
                "analyze_job": None,
                "analyze_parent": None,
                "analyze_all": False,
                "backend_port": 5556,
                "heartbeat_interval": 60,
                "identity": None,
                "socket_group": "0",
                "socket_path": "/var/run/directord.sock",
                "cache_path": "/var/cache/directord",
                "list_jobs": False,
                "list_nodes": False,
                "mode": "manage",
                "purge_jobs": False,
                "purge_nodes": False,
            },
        )

    def test__args_manage_export_nodes(self):
        args, _ = main._args(["manage", "--export-nodes", "xxxx"])
        self.assertDictEqual(
            vars(args),
            {
                "config_file": None,
                "datastore": "memory",
                "debug": False,
                "driver": "zmq",
                "dump_cache": False,
                "export_jobs": None,
                "export_nodes": "xxxx",
                "filter": None,
                "job_info": None,
                "job_port": 5555,
                "analyze_job": None,
                "analyze_parent": None,
                "analyze_all": False,
                "backend_port": 5556,
                "heartbeat_interval": 60,
                "identity": None,
                "socket_group": "0",
                "socket_path": "/var/run/directord.sock",
                "cache_path": "/var/cache/directord",
                "list_jobs": False,
                "list_nodes": False,
                "mode": "manage",
                "purge_jobs": False,
                "purge_nodes": False,
            },
        )

    def test__args_manage_bootstrap(self):
        m = unittest.mock.mock_open(read_data=tests.TEST_CATALOG.encode())
        with patch("builtins.open", m):
            args, _ = main._args(["bootstrap", "--catalog", "file"])
        self.assertDictEqual(
            vars(args),
            {
                "catalog": mock.ANY,
                "config_file": None,
                "datastore": "memory",
                "debug": False,
                "driver": "zmq",
                "job_port": 5555,
                "key_file": None,
                "backend_port": 5556,
                "heartbeat_interval": 60,
                "identity": None,
                "socket_group": "0",
                "socket_path": "/var/run/directord.sock",
                "threads": 10,
                "cache_path": "/var/cache/directord",
                "mode": "bootstrap",
            },
        )

    @patch("builtins.print")
    @patch("os.path.exists", autospec=True)
    @patch("os.makedirs", autospec=True)
    def test_systemdinstall_path_setup(
        self, mock_makedirs, mock_exists, mock_print
    ):
        mock_exists.return_value = False
        with patch("builtins.open", unittest.mock.mock_open()) as m:
            main.SystemdInstall().path_setup()
            m.assert_called()
        mock_makedirs.assert_called()
        mock_print.assert_called()

    @patch("os.path.exists", autospec=True)
    @patch("os.makedirs", autospec=True)
    def test_systemdinstall_path_setup_exists(
        self, mock_makedirs, mock_exists
    ):
        mock_exists.return_value = True
        with patch("builtins.open", unittest.mock.mock_open()) as m:
            main.SystemdInstall().path_setup()
            m.assert_not_called()
        mock_makedirs.assert_called()

    @patch("jinja2.FileSystemLoader", autospec=True)
    @patch("builtins.print")
    @patch("os.path.exists", autospec=True)
    @patch("os.makedirs", autospec=True)
    def test_systemdinstall_writer(
        self, mock_makedirs, mock_exists, mock_print, mock_jinja
    ):
        mock_exists.return_value = False
        with patch("builtins.open", unittest.mock.mock_open()) as m:
            main.SystemdInstall().writer(service_file="testfile")
            m.assert_called()
        mock_print.assert_called()
        mock_jinja.assert_called()

    @patch("builtins.print")
    @patch("os.path.exists", autospec=True)
    @patch("os.makedirs", autospec=True)
    def test_systemdinstall_writer_not_called(
        self, mock_makedirs, mock_exists, mock_print
    ):
        mock_exists.return_value = True
        with patch("builtins.open", unittest.mock.mock_open()) as m:
            main.SystemdInstall().writer(service_file="testfile")
            m.assert_not_called()
        mock_print.assert_called()

    @patch("jinja2.FileSystemLoader", autospec=True)
    @patch("builtins.print")
    @patch("os.path.exists", autospec=True)
    @patch("os.makedirs", autospec=True)
    def test_systemdinstall_server(
        self, mock_makedirs, mock_exists, mock_print, mock_jinja
    ):
        mock_exists.return_value = False
        with patch("builtins.open", unittest.mock.mock_open()) as m:
            main.SystemdInstall().writer(
                service_file="directord-client.service"
            )
            m.assert_called_with(
                "/etc/systemd/system/directord-client.service", "w"
            )
        mock_print.assert_called()
        mock_jinja.assert_called()

    @patch("jinja2.FileSystemLoader", autospec=True)
    @patch("builtins.print")
    @patch("os.path.exists", autospec=True)
    @patch("os.makedirs", autospec=True)
    def test_systemdinstall_client(
        self, mock_makedirs, mock_exists, mock_print, mock_jinja
    ):
        mock_exists.return_value = False
        with patch("builtins.open", unittest.mock.mock_open()) as m:
            main.SystemdInstall().writer(
                service_file="directord-server.service"
            )
            m.assert_called_with(
                "/etc/systemd/system/directord-server.service", "w"
            )
        mock_print.assert_called()
        mock_jinja.assert_called()

    @patch("jinja2.FileSystemLoader", autospec=True)
    @patch("builtins.print")
    @patch("os.path.exists", autospec=True)
    @patch("os.makedirs", autospec=True)
    def test_systemdinstall_server_service_file_dir(
        self, mock_makedirs, mock_exists, mock_print, mock_jinja
    ):
        mock_exists.return_value = False
        with patch("builtins.open", unittest.mock.mock_open()) as m:
            main.SystemdInstall(service_file_dir="/service-file-dir").writer(
                service_file="directord-client.service"
            )
            m.assert_called_with(
                "/service-file-dir/directord-client.service", "w"
            )
        mock_print.assert_called()
        mock_jinja.assert_called()

    @patch("jinja2.FileSystemLoader", autospec=True)
    @patch("builtins.print")
    @patch("os.path.exists", autospec=True)
    @patch("os.makedirs", autospec=True)
    def test_systemdinstall_client_service_file_dir(
        self, mock_makedirs, mock_exists, mock_print, mock_jinja
    ):
        mock_exists.return_value = False
        with patch("builtins.open", unittest.mock.mock_open()) as m:
            main.SystemdInstall(service_file_dir="/service-file-dir").writer(
                service_file="directord-client.service"
            )
            m.assert_called_with(
                "/service-file-dir/directord-client.service", "w"
            )
        mock_print.assert_called()
        mock_jinja.assert_called()

    @patch("directord.main._args", autospec=True)
    def test_main_server(self, mock__args):
        _args = {
            "config_file": None,
            "zmq_shared_key": None,
            "zmq_curve_encryption": False,
            "debug": False,
            "driver": "zmq",
            "job_port": 5555,
            "backend_port": 5556,
            "heartbeat_interval": 60,
            "socket_path": "/var/run/directord.sock",
            "stream": False,
            "cache_path": "/var/cache/directord",
            "mode": "server",
            "identity": None,
        }
        parsed_args = namedtuple("NameSpace", _args.keys())(*_args.values())
        mock__args.return_value = [parsed_args, mock.MagicMock()]
        with patch("directord.server.Server", autospec=True):
            main.main()

    @patch("directord.client.Client", autospec=True)
    @patch("directord.main._args", autospec=True)
    def test_main_client(self, mock__args, mock__client):
        _args = {
            "config_file": None,
            "zmq_shared_key": None,
            "zmq_curve_encryption": False,
            "debug": False,
            "driver": "zmq",
            "job_port": 5555,
            "backend_port": 5556,
            "heartbeat_interval": 60,
            "socket_path": "/var/run/directord.sock",
            "stream": False,
            "cache_path": "/var/cache/directord",
            "mode": "client",
            "identity": "client1",
        }
        parsed_args = namedtuple("NameSpace", _args.keys())(*_args.values())
        mock__args.return_value = [parsed_args, mock.MagicMock()]
        main.main()
        mock__client.assert_called_once_with(args=parsed_args)

    @patch("directord.main._args", autospec=True)
    def test_main_exec(self, mock__args):
        _args = {
            "config_file": None,
            "zmq_shared_key": None,
            "zmq_curve_encryption": False,
            "debug": False,
            "driver": "zmq",
            "job_port": 5555,
            "backend_port": 5556,
            "heartbeat_interval": 60,
            "socket_path": "/var/run/directord.sock",
            "stream": False,
            "cache_path": "/var/cache/directord",
            "mode": "exec",
            "verb": "RUN",
            "target": None,
            "wait": False,
            "exec": ["command1"],
            "poll": False,
            "identity": None,
        }
        parsed_args = namedtuple("NameSpace", _args.keys())(*_args.values())
        mock__args.return_value = [parsed_args, mock.MagicMock()]
        with patch("directord.mixin.Mixin.run_exec", autospec=True):
            main.main()

    @patch("directord.main._args", autospec=True)
    def test_main_orchestrate(self, mock__args):
        _args = {
            "config_file": None,
            "zmq_shared_key": None,
            "zmq_curve_encryption": False,
            "debug": False,
            "driver": "zmq",
            "finger_print": False,
            "job_port": 5555,
            "backend_port": 5556,
            "ignore_cache": False,
            "heartbeat_interval": 60,
            "socket_path": "/var/run/directord.sock",
            "stream": False,
            "cache_path": "/var/cache/directord",
            "mode": "orchestrate",
            "target": None,
            "wait": False,
            "orchestrate_files": ["file1 file2"],
            "poll": False,
            "restrict": None,
            "identity": None,
        }
        parsed_args = namedtuple("NameSpace", _args.keys())(*_args.values())
        mock__args.return_value = [parsed_args, mock.MagicMock()]
        with patch("directord.mixin.Mixin.run_orchestration", autospec=True):
            main.main()

    @patch("directord.main._args", autospec=True)
    def test_main_manage(self, mock__args):
        _args = {
            "config_file": None,
            "zmq_shared_key": None,
            "zmq_curve_encryption": False,
            "debug": False,
            "driver": "zmq",
            "export_jobs": None,
            "export_nodes": None,
            "job_info": None,
            "job_port": 5555,
            "backend_port": 5556,
            "heartbeat_interval": 60,
            "socket_path": "/var/run/directord.sock",
            "stream": False,
            "cache_path": "/var/cache/directord",
            "list_jobs": False,
            "list_nodes": True,
            "mode": "manage",
            "purge_jobs": False,
            "purge_nodes": False,
            "identity": None,
        }
        parsed_args = namedtuple("NameSpace", _args.keys())(*_args.values())
        mock__args.return_value = [parsed_args, mock.MagicMock()]
        with patch("directord.user.Manage.run", autospec=True) as d:
            d.return_value = {}
            main.main()

    @patch("directord.main._args", autospec=True)
    def test_main_bootstrap(self, mock__args):
        _args = {
            "catalog": mock.ANY,
            "config_file": None,
            "zmq_shared_key": None,
            "zmq_curve_encryption": False,
            "debug": False,
            "driver": "zmq",
            "job_port": 5555,
            "key_file": None,
            "backend_port": 5556,
            "heartbeat_interval": 60,
            "socket_path": "/var/run/directord.sock",
            "stream": False,
            "threads": 10,
            "cache_path": "/var/cache/directord",
            "mode": "bootstrap",
            "identity": None,
        }
        parsed_args = namedtuple("NameSpace", _args.keys())(*_args.values())
        mock__args.return_value = [parsed_args, mock.MagicMock()]
        with patch(
            "directord.bootstrap.Bootstrap.bootstrap_cluster", autospec=True
        ):
            main.main()

    @patch("directord.main._args", autospec=True)
    def test_main_fail(self, mock__args):
        _args = {
            "catalog": mock.ANY,
            "config_file": None,
            "zmq_shared_key": None,
            "zmq_curve_encryption": False,
            "debug": False,
            "driver": "zmq",
            "job_port": 5555,
            "key_file": None,
            "backend_port": 5556,
            "heartbeat_interval": 60,
            "socket_path": "/var/run/directord.sock",
            "stream": False,
            "threads": 10,
            "cache_path": "/var/cache/directord",
            "mode": "UNDEFINED",
            "identity": None,
        }
        parsed_args = namedtuple("NameSpace", _args.keys())(*_args.values())
        parser = mock.MagicMock()
        mock__args.return_value = [parsed_args, parser]
        self.assertRaises(SystemExit, main.main)
        parser.print_help.assert_called()
