# Components

* TOC
{:toc}

Directord uses a DSL inspired by the `Containerfile` specification. The aim of
Directord isn't to create a new programing language, it is to get things done,
and then get out of the way.

## Components

To access component specific help information the `--exec-help` flag can be
used.

* Example

``` shell
$ directord exec --verb ${COMPONENT} '--exec-help true'
```

## Extra options

Every job has the ability to skip a cache hit should one be present on the
client node. To instruct the system to ignore all forms of cache, add the
`--skip-cache` to the job definition.

``` shell
$ directord exec --verb RUN '--skip-cache echo -e "hello world"'
```

Every job can be executed only one time. This is useful when orchestrating
a complex deployment where service setup only needs to be performed once. Use
the `--run-once` flag in your command to ensure it's only executed one time.

``` shell
$ directord exec --verb RUN '--run-once echo -e "hello world"'
```

Every job has the ability to define am execution timeout. The default timeout
is 600 seconds (5 minutes) however, each job can set a timeout to suit it's
specific need. Setting a timeout in the job is does with the `--timeout` switch
which takes a single integer as an argument.

``` shell
$ directord exec --verb RUN '--timeout 1 sleep 10'
```

> The above example with trigger the timeout signal after 1 second of
  execution time.

Components power Directord and provide well documented interfaces.

### Basic Component Options

All component inherit the following basic options.


* `--exec-help`        Show this execution help message.

* `--skip-cache`       For a task to skip the on client cache.

* `--run-once`         Force a given task to run once.

* `--timeout` `STRING` Set the action timeout. Default 600.

* `--force-lock`       Force a given task to run with a lock.

### Built-in Components

The following section covers all of the built-in components Directord ships with.

##### `RUN`

Syntax: `STRING`

Execute a command. The client terminal will execute using `/bin/sh`.

Extra arguments available to the `RUN` component.

* `--stdout-arg` **STRING** Sets the stdout of a given command to defined cached
  argument.

* `--stderr-arg` **STRING** Sets the stderr of a given command to defined cached
  argument.

* `--no-block` When enabled commands are run in a "fire and forget" mode.

##### `ARG`

Syntax: `KEY VALUE`

Sets a cached item within the argument system, which allows for the brace
expansion of items within a command or through the blueprint interface.

> Argument values are cached for 12 hours.

##### `ENV`

Syntax: `KEY VALUE`

Sets a cached item within the environment system used to augment command
line execution.

> Environmental values are cached for 12 hours.

##### `ADD`

syntax: `SOURCE DESTINATION`

Copy a file or glob of files to a remote system. This method allows
operators to define multiple files on the CLI using the specific file, or a
glob of files within a given path.

> When copying multiple files, ensure that the destination path ends with an
  operating system separator.

Extra arguments available to the `ADD` component.

* `--chown` **user[:group]** - Sets the ownership of a recently transferred file to
  a defined user and group (optionally).

* `--chmod` **OCTAL_STRING** - Set the permissions (mode) of the transferred file.
  Permissions need to be written in octal form as a string: e.g. "0755", "2644",
  etc.

* `--blueprint` The blueprint option instructs the client to read and render
  a copied file. The file will be rendered using cached arguments.

> When a copy command has a brace expanded path, the value must be quoted:
  `example/path "/example/{{ target }}/path"`. The quotes around the brace
  exampled target path ensure that the string is preserved by the parser and
  is passed, as is, to the execution engine.

##### `COPY`

The same as `ADD`.

##### `WORKDIR`

Syntax: `STRING`

Extra arguments available to the `WORKDIR` component.

* `--chown` **user[:group]** - Sets the ownership of a recently transferred file to
  a defined user and group (optionally).

* `--chmod` **OCTAL_STRING** - Set the permissions (mode) of the transferred file.
  Permissions need to be written in octal form as a string: e.g. "0755", "2644",
  etc.

Create a directory on the client system.

##### `CACHEFILE`

Syntax: `STRING`

Read a **JSON** or **YAML** file on the client side and load the contents into
argument cache. While cached arguments can easily be defined using the `ARG` or
`ENV` component, the `CACHEFILE` component provides a way to load thousands of
arguments using a single action.

