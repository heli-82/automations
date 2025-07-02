import os
import tomli
import datetime
from termcolor import colored
import sys

def _dumps_value(value)->str:
    if isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, list):
        return f"[{', '.join(_dumps_value(v) for v in value)}]"
    else:
        raise TypeError(f"{type(value).__name__} {value!r} is not supported")


def dump(toml_dict: dict, table="")->str:
    def tables_at_end(item):
        _, value = item
        return isinstance(value, dict)

    toml = []
    for key, value in sorted(toml_dict.items(), key=tables_at_end):
        if isinstance(value, dict):
            table_key = f"{table}.{key}" if table else key
            toml.append(f"\n[{table_key}]\n{dump(value, table_key)}")
        else:
            toml.append(f"{key} = {_dumps_value(value)}")
    return "\n".join(toml)


DEFAULT_CONFIG = {
    "time_to_delete": {
        "days":45.0
    },
    "directories": ["C:/Downloads" if sys.platform == "win32" else "~/Downloads"]
}

def get_empty_dirs(start_path='.')->list[str]:
    d = []
    for root, dirs, files in os.walk(start_path):
        for di in dirs:
            if len(os.listdir(os.path.join(root, di)))==0:
                d.append(os.path.join(root, di))
    return d

def get_files_walk(start_path='.')->list[str]:
    d = []
    for root, dirs, files in os.walk(start_path):
        for file in files:
            d.append(os.path.join(root, file))
    return d

def main():
    config = DEFAULT_CONFIG.copy()

    if os.path.exists("config.toml"):
        with open("config.toml", mode="rb") as file:
            config = tomli.load(file)
    else:
        cfg = dump(config)
        with open("config.toml", mode="w+") as file:
            file.write(cfg)
    
    dir_contents = []
    for d in config["directories"]:
        if d[0]=='~': d = d.replace('~', os.path.expanduser('~'), 1)
        if "$HOME" in d: d = d.replace("$HOME", os.path.expanduser("$HOME"), 1)
        dir_contents.extend(get_files_walk(d))
    dir_contents.sort(key=lambda path: os.path.getmtime(path))
    
    for file in dir_contents:
        if datetime.datetime.fromtimestamp(os.path.getmtime(file)) < datetime.datetime.now()-datetime.timedelta(days=config["time_to_delete"]["days"]):
            print(f"{file}", colored(datetime.datetime.fromtimestamp(os.path.getmtime(file)), "blue"))
    print(f"You want to {colored("delete","red")} these files? [{colored("y", "green")}/{colored("N", "red")}]")
    
    ans = input()
    if ans=='Y' or ans=='y':
        for file in dir_contents:
            if datetime.datetime.fromtimestamp(os.path.getmtime(file)) < datetime.datetime.now()-datetime.timedelta(days=config["time_to_delete"]["days"]):
                os.remove(file)
        for directory in config["directories"]:
            if directory[0]=='~': directory = directory.replace('~', os.path.expanduser('~'), 1)
            if "$HOME" in directory: directory = directory.replace("$HOME", os.path.expanduser("$HOME"), 1)
            dirs = get_empty_dirs(directory)
            while len(dirs)>0:
                for d in dirs:
                    os.rmdir(d)
                dirs = get_empty_dirs(directory)
    else:
        print(f"Goodbye, be {colored("careful", "blue")}.")

if __name__=="__main__":
    main()