import argparse

if __name__ == "__main__":
    from control import remote, serve

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    start_operator = subparsers.add_parser("serve")
    start_operator.set_defaults(func=serve)

    boop_event = subparsers.add_parser("remote")
    boop_event.set_defaults(func=remote)

    args = parser.parse_args()
    args.func()