> A cache file allows Directord to rapidly ingest large sets of arguments which
  can later be used in blueprints or dynamic commands.

##### `CACHEEVICT`

Syntax: `STRING`

Evicts all cached items from a given tag. Built-in tags are: **jobs**,
**parents**, **args**, **envs**, **query**, **all**.

While all cached items have a TTL of 12 hours, this method is useful to purge
items on demand.

> The "all" keyword will evict all items from the cache.

##### `QUERY`

Syntax: `STRING`

Scan the environment for a given cached argument and store the resultant on
the target. The resultant is set in dictionary format:

``` json
{
  "query": {
    "query_identity_0": {
      "query_arg3": "query_value"
    },
    "query_identity_1": {
      "query_arg0": "query_value",
      "query_arg1": "query_value"
    },
    "query_identity_2": {
      "query_arg1": "query_value",
      "query_arg2": "query_value",
      "query_arg3": "query_value"
    }
  }
}
```

> The query cache is accumulative, and will always store items under the host
  in which the value originated.

Note that the key `query` stores all of the queried values for a given item
from across the cluster. This provides the ability to store multiple items
and intelligently parse/blueprint data based on node memberships.

> The `QUERY` will spawn a new async `ARG` task which will store the returned
  values across the orchestration targets.

##### `QUEUESENTINAL`

Evicts all items from all worker queues. This component is useful to halt all further
execution on a given target.

### Contributed Components

The following section covers all of the contributed components Directord ships with.

> Contributed components are not fully integrated and may lack testing, but
  otherwise are supported within Directord.

##### `POD`

This features allows operators to run, manage, or manipulate pods across a
Directord cluster.

> At this time pod management requires **podman**.

* `--env` **KEY=VALUE** Comma separated environment variables. KEY=VALUE,...
* `--command` **COMMAND** Run a command in an exec container.
* `--privileged` Access a container with privleges.
* `--tls-verify` Verify certificates when pulling container images.
* `--force` When running removal operations, Enable or Disable force.
* `--kill-signal`  **SIGNAL** Set the kill signal. Default: SIGKILL
* `--start` **POD_NAME** Start a pod.
* `--stop` **POD_NAME** Stop a pod.
* `--rm` **POD_NAME** Remove a pod.
* `--kill` **POD_NAME** Kill a pod.
* `--inspect` **POD_NAME** Inspect a pod.
* `--play` **POD_FILE** Play a pod from a structured file.
* `--exec-run` **CONTAINER_NAME** Container name or ID to use for an execution container.

> When installing Directord with `pip`, the dev optional packages are
  needed on the client side to manage pods; `pip install directord[dev]`.

