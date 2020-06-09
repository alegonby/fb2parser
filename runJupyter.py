from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
# URL to Jupyter notebook. we assume that Epam VPN is enabled
driver.get("https://projectby.trainings.dlabanalytics.com/agonchar41/notebooks/Aleksandr_Gonchar.ipynb")
# click SSO button
sso_button = driver.find_element_by_id('zocial-epam-idp').click()
# wait till cell dropdown menu is clickable, and click on it
wait = WebDriverWait(driver, 20)
cell = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="menus"]/div/div/ul/li[5]'))).click()
# click Run all button
runAll = driver.find_element_by_xpath('//*[@id="run_all_cells"]').click()


