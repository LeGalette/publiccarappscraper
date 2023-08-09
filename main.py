from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from datetime import date, timedelta
import time
from selenium.common.exceptions import NoSuchElementException
import os
import urllib.request
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import certifi
import urllib.request
import ssl
import shutil

# Update this path to the location of your chromedriver executable
CHROME_DRIVER_PATH = 'chromedriver'

def generate_url(start_date, start_time, end_date, end_time):
    base_url = ""
    url = f"{base_url}&start_date={start_date}&start_time={start_time}&end_date={end_date}&end_time={end_time}"
    return url

def save_car_image(image_url, car_id, car_title):
    file_name = f"{car_id}_{car_title}.jpg"
    file_path = os.path.join("cars", file_name)

    if not os.path.exists(file_path):
        try:
            # Add a custom header to the request
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')]
            urllib.request.install_opener(opener)

            # Create SSL context with the certificates
            context = ssl.create_default_context(cafile=certifi.where())

            # Download the image
            with urllib.request.urlopen(image_url, context=context) as response, open(file_path, 'wb') as out_file:
                out_file.write(response.read())
            
            print(f"{car_id}_{car_title}.jpg")
        except urllib.error.HTTPError as e:
            print(f"Error downloading image for {car_title} (ID: {car_id}): {e}")


def accept_cookie_banner(driver):
    try:
        time.sleep(7)  # Flaky modal
        driver.find_element(By.CSS_SELECTOR, ".js_cookie-consent-modal__agreement > .cob-Button__content").click()
        
        time.sleep(2)  # Flaky modal
    except Exception as e:
        print(e)
        pass

def main():
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service)

    today = date.today()
    three_days_later = today + timedelta(days=3)
    three_months_later = today + timedelta(days=90)

    start_time = "08%3A00"
    end_time = "16%3A00"

    current_date = three_days_later
    while current_date <= three_months_later:
        start_date = current_date.strftime("%Y-%m-%d")
        end_date = start_date
        url = generate_url(start_date, start_time, end_date, end_time)
        driver.get(url)

        accept_cookie_banner(driver) 

        time.sleep(5)  # Modals are bad

        while True:
            car_elements = driver.find_elements("xpath", "//a[contains(@class, 'car_card_search-result')]")
            for car_element in car_elements:
                car_id = car_element.get_attribute("data-car-id")
                car_title = car_element.get_attribute("title")
                car_image_element = car_element.find_element("xpath", ".//div[contains(@class, 'car_card__header')]")
                car_image_url = car_image_element.get_attribute("data-background-image")

                save_car_image(car_image_url, car_id, car_title)

            try:
                next_button = driver.find_element("xpath", "//a[@rel='next']")
                if not next_button.is_displayed():
                    break
                next_button.click()
                time.sleep(5)  # Strange backend behaviour
            except NoSuchElementException:
                break

        current_date += timedelta(days=1)

    driver.quit()

if __name__ == "__main__":
    main()