from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from chromedriver_py import binary_path
import os.path, json

from store_order import *
from load_config import *
from send_notification import *


chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(executable_path=binary_path, options=chrome_options)
driver.get("https://www.binance.com/en/support/announcement/c-48")


def get_last_coin():
    """
    Scrapes new listings page for and returns new Symbol when appropriate
    """
    latest_announcement = driver.find_element(By.ID, 'link-0-0-p1')
    latest_announcement = latest_announcement.text

    # Binance makes several annoucements, irrevelant ones will be ignored
    exclusions = ['Futures', 'Margin', 'adds']
    for item in exclusions:
        if item in latest_announcement:
            return None
    enum = [item for item in enumerate(latest_announcement)]
    #Identify symbols in a string by using this janky, yet functional line
    uppers = ''.join(item[1] for item in enum if item[1].isupper() and (enum[enum.index(item)+1][1].isupper() or enum[enum.index(item)+1][1]==' ' or enum[enum.index(item)+1][1]==')') )

    return uppers


def store_new_listing(listing):
    """
    Only store a new listing if different from existing value
    """

    if os.path.isfile('new_listing.json'):
        file = load_order('new_listing.json')
        if listing in file:
            print("No new listings detected...")

            return file
        else:
            file = listing
            store_order('new_listing.json', file)
            #print("New listing detected, updating file")
            send_notification(listing)
            return file

    else:
        new_listing = store_order('new_listing.json', listing)
        send_notification(listing)
        #print("File does not exist, creating file")

        return new_listing


def search_and_update():
    """
    Pretty much our main func
    """
    while True:
        latest_coin = get_last_coin()
        if latest_coin:
            store_new_listing(latest_coin)
        else:
            pass
        print("Checking for coin announcements every 2 hours (in a separate thread)")
        return latest_coin
        time.sleep(60*180)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from chromedriver_py import binary_path
import os
import json
import time

from store_order import *
from load_config import *
from send_notification import *

chrome_options = Options()
chrome_options.add_argument("--headless")  # Headless-Modus für Hintergrundausführung
driver = webdriver.Chrome(executable_path=binary_path, options=chrome_options)
driver.get("https://www.binance.com/en/support/announcement/c-48")


def get_last_coin():
    """
    Scrapes the Binance new listings page and returns the symbol and name if a new coin is detected.
    """
    try:
        # Finde die neuesten Ankündigungen
        announcements = driver.find_elements(By.CLASS_NAME, 'css-1ej4hfo')  # Klasse anpassen

        for announcement in announcements:
            text = announcement.text

            # Überprüfen, ob der Marker "Binance Will List" vorhanden ist
            if "Binance Will List" in text:
                # Suche nach Symbolen in Klammern, z. B. (ACX) oder (ORCA)
                symbols = []
                start = text.find("Binance Will List") + len("Binance Will List")
                parts = text[start:].split("and")  # Teile den Text bei "and" für mehrere Coins
                for part in parts:
                    if '(' in part and ')' in part:
                        symbol_start = part.index('(') + 1
                        symbol_end = part.index(')')
                        symbols.append(part[symbol_start:symbol_end].strip())
                return text, symbols

        return None, None
    except Exception as e:
        print(f"Error during scraping: {e}")
        return None, None


def store_new_listing(listing, symbols):
    """
    Stores a new listing if it doesn't already exist.
    """
    if os.path.isfile('new_listing.json'):
        file = load_order('new_listing.json')
        new_symbols = [symbol for symbol in symbols if symbol not in file]
        if not new_symbols:
            print("No new listings detected...")
            return file
        else:
            for symbol in new_symbols:
                file[symbol] = listing
            store_order('new_listing.json', file)
            send_notification(f"New listings detected: {', '.join(new_symbols)}")
            return file
    else:
        new_listing = {symbol: listing for symbol in symbols}
        store_order('new_listing.json', new_listing)
        send_notification(f"New listings detected: {', '.join(symbols)}")
        return new_listing


def search_and_update():
    """
    Main function to periodically check for new coin listings.
    """
    while True:
        latest_listing, latest_symbols = get_last_coin()
        if latest_symbols:
            store_new_listing(latest_listing, latest_symbols)
        else:
            print("No new coin listings found...")

        print("Checking for coin announcements every 2 hours.")
        time.sleep(60 * 120)  # 2 Stunden warten


if __name__ == "__main__":
    search_and_update()
