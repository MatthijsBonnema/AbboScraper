from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from re import sub
from time import sleep
import ftplib
import time


def waitForCSS(driver, data, seconds):
    """
    This function looks for the provided CSS Selector and returns the element.
    :param driver: The selenium webdriver
    :param data: What CSS Selector has to be searched
    :param seconds: How many seconds should be waited before raising an error.
    :return: The element that was found.
    """
    element = WebDriverWait(driver, seconds).until(EC.element_to_be_clickable((By.CSS_SELECTOR, data)))
    return element


def cookie_clicker(driver, link):
    pageNotLoaded = True
    while pageNotLoaded:
        try:
            waitForCSS(driver, "a.cookie-info-accept-button", 10)
            pageNotLoaded = False
        except TimeoutException:
            driver.get(link)
    element = driver.find_element_by_class_name("cookie-info-accept-button")
    element.click()

def get_phones():
    page = 1
    link = "https://telefoonabonnementen.mediamarkt.nl/smartphone-plus-abonnement/merk/samsung?sort=popular&p={}".format(
        page)
    driver = webdriver.Chrome('chromedriver.exe')
    driver.maximize_window()

    phones = []

    pages = True

    driver.get(link)

    cookie_clicker(driver, link)

    while pages:
        if page != 1:
            driver.get(link)

        phones_list = driver.find_elements_by_class_name("article-container")

        print(len(phones_list))
        if len(phones_list) == 0:
            pages = False
            break

        for phone in driver.find_elements_by_class_name("article-container"):
            buttons = phone.find_elements_by_class_name("button")
            for button in buttons:
                phoneLink = button.get_attribute("href")
                phones.append(phoneLink)

        page += 1
        link = "https://telefoonabonnementen.mediamarkt.nl/smartphone-plus-abonnement/merk/samsung?sort=popular&p={}".format(
            page)

    driver.close()
    return phones

def get_phone_info(link):
    driver = webdriver.Chrome('chromedriver.exe')
    driver.maximize_window()
    driver.get(link)

    cookie_clicker(driver, link)
    sleep(0.2)
    phone_name = driver.find_element_by_class_name("fullwidth").get_attribute("innerHTML").replace('<span class="fw-bold">GSM</span><br>', '').strip()
    phone_dict = {"name": phone_name}

    providers = driver.find_elements_by_class_name("provider-border")
    for provider in providers:
        if provider.text == "Advies":
            break
        provider_name = provider.get_attribute("title")
        provider.click()
        sleep(0.3)
        try:
            total_credit = driver.find_element_by_class_name("credit-table-totalvalue").text.strip("€").strip(",-")
        except NoSuchElementException:
            total_credit = "0"
            pass
        phone_dict["{}".format(provider_name)] = total_credit
        print(provider_name, total_credit)
    driver.close()
    return phone_dict


def create_page(phones_info):
    table_start = open("table.html", 'r')
    result = open("Samsung.html", 'w')
    now = time.strftime("%c")
    result.write("Voor het laatst aangepast op: %s<p>" % now)

    for line in table_start:
         result.write(line)

    table_start.close()

    phone_nr = 1

    phones_info =  sorted(phones_info, key=lambda k: k['name'], reverse=True)

    for phone in phones_info:
        if phone_nr % 2 == 0:
            table_class = "tg-even"
        else:
            table_class = "tg-odd"
        result.write("    <tr>\n")
        result.write('        <td class="{}">{}</td>\n'.format(table_class, phone['name']))
        result.write('        <td class="{}">&euro; {}</td>\n'.format(table_class, phone['Vodafone']))
        result.write('        <td class="{}">&euro; {}</td>\n'.format(table_class, phone['T-Mobile']))
        result.write('        <td class="{}">&euro; {}</td>\n'.format(table_class, phone['Tele2']))
        result.write('        <td class="{}">&euro; {}</td>\n'.format(table_class, phone['KPN']))
        result.write('        <td class="{}">&euro; {}</td>\n'.format(table_class, phone['Telfort']))
        result.write('        <td class="{}">&euro; {}</td>\n'.format(table_class, phone['Hollandsnieuwe']))
        result.write('        <td class="{}">&euro; {}</td>\n'.format(table_class, phone['Lebara']))
        result.write("    </tr>\n")

        phone_nr += 1

    result.write("</table>\n")

