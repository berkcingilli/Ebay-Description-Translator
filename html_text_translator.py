from bs4 import BeautifulSoup
from bs4.element import Comment
import time
import asyncio
import sys, os
import requests
from itertools import cycle
import re
from deep_translator import GoogleTranslator
from csv import reader
import random

start_time = time.time()

CSV_FILE_PATH = "C:/Users/----/----/example.csv"

# Do not remove /{0}, leave it end of the path
OUTPUT_DIRECTORY_PATH = "C:/Users/----/----/example/{0}"

LANGUAGES = ['de', 'fr', 'it', 'es']

PROXY_LIST = []

ITEM_NUMBERS = []

tasks = []

exceptions = []

proxy_pool = []


async def refresh_proxy_list():
    print('refresh_proxy_list ENTERED')
    PROXY_LIST.clear()

    try:

        PROXY_LIST.append(requests.get("https://www.proxy-list.download/api/v1/get?type=https").content)
        PROXY_LIST.append(requests.get(
            "https://api.proxyscrape.com/?request=displayproxies&proxytype=http&timeout=9000&ssl=yes").content)
        PROXY_LIST.append(requests.get(
            "http://pubproxy.com/api/proxy?limit=20&format=txt&https=true&level=elite&country=DE,FR,IT,ES,BE,NL").content)

    except Exception as e:
        exceptions.append(e)
        print("EXCEPTION : def refresh_proxy_list()", e)

    # Regular Expression to extract IP address
    FIXED_PROXY_LIST = re.findall(r'[0-9]+(?:\.[0-9]+){3}:[0-9]+', str(PROXY_LIST))
    print('here', FIXED_PROXY_LIST)

    # PROXY POOL
    global proxy_pool
    proxy_pool = cycle(FIXED_PROXY_LIST)


async def get_ebay_item_description(item_number):
    print('get_ebay_item_description ENTERED   ', item_number)

    try:
        temp_ebay_url = 'https://www.ebay.co.uk/itm/{0}'.format(item_number)
        proxy = next(proxy_pool)
        req = requests.get(temp_ebay_url, proxies={'http': proxy})
        await asyncio.sleep(random.randint(0, 3))
        soup = BeautifulSoup(req.content, 'html.parser')
        iframe_src = soup.find("iframe", id="desc_ifr")
        iframe_req = requests.get(iframe_src['src'], proxies={'http': proxy})
        final_soup = BeautifulSoup(iframe_req.content, 'html.parser')
        return final_soup

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("def get_ebay_item_description()  ", exc_type, fname, exc_tb.tb_lineno, e)
        exceptions.append(e)
        await refresh_proxy_list()


async def read_translate_write_html(language, item_number):
    print('read_translate_write_html ENTERED    ', language, item_number)

    soup = await get_ebay_item_description(item_number)

    # Check if ebay description page is retrieved without problem.
    try:
        texts = soup.findAll(text=True)
    except Exception as e:
        with open(OUTPUT_DIRECTORY_PATH.format("PROBLEM_ITEMNUBER" + language + item_number), "w",
                  encoding="UTF-8") as file:
            file.write(str(soup))
            exceptions.append(e)
            return

    # Loop for visible texts in ebay description template
    for elem in texts:
        # Add an if conditional if you want to skip some specific text for translation.
        if elem.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            continue
        elif isinstance(elem, Comment):
            continue
        else:
            if len(elem.strip()) != 1 and len(elem.strip()) != 0 and str(
                    elem.strip()).isdecimal() != True and not re.match(r'^[_\W]+$', str(elem.strip())):
                try:
                    proxy = next(proxy_pool)
                    print('READ TRANSLATE WRITE ', language, proxy, item_number)

                    print(elem.strip(), type(elem.strip()))

                    translated_string = GoogleTranslator(source='auto', target=language,
                                                         proxies={'http': proxy}).translate(str(elem.strip()))
                    await asyncio.sleep(random.randint(0, 3))

                    # IF GOOGLE RETURNS 2 RESULTS
                    if isinstance(translated_string, list):
                        translated_string = translated_string[0]

                    # Replace the visible text with it's translation
                    fixed_text = elem.replace(str(elem.strip()), translated_string)
                    print(fixed_text)
                    elem.replace_with(fixed_text)
                except Exception as e:

                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print("def read_translate_write_html()  ", exc_type, fname, exc_tb.tb_lineno, e, item_number)
                    exceptions.append(e)
                    # Create Problem HTML
                    with open(OUTPUT_DIRECTORY_PATH.format("PROBLEM_TRANSLATE" + language + item_number), "w",
                              encoding="UTF-8") as file:
                        file.write(str(soup))
                    await refresh_proxy_list()

    # Create final html and call for new proxy
    with open(OUTPUT_DIRECTORY_PATH.format(language + item_number + ".html"), "w", encoding="UTF-8") as file:
        file.write(str(soup))


async def read_translate_write_html_sem(sem, language, item_number):
    async with sem:
        await read_translate_write_html(language, item_number)


async def main():
    # GET PROXIES
    await refresh_proxy_list()

    # OPEN FILE AND STORE EACH ITEM TO LIST
    with open(CSV_FILE_PATH, 'r',
              encoding='utf-8-sig') as read_obj:
        csv_reader = reader(read_obj)
        for row in csv_reader:
            ITEM_NUMBERS.append(str(row[0]))

    print(ITEM_NUMBERS)
    print(len(ITEM_NUMBERS))

    # Number of Semaphores (number of threads when running all the tasks)
    sem = asyncio.Semaphore(20)
    # LOOP EACH ITEM
    for item_number in ITEM_NUMBERS:
        try:
            # CREATE TASKS WITH DIFFERENT PROXIES AND LANGUAGES FOR EACH HTML
            for i in LANGUAGES:
                proxy = next(proxy_pool)
                print(item_number + "   " + i + "   " + proxy)
                tasks.append(asyncio.create_task(read_translate_write_html_sem(sem, i, item_number)))

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("def main()  ", exc_type, fname, exc_tb.tb_lineno, e)
            exceptions.append(e)

    # Print all the tasks
    print(tasks)
    # Gather all the tasks
    await asyncio.gather(*tasks)


asyncio.run(main())

print("Exceptions :  ", exceptions)
print("------- {0} minutes ------".format((time.time() - start_time) / 60))
