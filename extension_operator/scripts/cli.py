import argparse
import asyncio

from ext_operator import ExtensionOperator
from tilt.utils import get_or_create_extension_operator


def serve():
    optr = ExtensionOperator()
    asyncio.run(optr.run())


def remote():
    optr_ui = get_or_create_extension_operator()

    if not optr_ui.is_enabled:
        optr_ui.enable(wait=True)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    start_operator = subparsers.add_parser("serve")
    start_operator.set_defaults(func=serve)

    boop_event = subparsers.add_parser("remote")
    boop_event.set_defaults(func=remote)

    args = parser.parse_args()
    args.func()
