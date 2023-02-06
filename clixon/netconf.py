from enum import Enum

from clixon.element import Element
from clixon.parser import parse_string


class RPCTypes(Enum):
    GET_CONFIG = 0
    EDIT_CONFIG = 1
    COMMIT = 2


class RPCError(Exception):
    pass


def rpc_config_get(user="root"):
    attributes = {
        "nc:type": "xpath",
        "nc:select": "/"
    }

    root = rpc_header_get(RPCTypes.GET_CONFIG, user)
    root.rpc.get_config.create("source")
    root.rpc.get_config.source.create("candidate")
    root.rpc.get_config.create("nc:filter", attributes=attributes)

    return root


def rpc_config_set(config, user="root"):
    root = rpc_header_get(RPCTypes.EDIT_CONFIG, user)
    root.rpc.edit_config.create("target")
    root.rpc.edit_config.target.create("candidate")
    root.rpc.edit_config.create("default-operation")
    root.rpc.edit_config.default_operation.cdata = "replace"
    root.rpc.edit_config.create("config")

    for node in config.get_elements():
        root.rpc.edit_config.config.add(node)

    return root


def rpc_commit(user="root"):
    return rpc_header_get(RPCTypes.COMMIT, user)


def rpc_header_get(rpc_type, user, attributes=None):
    if attributes is None:
        attributes = {
            "xmlns": "urn:ietf:params:xml:ns:netconf:base:1.0",
            "username": user,
            "xmlns:nc": "urn:ietf:params:xml:ns:netconf:base:1.0",
            "message-id": 42
        }

    root = Element("root", {})
    root.create("rpc", attributes=attributes)

    if rpc_type == RPCTypes.GET_CONFIG:
        root.rpc.create("get-config")
    elif rpc_type == RPCTypes.EDIT_CONFIG:
        root.rpc.create("edit-config")
    elif rpc_type == RPCTypes.COMMIT:
        root.rpc.create("commit")

    return root


def rpc_subscription_create():
    attributes = {
        "xmlns": "urn:ietf:params:xml:ns:netmod:notification"
    }

    rpcattrs = {
        "xmlns": "urn:ietf:params:xml:ns:netconf:base:1.0",
        "message-id": "42"
    }

    root = rpc_header_get("", "root", rpcattrs)
    root.rpc.create("create-subscription", attributes=attributes)
    root.rpc.create_subscription.create("stream")
    root.rpc.create_subscription.stream.cdata = "controller"
    root.rpc.create_subscription.create(
        "filter", {"type": "xpath", "select": ""})

    return root


def rpc_error_get(xmlstr):
    root = parse_string(xmlstr)
    try:
        raise RPCError(root.rpc_reply.rpc_error.error_message)
    except AttributeError:
        return None