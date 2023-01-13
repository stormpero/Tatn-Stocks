import os
import sys

from threading import Thread, Event

import pystray
from pystray import Menu, MenuItem as Item
from PIL import Image

from bs4 import BeautifulSoup as bs
import hashlib
import time
from urllib.request import urlopen, Request

url = Request("https://ru.investing.com/equities/tatneft_rts", headers={"User-Agent": "Mozilla/5.0"})


def get_price_from_html(content):
    return bs(content, "html.parser").find('span', {'data-test': "instrument-price-last"}).text


def get_html_hash(url):
    response = urlopen(url).read()
    return hashlib.sha224(response).hexdigest()


def get_curr_time():
    t = time.localtime()
    return time.strftime("%H:%M:%S", t)


exit = Event()


def loop(icon):
    prev_hash = get_html_hash(url)
    while not exit.is_set():
        try:
            new_hash = get_html_hash(url)
            if new_hash != prev_hash:
                response = urlopen(url).read()
                price = get_price_from_html(response)
                icon.title = str(f" {price} р.\n {get_curr_time()}")
                prev_hash = new_hash
                print(price)
            exit.wait(15)
        except Exception as e:
            print("error")


def action_exit(icon):
    icon.stop()
    exit.set()
    thread.join()


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


if __name__ == '__main__':
    response = urlopen(url).read()
    price = get_price_from_html(response)

    icon = pystray.Icon("TATN", Image.open(resource_path("TATN.ico")),
                        menu=Menu(Item('Выход', action_exit)),
                        title=str(f" {price} р.\n {get_curr_time()}"))

    thread = Thread(target=loop, args=[icon])
    thread.start()
    icon.run()
