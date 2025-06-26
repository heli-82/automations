#!/usr/bin/env python3
import subprocess
import sys
import shlex
import signal


def run_dbus_monitor():
    """Запускает dbus-monitor и выводит его вывод в реальном времени"""
    # Формируем команду для мониторинга уведомлений
    cmd = "dbus-monitor \"interface='org.freedesktop.Notifications',member='Notify'\""
    args = shlex.split(cmd)

    print(f"Запускаем команду: {' '.join(args)}")
    print("Ожидание уведомлений... Нажмите Ctrl+C для выхода")
    print("Отправьте тестовое уведомление командой: notify-send 'Тест' 'Привет, мир!'")

    try:
        # Запускаем процесс
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # объединяем stderr с stdout
            text=True,
            bufsize=1,  # построчная буферизация
            universal_newlines=True
        )

        # Читаем вывод построчно
        counter: int = 0
        in_array = False
        while True:
            line = process.stdout.readline()
            if not line:
                break
            if "array [" in line:
                in_array = True
            print(f"{counter}: {line}", end='')
            counter += 1

    except KeyboardInterrupt:
        print("\nЗавершение работы по запросу пользователя...")
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait()
        print("Процесс dbus-monitor завершен")


def main():
    # Обработка Ctrl+C
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))

    print("=== Простой монитор D-Bus уведомлений ===")
    run_dbus_monitor()


if __name__ == "__main__":
    main()