> Client side **podman** needs to be setup to enable the socket API. The
  orchestration [podman.yaml](https://github.com/directord/directord/blob/main/orchestrations/podman.yaml)
  can be used to automate the **podman** installation and setup process.

##### `SECONTEXT`

Syntax: `STRING`

> Sets SELinux context for a given target.

* `--ftype` **STRING** The contexts type.
* `--reload` **BOOLEAN** Reload policy after commit.
* `--selevel` **STRING** Selinux level.
* `--setype` **STRING** Selinux type.
* `--seuser` **STRING** Selinux user.

##### `DNF`

Syntax: `PACKAGE [PACKAGE ...]`

> Install/Update/Remove packages using dnf.

* `--clear-metadata` **BOOLEAN** Clear dnf metadata and build cache before running install.
* `--exclude` **STRING** Comma separated list for excluding packages.
* `--latest` **BOOLEAN** Ensure latest package is installed.
* `--absent` **BOOLEAN** Remove package.

> NOTE: Installation assumes metadata cache is available.  Use --clear-metadata
  to ensure it's available at least once during an orchestration.

##### `SERVICE`

Syntax: `SERVICE [SERVICE ...]`

> Manage systemd service state

* `--reloaded ` **BOOLEAN** Ensure service is reloaded.
* `--restarted` **BOOLEAN** Ensure service is restarted.
* `--stopped` **BOOLEAN** Ensure service is stopped.
* `--enable` **BOOLEAN** Ensure service is enabled.
* `--disable` **BOOLEAN** Ensure service is disabled.

> NOTE: If no options are provided, a service will be started only.

##### `REBOOT`

Syntax: `INTEGER`

Reboot takes an integer value which is interpreted as seconds before executing
a reboot.

> The default reboot wait time is 10 seconds.

> Reboot operations are performed with `systemctl` on the client side. If the remote
  system does not support this method, additional operations can be performed using
  the `RUN` component in non-blocking mode.

##### `QUERY_WAIT`

Syntax: `STRING`

Block client task execution until a specific item is present in the remote query cache.

* `--query-timeout` **INTEGER** Wait time for an item to be present in the query cache.

* `--identity` **STRING** sets a specific identity when searching for cache entries.
  This can be used multiple times.

> The lookup will search for a **KEY** within the query cache using the input string by
  flattening the identity cache blobs.

> While blocking, the loop will wait 1 second between check intervals.

##### `JOB_WAIT`

Syntax: `STRING`

Block client task execution until a specific job has entered a completed state.

* `--job-timeout` **INTEGER** Wait time for an item to be present in the query cache.

> `JOB_WAIT` requires the job SHA to block. This is most useful for component developers
  using callback jobs.

##### `WAIT`

Syntax: `[CMD ...]`

Conditional wait based on time, url, or command

* `--seconds` **INTEGER** Wait for the provided seconds.
* `--url` **STRING** URL to fetch and check for a 2xx or 3xx response.
* `--cmd` **STRING** Run the provided command string and check success.
* `--retry` **INTEGER** Number of retries on failure. Default: 30
* `--retry-wait` **INTEGER** Number of seconds to wait before retrying. Default: 1
* `--insecure` **BOOLEAN** Allow insecure service connections when using SSL (works only with --url).

> The options `--seconds`, `--url`, and `--cmd` are mutually exclusive and one of
  the options must be provided.  When `--cmd` is specified any additional that are
  not specifically parameters are assumes to be a command to run similar to the RUN
  component.

##### `CONTAINER_IMAGE`

Syntax: `STRING`

Executes basic container image commands - pull, push, list, inspect, tag.

* `--push` **STRING** Image or list of images to push.
* `--pull` **STRING** Image or list of images to pull.
* `--list` **BOOLEAN** List all images on the host.
* `--tag` **STRING** Retag image from/to, requires two images as input.
* `--inspect` **STRING** Image or list of images to inspect.

> The options `--push`, `--pull`, `--list`, `--inspect` and `--tag` are
  mutually exclusive and one of the options must be provided.

##### `FACTER`

Syntax: `STRING`

Runs `facter` on the target and saves result to cache.

* `--custom-dir` **STRING** A directory to use for custom facts.
* `--external-dir` **STRING** A directory to use for external facts.

### User defined Components

User defined components are expected to be in the
 `/etc/directord/components`, or within the package maintained share
path `share/directord/components`. When running user defined components,
Directord will ship them to target nodes when needed and ensure
remote nodes are up-to-date with the latest version. Because Directord
will automatically handle the transport, developing new components is
simple.

#### Complete User Defined Component Example

An example user defined component is available within the **components**
directory of Directord; [echo component](https://github.com/directord/directord/blob/main/components/echo.py).

##### Minified Example

``` python
from directord import components

from directord.components.lib import cacheargs


class Component(components.ComponentBase):
    def __init__(self):
        super().__init__(desc="Process echo commands")

    def args(self):
        super().args()
        self.parser.add_argument(
            "echo",
            help=("add echo statement for tests and example."),
        )

    def server(self, exec_array, data, arg_vars):
        super().server(exec_array=exec_array, data=data, arg_vars=arg_vars)
        data["echo"] = self.known_args.echo
        return data

    @cacheargs
    def client(self, cache, job):
        print(job["echo"])
        return job["echo"], None, True, None
```

To build a component, only three methods are required. `args`, `server`, `client`.

| Method    | Return                             | Description                                                                   |
| --------- | ---------------------------------- | ----------------------------------------------------------------------------- |
| `args`    | None                               | Defines arguments used within a component. Sets component arguments.          |
| `server`  | Dictionary -> {...}                | Encompasses everything that must be done server side. Returns formatted data. |
| `client`  | Tuple -> (STDOUT, STDERR, OUTCOME) | Encompasses everything that will be done client side. Returns results.        |

Once the user defined component is developed and in-place, it responds just like
a built-in, with all the same syntactic guarantees across executions and
orchestrations.

> The following shell output is from the invocation of the above user-defined
  component, which can also be seen
  [here](https://github.com/directord/directord/blob/main/components/echo.py).


###### Help Information From Components

All components have access to `--exec-help` which will provide information on
specific options a component has.

``` shell
$ directord exec --verb ECHO "--exec-help true"
usage: directord [--exec-help] [--skip-cache] [--run-once] [--timeout TIMEOUT] echo

Process echo commands

positional arguments:
  echo               add echo statement for tests and example.

optional arguments:
  --exec-help        Show this execution help message.
  --skip-cache       For a task to skip the on client cache.
  --run-once         Force a given task to run once.
  --timeout TIMEOUT  Set the action timeout. Default 600.
  --force-lock       Force a given task to run with a lock.
```

###### Executing a User Defined Component

``` shell
$ directord exec --verb ECHO "true"
Job received. Task ID: 09a0d4aa-ff84-40e4-a7e2-88be8dff841a
```

###### Inspecting an Execution

``` shell
$ directord --debug manage --job-info 09a0d4aa-ff84-40e4-a7e2-88be8dff841a
DEBUG Executing Management Command:list-jobs
KEY                   VALUE
--------------------  -------------------------------------------------------
ID                    09a0d4aa-ff84-40e4-a7e2-88be8dff841a
STDOUT                df.next-c0.localdomain = true
VERB                  ECHO
JOB_SHA3_224          86823a46fb4af75c9f93c8bedb301dfa8968321a
JOB_DEFINITION        verb = ECHO
                      echo = true
                      timeout = 600
                      job_sha3_224 = 86823a46fb4af75c9f93c8bedb301dfa8968321a
                      job_id = 09a0d4aa-ff84-40e4-a7e2-88be8dff841a
                      parent_id = 09a0d4aa-ff84-40e4-a7e2-88be8dff841a
PARENT_JOB_ID         09a0d4aa-ff84-40e4-a7e2-88be8dff841a
PROCESSING            False
SUCCESS               df.next-c0.localdomain
EXECUTION_TIME        0.0037195682525634766
ROUNDTRIP_TIME        0.023545026779174805

Total Items: 14
```

The `--job-info` command also accepts special identifiers (`last`), to more
quickly inspect certain executions.

``` shell
$ directord --debug manage --job-info last
```

###### Building an Orchestration

``` yaml
---
- jobs:
  - ECHO: Hello World
```

#### Developing Adapted Components

User defined components can be developed from scratch or through adaptation of
existing solutions. Because the Directord component implementation is so simple,k
it is possible to create new modules from existing solutions, like Ansibe modules
without a lot of effort.

The `ComponentBase` offers an Ansible documentation to Directord argument
conversion method `options_converter`, which will allow developers to create
new Directord components with ease. An example of a converted module can be
seen in the `container_config_data` component and found
[here](https://github.com/directord/directord/blob/main/components/container_config_data.py).

#### Job specification

| Key                   | Value                                 |
| --------------------- | --------------------------------------|
| `${COMPONENT_OPTS}`   | **Component specific options**        |
| `verb`                | **Component verb**                    |
| `timeout`             | **Time value in seconds**             |
| `skip_cache`          | **Boolean, skips local cache checks** |
| `targets`             | **Array of targets**                  |
| `job_id`              | **UUID**                              |
| `job_sha3_224`        | **Job SHA in SHA3 224**               |
| `extend_args`         | **Boolean**                           |
| `parent_async_bypass` | **Boolean**                           |
| `parent_sha3_224`     | **Parent SHA in SHA3 224**            |
| `parent_id`           | **UUID**                              |
