#!/usr/bin/env python3
import subprocess
import sys
import shlex
import signal

def handle_notification(notification: dict):
    print(notification)

def run_dbus_monitor():
    cmd = "dbus-monitor \"interface='org.freedesktop.Notifications',member='Notify'\""
    args = shlex.split(cmd)

    try:

        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        counter: int = 0
        in_notification = False
        notification = {
            "app_name": "",
            "summary": "",
            "body": ""
        }
        index = 0
        while True:
            line = process.stdout.readline()
            if not line:
                break

            print(line, end="")

            if "   array [" in line:
                if in_notification:
                    handle_notification(notification)
                    notification = {
                        "app_name": "",
                        "summary": "",
                        "body": ""
                    }
                in_notification = False
                index = 0

            if "interface=org.freedesktop.Notifications; member=Notify" in line:
                in_notification = True
                continue

            if not in_notification:
                continue

            msg = line.replace("   string ", "", 1).strip()
            is_ended = (msg[-1] == '\"')
            s = msg
            if msg[0] == '\"':
                s = s[1:]
            if is_ended:
                s = s[:-1]
            if index == 0:
                notification["app_name"] += s if is_ended else s + '\n'
            elif index == 3:
                notification["summary"] += s if is_ended else s + '\n'
            elif index == 4:
                notification["body"] += s if is_ended else s + '\n'
            if line.startswith("   string "):
                if not is_ended:
                    continue
            index += 1

    except KeyboardInterrupt:
        print("\nShutting down service...")
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait()
        print("dbus-monitor process stopped")


def main():
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    run_dbus_monitor()


if __name__ == "__main__":
    main()
