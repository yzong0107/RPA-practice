__author__="Tim Zong (yzong@ualberta.ca)"

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *

import csv


class TestPractice():
    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_practice(self, path):
        now = time.time()
        """Load credentials to log in"""
        with open(r"credential.csv",
                  "r") as credential:
            credential = csv.DictReader(credential)
            for row in credential:
                username = row["username"]
                password = row["password"]

        row_count = 0
        error_log = open("Error Logs.txt", "r+")
        error_log.truncate(0)
        errorCount = 0
        
        self.driver.get(r"https://www.aimdemo.ualberta.ca/fmax/screen/WORKDESK")
        self.driver.set_window_size(1900, 1020)
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(By.ID, "login").click()

        """Read csv file"""
        with open(path, "r") as csvFile:
            csvReader = csv.DictReader(csvFile)
            fields = csvReader.fieldnames
            for row in csvReader:
                row_count += 1
                print_to_log = ',\n'.join(field + ":" + row[field] for field in fields)
                add_location_success = True
                # print(row)
                self.driver.find_element(By.ID, "mainForm:menuListMain:PROPERTY").click()
                self.driver.find_element(By.ID, "mainForm:menuListMain:new_SA_LOCATION_VIEW").click()
                self.driver.find_element(By.ID, "mainForm:SA_LOCATION_EDIT_content:ae_b_loc_d_location_code").send_keys(row["LocationName"])

                try:
                    self.driver.find_element(By.ID, "mainForm:SA_LOCATION_EDIT_content:RFPLZoom:level2").send_keys(row["Property"])
                    self.driver.find_element(By.CSS_SELECTOR,"#mainForm\\3ASA_LOCATION_EDIT_content\\3ARFPLZoom\\3Alevel2_button > .halflings").click()
                    self.driver.find_element(By.ID, "mainForm:SA_LOCATION_EDIT_content:locTypeZoom:level0").send_keys(row["LocationType"])
                    self.driver.find_element(By.CSS_SELECTOR,"#mainForm\\3ASA_LOCATION_EDIT_content\\3AlocTypeZoom\\3Alevel0_button > .halflings").click()
                    self.driver.find_element(By.ID, "mainForm:SA_LOCATION_EDIT_content:usageZoom:level1").send_keys(row["PrimaryUsage"])
                    self.driver.find_element(By.CSS_SELECTOR,"#mainForm\\3ASA_LOCATION_EDIT_content\\3AusageZoom\\3Alevel1_button > .halflings").click()
                except NoSuchElementException:
                    errorCount += 1
                    error_log.write(str(errorCount) + ". Record of \n{" + print_to_log + "} not saved!\n")
                    error_log.write("Validation of Property/Location Type/ Primary Usage fails!Please double check the input.\n")
                    error_log.write("\n")  # blank row
                    self.driver.find_element(By.ID, "mainForm:buttonPanel:cancel").click()
                    self.driver.find_element(By.ID, "mainForm:headerInclude:aimTitle1").click()
                    continue  # move to next row

                self.vars["gen_region"] = self.driver.find_element(By.ID,"mainForm:SA_LOCATION_EDIT_content:RFPLZoom:level0").get_attribute("value")
                self.vars["gen_facility"] = self.driver.find_element(By.ID,"mainForm:SA_LOCATION_EDIT_content:RFPLZoom:level1").get_attribute("value")
                # yzong: verify if the generated region and facility matches to the input value
                if self.vars["gen_region"] != row["Region"]:
                    errorCount += 1
                    error_log.write(str(errorCount) + ". Record of \n{" + print_to_log + "} not saved!\n")
                    error_log.write("Region area doesn't match!Please double check the input.\n")
                    error_log.write("\n")  # blank row
                    self.driver.find_element(By.ID, "mainForm:buttonPanel:cancel").click()
                    self.driver.find_element(By.ID, "mainForm:headerInclude:aimTitle1").click()
                    continue  # move to next row
                if self.vars["gen_facility"] != row["Facility"]:
                    errorCount += 1
                    error_log.write(str(errorCount) + ". Record of \n{" + print_to_log + "} not saved!\n")
                    error_log.write("Facility area doesn't match!Please double check the input.\n")
                    error_log.write("\n")  # blank row
                    self.driver.find_element(By.ID, "mainForm:buttonPanel:cancel").click()
                    self.driver.find_element(By.ID, "mainForm:headerInclude:aimTitle1").click()
                    continue  # move to next row

                # yzong: sanity check if the record can be saved. If success, move to adding organization; else, skip to next row to add.
                self.driver.find_element(By.ID, "mainForm:buttonPanel:save").click()
                try:
                    self.driver.find_element(By.ID, "mainForm:headerInclude:aimTitle1").click()
                except NoSuchElementException:
                    add_location_success = False
                    errorCount += 1
                    error_log.write(str(errorCount) + ". Record of \n{" + print_to_log + "} not saved!\n")
                    error_log.write(self.driver.find_element(By.CSS_SELECTOR, "#mainForm\\3ASA_LOCATION_EDIT_content\\3Amessages > li").text + "\n")
                    error_log.write("\n")  # blank row
                    self.driver.find_element(By.ID, "mainForm:buttonPanel:cancel").click()
                    self.driver.find_element(By.ID, "mainForm:headerInclude:aimTitle1").click()

                """Add Organization part"""
                if add_location_success:
                    self.driver.find_element(By.ID, "mainForm:menuListMain:SPACEMGT").click()
                    self.driver.find_element(By.ID, "mainForm:menuListMain:search_ORG_OCC_VIEW").click()
                    self.driver.find_element(By.ID, "mainForm:ae_b_loc_d_region_code:level0").clear()
                    self.driver.find_element(By.ID, "mainForm:ae_b_loc_d_region_code:level0").send_keys(row["Region"])
                    self.driver.find_element(By.ID, "mainForm:ae_b_loc_d_fac_id:level1").clear()
                    self.driver.find_element(By.ID, "mainForm:ae_b_loc_d_fac_id:level1").send_keys(row["Facility"])
                    self.driver.find_element(By.ID, "mainForm:ae_b_loc_d_bldg:level2").clear()
                    self.driver.find_element(By.ID, "mainForm:ae_b_loc_d_bldg:level2").send_keys(row["Property"])
                    self.driver.find_element(By.ID, "mainForm:ae_b_loc_d_location_code:level3").clear()
                    self.driver.find_element(By.ID, "mainForm:ae_b_loc_d_location_code:level3").send_keys(row["LocationName"])
                    self.driver.find_element(By.ID, "mainForm:buttonPanel:executeSearch").click()
                    self.driver.find_element(By.ID, "mainForm:browse:0:ae_b_loc_d_location_code").click()
                    self.driver.find_element(By.ID, "mainForm:buttonPanel:edit").click()
                    self.driver.find_element(By.ID, "mainForm:ORG_OCC_EDIT_content:organizationList:addRowButton").click()
                    self.driver.find_element(By.ID, "mainForm:ORG_OCC_DETAIL_EDIT_content:CDOCZoom:CDOCZoom2").click()
                    self.driver.find_element(By.ID, "mainForm:ORG_OCC_DETAIL_EDIT_content:CDOCZoom:CDOCZoom2").send_keys(row["Organization"])
                    try:
                        self.driver.find_element(By.CSS_SELECTOR, "#mainForm\\3AORG_OCC_DETAIL_EDIT_content\\3A CDOCZoom\\3A CDOCZoom2_button > .halflings").click()
                        self.driver.find_element(By.ID, "mainForm:ORG_OCC_DETAIL_EDIT_content:fromValue").click()
                    except NoSuchElementException:
                        errorCount += 1
                        error_log.write(str(errorCount) + ". Record of \n{" + print_to_log + "} not saved!\n")
                        error_log.write("Validation of Organization fails! Please double check the input.\n")
                        error_log.write("\n")  # blank row
                        self.driver.find_element(By.ID, "mainForm:buttonPanel:cancel").click()
                        self.driver.find_element(By.ID, "mainForm:buttonPanel:cancel").click()
                        self.driver.find_element(By.ID, "mainForm:buttonPanel:cancel").click()
                        self.driver.find_element(By.ID, "mainForm:headerInclude:aimTitle1").click()
                        continue


                    # Default value is TODAY
                    if row["FromDate"] == "":
                        self.driver.find_element(By.CSS_SELECTOR, ".today").click()
                    else:
                        self.driver.find_element(By.ID, "mainForm:ORG_OCC_DETAIL_EDIT_content:fromValue").send_keys(row["FromDate"])
                    self.driver.find_element(By.ID, "mainForm:ORG_OCC_DETAIL_EDIT_content:percentValue").click()
                    self.driver.find_element(By.ID, "mainForm:ORG_OCC_DETAIL_EDIT_content:percentValue").send_keys(row["Percentage"])

                    try:
                        self.driver.find_element(By.ID, "mainForm:buttonPanel:done").click()
                        self.driver.find_element(By.ID, "mainForm:buttonPanel:save").click()
                        self.driver.find_element(By.ID, "mainForm:headerInclude:aimTitle1").click()
                    except NoSuchElementException:
                        errorCount += 1
                        error_log.write(str(errorCount) + ". Record of \n{" + print_to_log + "} not saved!\n")
                        error_log.write(self.driver.find_element(By.CSS_SELECTOR, "#mainForm\\3AORG_OCC_DETAIL_EDIT_content\\3Amessages > li").text + "\n")
                        error_log.write("\n")  # blank row
                        self.driver.find_element(By.ID, "mainForm:buttonPanel:cancel").click()
                        self.driver.find_element(By.ID, "mainForm:buttonPanel:cancel").click()
                        self.driver.find_element(By.ID, "mainForm:headerInclude:aimTitle1").click()
            error_log.close()

        print ("Taken: " + str(time.time()-now) + " s")
        print (str(errorCount)+"/"+str(row_count)+" records NOT saved. Check error logs for more details.")

if __name__ == '__main__':
    selenium_test = TestPractice()
    selenium_test.setup_method("POST")
    selenium_test.test_practice(r"..\new locations.csv")
