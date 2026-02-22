import json
import os
import sys


def greet(name: str) -> str:
    msg = "Hello, " + name + "!"
    return msg


def load_config(path: str) -> dict:
    with open(path) as f:
        data = json.load(f)
    return data


def main() -> None:
    name = os.environ.get("USER", "world")
    greeting = greet(name)
    print(greeting)

    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    if config_path is not None:
        config = load_config(config_path)
        print(config)


if __name__ == "__main__":
    main()
