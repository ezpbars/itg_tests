import multiprocessing
import updater
import time


def main():
    multiprocessing.Process(target=updater.listen_forever_sync, daemon=True).start()
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
