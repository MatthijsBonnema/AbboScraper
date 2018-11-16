from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementNotVisibleException
from re import sub
from time import sleep
import ftplib
import time
import os


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


def get_phones(driver):
    page = 1
    link = ""

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
        link = ""

    return phones


def get_phone_info(link, driver):
    driver.get(link)
    waitForCSS(driver, "div.provider-icon-big", 10)

    waiting = True

    while waiting:
        try:
            phone_name = driver.find_element_by_class_name("fullwidth").get_attribute("innerHTML").replace(
                '<span class="fw-bold">GSM</span><br>', '').strip()
            waiting = False
        except NoSuchElementException:
            pass
    test = open("test.txt", 'w')
    test.write(phone_name)

    phone_dict = {"name": phone_name}
    providers = driver.find_elements_by_class_name("provider-border")

    for provider in providers:
        if provider.text == "Advies":
            break
        provider_name = provider.get_attribute("title")
        provider.click()
        sleep(0.4)

        options = driver.find_elements_by_class_name("form-option-dropdown")
        if len(options) > 0:
            option_nr = 0
            for option in options:
                try:
                    option.click()
                except StaleElementReferenceException:
                    sleep(0.2)
                    option.click()
                sleep(0.4)

                try:
                    two_years = driver.find_element_by_xpath("//input[@type='radio' and @value='24']/following-sibling::label")
                    two_years.click()
                except ElementNotVisibleException:
                    pass

                try:
                    total_credit = driver.find_element_by_class_name("credit-table-totalvalue").text.strip(
                        "€").strip(",-")
                except NoSuchElementException:
                    total_credit = "0"
                    pass
                except StaleElementReferenceException:
                    total_credit = "0"
                    pass
                if option_nr == 0:
                    phone_dict["{}".format("{}".format(provider_name))] = total_credit
                    print(phone_name, provider_name, total_credit)
                elif option_nr == 1:
                    phone_dict["{}".format("{}_secundair".format(provider_name))] = total_credit
                    print(phone_name, "{}".format("{}_secundair".format(provider_name)), total_credit)
                else:
                    print("Dafuq!")
                option_nr += 1
        else:
            try:
                total_credit = driver.find_element_by_class_name("credit-table-totalvalue").text.strip("€").strip(",-")
            except NoSuchElementException:
                total_credit = "0"
                pass
            except StaleElementReferenceException:
                total_credit = "0"
                pass
            phone_dict["{}".format(provider_name)] = total_credit
            total_credit_secundair = "-"
            phone_dict["{}".format("{}_secundair".format(provider_name))] = total_credit_secundair

            print(phone_name, provider_name, total_credit)

    test.close()
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

    phones_info = sorted(phones_info, key=lambda k: k['name'], reverse=True)

    for phone in phones_info:
        if phone_nr % 2 == 0:
            table_class = "tg-even"
        else:
            table_class = "tg-odd"
        result.write("    <tr>\n")
        provider_lijst = ['Vodafone', 'T-Mobile', 'Tele2', 'KPN', 'Telfort', 'Ben', 'Hollandsnieuwe', 'Lebara']
        provider_lijst_2 = ['Vodafone', 'T-Mobile', 'Tele2', 'KPN', 'Lebara']
        result.write('        <td class="{}">{}</td>\n'.format(table_class, phone['name']))

        for provider in provider_lijst:
            try:
                result.write('        <td class="{}">&euro; {}</td>\n'.format(table_class, phone[provider]))
                if provider in provider_lijst_2:
                    result.write('        <td class="{}">&euro; {}</td>\n'.format(table_class, phone["{}_secundair".format(provider)]))
            except KeyError:
                try:
                    result.write('        <td class="{}">&euro; {}</td>\n'.format(table_class, phone[provider]))
                    if provider in provider_lijst_2:
                        result.write('        <td class="{}">&euro; -</td>\n'.format(table_class))

                except KeyError:
                    result.write('        <td class="{}">&euro; -</td>\n'.format(table_class))


        result.write("    </tr>\n")

        phone_nr += 1

    result.write("</tbody>\n")
    result.write("</table>\n")
    result.write("<p><h3>Gemaakt door Matthijs Bonnema, voor vragen mail admin[apenstaartje]msbonnema.nl<h3>\n")


def upload_page(filename):
    session = ftplib.FTP('host', 'user', 'pass')
    file = open(filename, 'rb')
    session.cwd('web')
    session.storbinary('STOR Samsung.html', file)
    file.close()
    session.quit()
    print("UPLOADED!")


if __name__ == '__main__':
    os.chdir("")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"

    while True:
        driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver)
        driver.maximize_window()
        driver.get("https://google.nl")
        phones = get_phones(driver)
        phones_info = []
        for phone in phones:
            phones_info.append(get_phone_info(phone, driver))
        create_page(phones_info)
        upload_page("Samsung.html")
        driver.close()
        sleep(60)
