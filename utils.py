#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 23 19:43:11 2023

@author: josep
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
from tqdm import tqdm

def scrape_numeric_values(url):
    """
    Fa webscraping d'una pàgina web per obtindre els valor numerics continguts pels divs tags
    amb class "form-chek"
    
    """
    headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,\
                */*;q=0.8",
                "Accept-Encoding": "gzip, deflate, sdch, br",
                "Accept-Language": "en-US,en;q=0.8",
                "Cache-Control": "no-cache",
                "dnt": "1",
                "Pragma": "no-cache",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/5\
                37.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
                }
    response = requests.get(url,  headers=headers)
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
    Selecciona els chekboxes que correspon als valors numerics i retorna una llista de les 
    URLs resultants.

    """
    driver = webdriver.Chrome()
    driver.get(url)

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
        driver.get(url)

    driver.quit()

    return result_urls


def scrape_links(url_list, class_name):
    
    """
    Fa webscraping de la llista d'URLs i retorna una llista amb tots els links trobats.

    """
    links = []

    # Fer scraping per a cada URL per trobar els links amb el class_name 
    for url in url_list:
        response = requests.get(url)
        html_content = response.content

        soup = BeautifulSoup(html_content, 'html.parser')

        for element in soup.find_all(class_=class_name):
            link = element.find('a')
            if link:
                links.append(link['href'])

    return links


def scrape_session_data(enlaces_totales):
    
    """
    
    Realitza el scraping de llista d'URLs utilitzant Selenium i BeautifulSoup
    i escriu els resultats a un CSV.
    
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