def upload_page(filename):
    session = ftplib.FTP('abbo.msbonnema.nl', 'default_ftp', 'VchL7X_Uyh')
    file = open(filename, 'rb')
    session.cwd('web')
    session.storbinary('STOR Samsung.html', file)
    file.close()
    session.quit()

if __name__ == '__main__':

    # phones = get_phones()
    # phones = ['https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-s9/zwart/abonnement?articles=405%2B483%2B3519', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-s9-plus/zwart/abonnement?articles=405%2B487%2B3519', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-note9-128gb/zwart/abonnement?articles=405%2B495%2B3519', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-s8/zwart/abonnement?articles=405%2B477%2B3519', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-a6-2018/paars/abonnement?articles=2800%2B2807%2B2849', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-a8-dual-sim/zwart/abonnement?articles=405%2B472%2B3519', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-a7/blauw/abonnement?articles=405%2B471%2B3519', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-a6-plus-2018/paars/abonnement?articles=405%2B471%2B3519', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-j6-2018/goud/abonnement?articles=2800%2B2807%2B2839', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-a5-2017/zwart/abonnement?articles=2800%2B2807%2B2845', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-s7/zwart/abonnement?articles=2800%2B2807%2B2867', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-j3-2017/zwart/abonnement?articles=2800%2B2807%2B2837', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-note9-512gb/abonnement?articles=405%2B498%2B3519', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-j4-plus/goud/abonnement?articles=405%2B467%2B3519', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-j5-2017/goud/abonnement?articles=1658%2B3458', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-s9-plus-256gb/abonnement?articles=405%2B493%2B3519', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-j6-plus/grijs/abonnement?articles=2800%2B2807%2B2845', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-j7-2017/zwart/abonnement?articles=2800%2B2807%2B2843', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-s9-256gb/abonnement?articles=405%2B490%2B3519', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-xcover-4/abonnement?articles=2800%2B2807%2B2843', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-j3/goud/abonnement?articles=2800%2B2833%2B3776', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-note8/zwart/abonnement?articles=405%2B488%2B3519', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-s8-plus/zwart/abonnement?articles=405%2B484%2B3519', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-a3-2017/zwart/abonnement?articles=2800%2B2807%2B2853', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-a9/blauw/abonnement?articles=1506%2B3383%2B3394', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-s7-edge/blauw/abonnement?articles=405%2B478%2B3519', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-a3-2016/goud/abonnement?articles=405%2B469%2B3519', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-j7-2016/goud/abonnement?articles=405%2B472%2B3519', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-s6-32gb/goud/abonnement?articles=405%2B473%2B3519', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-s6-edge-32gb/goud/abonnement?articles=405%2B477%2B3519', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-a5-2016/goud/abonnement?articles=2800%2B2865%2B3776', 'https://telefoonabonnementen.mediamarkt.nl/samsung-galaxy-j5-2016/goud/abonnement?articles=2800%2B2807%2B2843']
    # phones_info = []
    # for phone in phones:
    #     phones_info.append(get_phone_info(phone))
    phones_info = [{'name': 'Samsung Galaxy S9 Zwart', 'Vodafone': '480', 'T-Mobile': '480', 'Tele2': '480', 'KPN': '528', 'Telfort': '528', 'Hollandsnieuwe': '528', 'Lebara': '516,40'}, {'name': 'Samsung Galaxy S9+ Zwart', 'Vodafone': '552', 'T-Mobile': '576', 'Tele2': '576', 'KPN': '600', 'Telfort': '624', 'Hollandsnieuwe': '624', 'Lebara': '612,93'}, {'name': 'Samsung Galaxy Note9 128GB Midnight Zwart', 'Vodafone': '768', 'T-Mobile': '720', 'Tele2': '768', 'KPN': '720', 'Telfort': '816', 'Hollandsnieuwe': '816', 'Lebara': '821,75'}, {'name': 'Samsung Galaxy S8 Zwart', 'Vodafone': '360', 'T-Mobile': '384', 'Tele2': '336', 'KPN': '408', 'Telfort': '480', 'Ben': '468', 'Hollandsnieuwe': '432', 'Lebara': '468,72'}, {'name': 'Samsung Galaxy A6 2018 Paars', 'Vodafone': '192', 'T-Mobile': '168', 'Tele2': '168', 'KPN': '144', 'Telfort': '192', 'Ben': '216', 'Hollandsnieuwe': '216', 'Lebara': '218,59'}, {'name': 'Samsung Galaxy A8 Dual Sim Zwart', 'Vodafone': '288', 'T-Mobile': '216', 'Tele2': '216', 'KPN': '216', 'Telfort': '240', 'Ben': '300', 'Hollandsnieuwe': '288', 'Lebara': '299'}, {'name': 'Samsung Galaxy A7 64GB Blauw', 'Vodafone': '192', 'T-Mobile': '192', 'Tele2': '192', 'KPN': '240', 'Telfort': '264', 'Ben': '264', 'Hollandsnieuwe': '216', 'Lebara': '258,13'}, {'name': 'Samsung Galaxy A6+ 2018 Paars', 'Vodafone': '216', 'T-Mobile': '192', 'Tele2': '192', 'KPN': '192', 'Telfort': '240', 'Ben': '240', 'Hollandsnieuwe': '240', 'Lebara': '245,06'}, {'name': 'Samsung Galaxy J6 2018 Goud', 'Vodafone': '120', 'T-Mobile': '96', 'Tele2': '96', 'KPN': '72', 'Telfort': '144', 'Ben': '156', 'Hollandsnieuwe': '144', 'Lebara': '153,68'}, {'name': 'Samsung Galaxy A5 2017 Zwart', 'Vodafone': '240', 'T-Mobile': '240', 'Tele2': '192', 'KPN': '240', 'Telfort': '192', 'Ben': '192', 'Hollandsnieuwe': '240', 'Lebara': '231,62'}, {'name': 'Samsung Galaxy S7 Zwart', 'Vodafone': '336', 'T-Mobile': '288', 'Tele2': '288', 'KPN': '336', 'Telfort': '336', 'Ben': '324', 'Hollandsnieuwe': '336', 'Lebara': '326,88'}, {'name': 'Samsung Galaxy J3 2017 Zwart', 'Vodafone': '144', 'T-Mobile': '144', 'Tele2': '96', 'KPN': '144', 'Telfort': '144', 'Ben': '144', 'Hollandsnieuwe': '72', 'Lebara': '139,08'}, {'name': 'Samsung Galaxy Note9 512GB Midnight Zwart', 'Vodafone': '912', 'T-Mobile': '912', 'Tele2': '912', 'KPN': '864', 'Telfort': '960', 'Hollandsnieuwe': '960', 'Lebara': '955,16'}, {'name': 'Samsung Galaxy J4+ 32GB Goud', 'Vodafone': '144', 'T-Mobile': '144', 'Tele2': '96', 'KPN': '144', 'Telfort': '144', 'Ben': '144', 'Hollandsnieuwe': '144', 'Lebara': '144,41'}, {'name': 'Samsung Galaxy J5 2017 Goud', 'Vodafone': '144', 'T-Mobile': '168', 'Tele2': '120', 'KPN': '144', 'Telfort': '144', 'Ben': '156', 'Hollandsnieuwe': '96', 'Lebara': '177,27'}, {'name': 'Samsung Galaxy S9+ 256GB Midnight Zwart', 'Vodafone': '720', 'T-Mobile': '720', 'Tele2': '720', 'KPN': '744', 'Telfort': '768', 'Hollandsnieuwe': '768', 'Lebara': '765,35'}, {'name': 'Samsung Galaxy J6+ 32GB Grijs', 'Vodafone': '168', 'T-Mobile': '144', 'Tele2': '144', 'KPN': '120', 'Telfort': '192', 'Ben': '192', 'Hollandsnieuwe': '192', 'Lebara': '187,10'}, {'name': 'Samsung Galaxy J7 2017 Zwart', 'Vodafone': '192', 'T-Mobile': '192', 'Tele2': '144', 'KPN': '192', 'Telfort': '192', 'Ben': '180', 'Hollandsnieuwe': '192', 'Lebara': '182,04'}, {'name': 'Samsung Galaxy S9 256GB Midnight Zwart', 'Vodafone': '672', 'T-Mobile': '648', 'Tele2': '648', 'KPN': '696', 'Telfort': '696', 'Hollandsnieuwe': '696', 'Lebara': '696,67'}, {'name': 'Samsung Galaxy xCover 4 Zwart', 'Vodafone': '168', 'T-Mobile': '168', 'Tele2': '120', 'KPN': '168', 'Telfort': '168', 'Ben': '180', 'Hollandsnieuwe': '168', 'Lebara': '175,23'}, {'name': 'Samsung Galaxy J3 Goud', 'Vodafone': '120', 'T-Mobile': '120', 'Tele2': '72', 'KPN': '120', 'Telfort': '120', 'Ben': '120', 'Hollandsnieuwe': '120', 'Lebara': '120'}, {'name': 'Samsung Galaxy Note8 Zwart', 'Vodafone': '648', 'T-Mobile': '648', 'Tele2': '600', 'KPN': '648', 'Telfort': '648', 'Hollandsnieuwe': '648', 'Lebara': '647'}, {'name': 'Samsung Galaxy S8+ Zwart', 'Vodafone': '552', 'T-Mobile': '552', 'Tele2': '504', 'KPN': '552', 'Telfort': '552', 'Hollandsnieuwe': '552', 'Lebara': '547'}, {'name': 'Samsung Galaxy A3 2017 Zwart', 'Vodafone': '240', 'T-Mobile': '240', 'Tele2': '192', 'KPN': '240', 'Telfort': '240', 'Ben': '240', 'Hollandsnieuwe': '240', 'Lebara': '235,73'}, {'name': 'Samsung Galaxy A9 Lemonade Blauw', 'Vodafone': '480', 'T-Mobile': '456', 'Tele2': '432', 'KPN': '456', 'Telfort': '480', 'Ben': '492', 'Hollandsnieuwe': '480', 'Lebara': '491,47'}, {'name': 'Samsung Galaxy S7 Edge Blauw', 'Vodafone': '408', 'T-Mobile': '408', 'Tele2': '360', 'KPN': '408', 'Telfort': '408', 'Hollandsnieuwe': '408', 'Lebara': '399'}, {'name': 'Samsung Galaxy A3 2016 Goud', 'Vodafone': '192', 'T-Mobile': '192', 'Tele2': '144', 'KPN': '192', 'Telfort': '192', 'Ben': '204', 'Hollandsnieuwe': '192', 'Lebara': '199'}, {'name': 'Samsung Galaxy J7 2016 Goud', 'Vodafone': '264', 'T-Mobile': '264', 'Tele2': '216', 'KPN': '264', 'Telfort': '264', 'Ben': '252', 'Hollandsnieuwe': '264', 'Lebara': '257,25'}, {'name': 'Samsung Galaxy S6 32GB Goud', 'Vodafone': '288', 'T-Mobile': '288', 'Tele2': '240', 'KPN': '288', 'Telfort': '288', 'Ben': '288', 'Hollandsnieuwe': '288', 'Lebara': '288'}, {'name': 'Samsung Galaxy S6 Edge 32GB Goud', 'Vodafone': '384', 'T-Mobile': '384', 'Tele2': '336', 'KPN': '384', 'Telfort': '384', 'Ben': '396', 'Hollandsnieuwe': '384', 'Lebara': '394,97'}, {'name': 'Samsung Galaxy A5 2016 Goud', 'Vodafone': '312', 'T-Mobile': '312', 'Tele2': '264', 'KPN': '312', 'Telfort': '312', 'Ben': '312', 'Hollandsnieuwe': '312', 'Lebara': '311,15'}, {'name': 'Samsung Galaxy J5 2016 Goud', 'Vodafone': '192', 'T-Mobile': '192', 'Tele2': '144', 'KPN': '192', 'Telfort': '192', 'Ben': '180', 'Hollandsnieuwe': '192', 'Lebara': '181,92'}]
    create_page(phones_info)
    upload_page("Samsung.html")

