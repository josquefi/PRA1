#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback
import csv
import sys
import time
from tqdm import tqdm
import undetected_chromedriver as uc
import utils as u

def scrape_numeric_values(url):
    """
    Scrapes a webpage to extract numerical values from div tags that contain the
    "form-check" class.
    
    Args:
        url (str): The URL of the webpage to scrape.
    
    Returns:
        list: A list of all the numerical values found in div tags with class
        "form-check" on the webpage.
    """
    response = requests.get(url)
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
    values_divs = soup.find_all('div', class_='form-check')
    values_list = []
    for div in values_divs:
        value = div.find('input')['value']
        if re.match(r'^\d+$', value):
            values_list.append(value)
    return values_list


def scrape_result_urls(values_list, url):
    """
    Scrapes a webpage to select checkboxes corresponding to the given numerical
    values, waits for the resulting page to load, and returns a list of the
    resulting URLs.

    Args:
        values_list (list): A list of numerical values to select checkboxes for.
        url (str): The URL of the webpage to scrape.

    Returns:
        list: A list of URLs resulting from selecting the given checkboxes.
    """
    # Initialize the browser
    driver = webdriver.Chrome()
    driver.get(url)

    # Select checkboxes for each value and capture the resulting URLs
    result_urls = []
    for value in values_list:
        checkbox_id = f"pg_checkbox_{value}"
        try:
            checkbox = driver.find_element(By.ID, checkbox_id)
            checkbox.click()
            # Wait for the page to load
            WebDriverWait(driver, 10).until(EC.url_changes(url))
            result_urls.append(driver.current_url)
        except NoSuchElementException:
            print(f"No se encontró el elemento con id '{checkbox_id}'")
            continue
        # Return to the original URL
        driver.get(url)

    # Close the browser
    driver.quit()

    return result_urls


def scrape_links(url_list, class_name):
    """
    Scrapes a list of webpages for links with the given class, and returns a list
    of all the links found.

    Args:
        url_list (list): A list of URLs to scrape.
        class_name (str): The class name to search for in the HTML.

    Returns:
        list: A list of all the links found on the scraped webpages.
    """
    # Initialize a list to store all the links
    links = []

    # Scrape each URL for links with the given class name
    for url in url_list:
        # Get the HTML content of the webpage
        response = requests.get(url)
        html_content = response.content

        # Parse the HTML content with Beautiful Soup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all elements with the given class name and get their links
        for element in soup.find_all(class_=class_name):
            link = element.find('a')
            if link:
                links.append(link['href'])

    return links


def scrape_session_data(enlaces_totales):
    """
    Scrapes session data from a list of URLs using Selenium and BeautifulSoup, and writes the data to a CSV file.
    
    Args:
        enlaces_totales (list): A list of URLs to scrape data from.
    
    Returns:
        None.
    
    Raises:
        SystemExit: If an exception occurs while scraping data, the program exits with status code 1.
    
    The function uses the Chrome web driver to open each URL in the list and waits for a session block title to appear. It then extracts the session and information strings from the page, and loops over all abstracts in the session to extract their title, authors, and up to 18 characteristics. The extracted data is written to a CSV file named 'Sessions_EGU2023.csv' in append mode, using the header row specified in the `fieldnames` variable.
    
    If an exception occurs while scraping data, the function prints an error message and traceback to the console and exits with status code 1.
    
    """

    target_urls = enlaces_totales
    fieldnames = ['Sessió', 'Informació', 'Títol', 'Autors', 'Caracteristica1', 'Caracteristica2', 'Caracteristica3', 'Caracteristica4', 'Caracteristica5', 'Caracteristica6', 'Caracteristica7', 'Caracteristica8', 'Caracteristica9', 'Caracteristica10', 'Caracteristica11', 'Caracteristica12', 'Caracteristica13', 'Caracteristica14', 'Caracteristica15', 'Caracteristica16', 'Caracteristica17', 'Caracteristica18']
    
    with open('Sessions_EGU2023.csv', mode='a', encoding='utf-8', newline='') as prop_file:
        prop_writer = csv.DictWriter(prop_file, fieldnames=fieldnames)

        prop_writer.writeheader()

        try:
            with webdriver.Chrome() as driver:
                for target_url in tqdm(target_urls):
                    driver.get(target_url)

                    wait = WebDriverWait(driver, 10)
                    session_block_title = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.co_mto_programme-session-block-title.active')))

                    resp = driver.page_source
                    soup = BeautifulSoup(resp, 'html.parser')

                    all_sesiones = soup.find_all("div", {"class": ["oralprogramme_schedulings_abstract col", "displayprogramme_schedulings_abstract col-12"]})
                    session = session_block_title.text.strip("\n")
                    info = soup.find("div",{"class": "mo_scheduling_string"}).text.strip("\n")

                    for sesiones in all_sesiones:
                        title = sesiones.find("div", {"class": "co_mto_abstractHTML-title d-inline col-12"}).text.strip("\n")
                        authors = sesiones.find("div", {"class": "authors col-12"}).text.strip("\n")
                        sesion_element = sesiones.find("div", {"class": "row no-gutters co_mto_abstractRow"})
                        sesion_list = sesion_element.find_all("div", {"class":["col-auto regular","col-auto"]})
                        elementos = {}
                        for i, elemento in enumerate(sesion_list):
                            elemento_name = f"Caracteristica{i+1}"
                            elementos[elemento_name] = elemento.text.strip()

                        # Se escriben los datos en el archivo CSV
                        prop_writer.writerow({'Sessió': session, 'Informació': info, 'Títol': title, 'Autors': authors, **elementos})

        except Exception as e:
            print(f"Error: {e}")
            print("".join(traceback.format_exception(*sys.exc_info())))
            sys.exit(1)

