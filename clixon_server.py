#!/usr/bin/env python3
import os
import sys
import threading
import time

from daemonize import Daemonize

from clixon.args import parse_args
from clixon.client import readloop
from clixon.log import get_logger
from clixon.modules import load_modules

sockpath, modulespath, modulefilter, pidfile, foreground, pp, log = parse_args()
logger = get_logger(output=log)
lockfd = None


def main() -> None:
    """
    Main function for clixon_server.
    """

    modules = load_modules(modulespath, modulefilter)

    if modules == []:
        logger.error("No loadable modules found.")
        sys.exit(0)

    threads = []
    threads.append(threading.Thread(
        target=readloop, args=(sockpath, modules, pp)))

    try:
        for thread in threads:
            thread.daemon = True
            thread.start()

        while True:
            time.sleep(5)
    except IOError as e:
        logger.error(f"IO error: {e}")
    except Exception as e:
        logger.error(e)
    except KeyboardInterrupt:
        logger.info("\nGoodbye.")


if __name__ == "__main__":

    daemon = Daemonize(app="clixon_server", pid=pidfile, action=main,
                       logger=logger,
                       foreground=foreground,
                       verbose=True,
                       chdir=os.getcwd())
    daemon.start()
