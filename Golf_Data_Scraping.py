import pandas as pd

""" data = {
  "calories": [420, 380, 390],
  "duration": [50, 40, 45]
} """

""" df = pd.DataFrame(data, index = ["day1", "day2", "day3"])
 """


URL = "https://www.pgatour.com/tournaments/2023/masters-tournament/R2023014/past-results"

from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

driver = webdriver.Chrome()

# load page
driver.get(URL)

# get table
table = driver.find_element(By.CSS_SELECTOR, "table.chakra-table")
assert table, "table not found"

# remove empty rows
driver.execute_script("""arguments[0].querySelectorAll("td.css-1au52ex").forEach((e) => e.parentElement.remove())""", table)

# get html of the table
table_html = table.get_attribute("outerHTML")

# quit selenium
driver.quit()

df = pd.read_html(table_html)[0]

print(df)