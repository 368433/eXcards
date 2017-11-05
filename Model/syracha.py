import requests, csv, os, time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
#line below added to enable headless run of code
from selenium.webdriver.chrome.options import Options


#following code aims to make headless use of chromedriver
#taken from https://duo.com/blog/driving-headless-chrome-with-python
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# yo = webdriver.Chrome("/Users/Bond/Documents/Etude/CSLab/CardsProject/testing/headless/chromedriver", chrome_options=chrome_options)
driver = webdriver.Chrome("/Users/Bond/Documents/Etude/CSLab/CardsProject/testing/headless/chromedriver")

util = 'IP024043'
mdp = 'DZTfprU2eDJT'
# Normalement, j'ajoute une entête quand je me connecte à un site web par le biais d'un script, afin de m'identifier.
# Mais selenium ne permet pas d'envoyer des entêtes dans une requête à un site...
driver.get("https://www4.prod.ramq.gouv.qc.ca/AGS/YR/YRM_GestAuthn/YRM1_V4Authn_iut/IntrfAuth.aspx")

inpututil = driver.find_element_by_id("PlaceHolderContenuCentre_PlaceHolderMain_CtrlAuthnUtil_TxtNomUtil_MonTextBox1")
inputmdp = driver.find_element_by_id("PlaceHolderContenuCentre_PlaceHolderMain_CtrlAuthnUtil_TxtMotPass_MonTextBox1")

inpututil.send_keys(util)
time.sleep(3)
inputmdp.send_keys(mdp, Keys.RETURN)

time.sleep(5)
driver.get("https://www4.prod.ramq.gouv.qc.ca/RFP/SiteRemuProf/accueil")

# resultats = driver.page_source
# element = WebDriverWait(driver, 10).until(
#         driver.find_element_by_partial_link_text('FacturActe')))

# creer une facture
time.sleep(5)
elem = driver.find_element_by_xpath('/html/body/main/div/div/div/div/button')
elem.click()
# suivant
time.sleep(7)
next = driver.find_element_by_xpath('/html/body/main/div/div/div/div/div[2]/div[2]/div[2]/div/div/div/div/button')
next.click()
# NAM
time.sleep(5)
nam = driver.find_element_by_xpath('//*[@id="AvecCarte"]/div/div/div/div[2]/div[1]/div[2]/div[1]/div/input')
nam.send_keys('AMIR')
# diagnostic code
time.sleep(5)
toggledx = driver.find_element_by_xpath('//*[@id="AvecCarte"]/div/div/div/div[2]/div[1]/div[4]/div/div/div/div/div[1]/div/h2/span/div[1]')
toggledx.click()
diagnosis = driver.find_element_by_xpath('//*[@id="ListeDiagnMedicAvecNam"]/div/div/table/tbody[2]/tr/td[1]/div/div/input')
diagnosis.send_keys('0400')
ajout = driver.find_element_by_xpath('//*[@id="ListeDiagnMedicAvecNam"]/div/div/table/tbody[2]/tr/td[3]/div/div/button')
ajout.click()
#lieu de dispensation = hopital/clinique
lieu = driver.find_element_by_xpath('//*[@id="ScrollLieu"]/div[2]/div/div[1]/div[1]/div/div/label[1]/input')
lieu.click()
time.sleep(3)
numerolieu = driver.find_element_by_xpath('//*[@id="ScrollLieu"]/div[2]/div/div[1]/div[2]/div[2]/div[1]/div/input')
numerolieu.send_keys('07533')
# secteur
# //*[@id="rechrSectActiv"]/div[2]/div[3]/table/tbody/tr[2]/td[1]
secteur = driver.find_element_by_xpath('//*[@id="ScrollLieu"]/div[2]/div/div[1]/div[2]/div[5]/div/div[1]/div/input')
secteur.click()
secteur2 = driver.find_element_by_xpath('//*[@id="rechrSectActiv"]/div[2]/div[1]/div[1]/div[2]/div[1]/input')
secteur2.send_keys('Clinique externe')
resultrow = driver.find_element_by_xpath('//*[@id="rechrSectActiv"]/div[2]/div[3]/table/tbody/tr')
resultrow.click()
#next page - Etape 2 lignes de facture
time.sleep(3)
next = driver.find_element_by_xpath('/html/body/main/div/div/div/div/div[2]/div[6]/div/div/div/div/button[2]')
next.click()
