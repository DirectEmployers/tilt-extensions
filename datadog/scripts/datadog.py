import argparse
import asyncio

from tilt import tilt_enable

from control import ExtensionOperator


def serve():
    operator = ExtensionOperator()
    asyncio.run(operator.run())


def remote():
    operator = ExtensionOperator()
    if op_port := operator.get_operator():
        tilt_enable("datadog-operator", port=op_port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    start_operator = subparsers.add_parser("serve")
    start_operator.set_defaults(func=serve)

    boop_event = subparsers.add_parser("remote")
    boop_event.set_defaults(func=remote)

    args = parser.parse_args()
    args.func()
