#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""

import utils as u

url = "https://meetingorganizer.copernicus.org/EGU23/sessionprogramme/pg-selection"

values_list = u.scrape_numeric_values(url)

result_urls = u.scrape_result_urls(values_list, url)

enlaces_totales = u.scrape_links(result_urls, 'co_mto_programme-session-block-title active')

u.scrape_session_data(enlaces_totales)
