import os

from clixon.args import parse_args
from clixon.client import create_socket, read, send
from clixon.log import get_logger
from clixon.netconf import rpc_commit, rpc_config_get, rpc_config_set
from clixon.parser import parse_string

logger = get_logger()
sockpath, _, _, _, _, pp = parse_args()


class Clixon():
    def __init__(self, sockpath="/usr/local/var/controller.sock",
                 commit=False):
        if sockpath == "" or not os.path.exists(sockpath):
            raise ValueError(f"Invalid socket: {sockpath}")

        self.__socket = create_socket(sockpath)
        self.__commit = commit

        send(self.__socket, rpc_config_get(), pp)
        data = read(self.__socket, pp)

        self.__root = parse_string(data).rpc_reply.data

    def __enter__(self):
        return self.__root

    def __exit__(self, *args):
        for device in self.__root.devices.get_elements():
            config = rpc_config_set(device, device=True)

            # if self.__root.get_elements("services") != []:
            #    config.rpc.edit_config.config.add(self.__root.services)

            send(self.__socket, config, pp)
            read(self.__socket, pp)

            if self.__commit:
                self.commit()

    def commit(self):
        commit = rpc_commit()
        send(self.__socket, commit, pp)
        read(self.__socket, pp)

    def get_root(self):
        return self.__root

    def set_root(self, root):
        send(self.__socket, root, pp)
        read(self.__socket, pp)

        if self.__commit:
            self.commit()


def rpc(sockpath=sockpath, commit=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            with Clixon(sockpath, commit=commit) as root:
                return func(root, logger)
        return wrapper
    return decorator
