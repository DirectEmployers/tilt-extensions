import argparse

if __name__ == "__main__":
    from control import remote, serve

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    start_operator = subparsers.add_parser(
        "serve",
        description="Start an async process to maintain the state of Tilt resources.",
        help="Start the extension operator server.",
    )
    start_operator.set_defaults(func=serve)

    boop_event = subparsers.add_parser(
        "remote",
        description="Handle button press events from Tilt and update credentials.",
        help="Handle Tilt UI button events.",
    )
    boop_event.add_argument("keyfile_path", help="Path to Datadog credentials file.")
    boop_event.set_defaults(func=remote)

    parsed = parser.parse_args()

    if parsed.func == remote:
        parsed.func(parsed.keyfile_path)
    else:
        parsed.func()
