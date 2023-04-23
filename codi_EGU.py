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

url = "https://meetingorganizer.copernicus.org/EGU23/sessionprogramme/pg-selection"

# Obtener el contenido HTML de la página web
response = requests.get(url)
html_content = response.content

# Analizar el contenido HTML con Beautiful Soup
soup = BeautifulSoup(html_content, 'html.parser')

# Buscar todas las etiquetas div con clase "form-check"
values_divs = soup.find_all('div', class_='form-check')

# Obtener los valores de cada div que sean numéricos
values_list = []
for div in values_divs:
    value = div.find('input')['value']
    if re.match(r'^\d+$', value):
        values_list.append(value)

# Imprimir los valores obtenidos
print(values_list)

# Iniciar el navegador
driver = webdriver.Chrome()
url = "https://meetingorganizer.copernicus.org/EGU23/sessionprogramme/pg-selection"
driver.get(url)

valores_checkbox = values_list
result_urls = []

for valor in valores_checkbox:
    checkbox_id = f"pg_checkbox_{valor}"
    try:
        checkbox = driver.find_element(By.ID, checkbox_id)
        checkbox.click()
        # Esperar a que se cargue la página resultante
        WebDriverWait(driver, 10).until(EC.url_changes(url))
        result_urls.append(driver.current_url)
    except NoSuchElementException:
        print(f"No se encontró el elemento con id '{checkbox_id}'")
        continue
# Volver a la url original
    driver.get(url)

# Imprimir las URLs resultantes
print(result_urls)

# Lista de URLs
url_list = result_urls

# Lista para almacenar los enlaces de todas las páginas
enlaces_totales = []

# Recorrer la lista de URLs y obtener los enlaces de cada página
for url_session in url_list:
    # Obtener el contenido HTML de la página web
    response = requests.get(url_session)
    html_content = response.content

    # Analizar el contenido HTML con Beautiful Soup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Buscar todos los elementos con la clase "co_mto_programme-session-block-title active" y obtener los enlaces
    enlaces = []
    for elemento in soup.find_all("div", class_="co_mto_programme-session-block-title active"):
        enlace = elemento.find('a')
        enlaces.append(enlace['href'])

    # Agregar los enlaces a la lista total
    enlaces_totales.extend(enlaces)

# Imprimir la lista de enlaces totales
print(enlaces_totales)

# Nova part

target_urls = enlaces_totales

fieldnames = ['Sessió', 'Informació', 'Títol', 'Autors', 'Caracteristica1', 'Caracteristica2', 'Caracteristica3', 'Caracteristica4', 'Caracteristica5', 'Caracteristica6', 'Caracteristica7', 'Caracteristica8','Caracteristica9','Caracteristica10','Caracteristica11','Caracteristica12','Caracteristica13','Caracteristica14','Caracteristica15','Caracteristica16','Caracteristica17','Caracteristica18'] # modificar los nombres de las características según corresponda

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

