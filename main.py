# Main function to iterate through pages
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from crunchbase import cb_search_main
from comparison import compare

# Company information scraper
# It goes to a specified URL and reads the data there with selenium. Then it requests information
# from crunchbase about those companies. It has it's limitations and places to expand and update...
# For now, it's just a simple example. 

# scrape_with_selenium needs to be adjusted for each conference since the page setup for listing the exhibitors differs.
# Requesting information from crunchbase is now done with my free account, this is why I needed to build in a timer to 
# stop and restart every time the number of free requests in a minute is over. Comparison is based on JSON files. It most probably needs
# some tweeking for each occasion, the class created to save the enriched company data might need to be updated.
# Next things to develop would be:
#   - fine tuning the information enrichment with crunchbase (and possibly with other sources):
#       - Company name matching works a bit weird, sometimes the company name is not the same in the conference's page and crunchbase
#       - Other information is available after payment: Job postings, employees, funding information...
#   - an actual decision helper, probably with AI
#   - script to go through the websites and get contact persons
#   - save everything in a database for Sales, get a score for each as possible partners, lead value so an AI algorithm can learn from that

def main():
    # URL of the event where the companies are listed
    base_url = 'https://www.dmea.de/en/exhibitors/exhibitor-overview/#/search/f=h-entity_orga;v_sg=0;v_fg=0;v_fpa=FUTURE'

    # Ask if executing the full stuff or just the comparison script (Saving time. Since the cost of this is 0, 
    # scraping through the web page takes time, then requesting information from crunchbase takes even more time.)
    executor = 'a'
    while executor.lower() != 'c' and executor.lower() != 'f':
        print("Wrong input. Try again! Input was: " + executor)
        executor = input("Execute the full script (F), or just the comparison part (C)? F / C")
    if executor == "f":
        # Scrape data
        scrape_with_selenium(base_url)
        compare()
    else: 
        compare()

def scrape_with_selenium(url):

    # Testing only the cb part
    isTesting = True
    if isTesting != True:

        #Real, working code from here
        driver = webdriver.Chrome()
        driver.get(url)
        driver.maximize_window()

        # Accept cookies if the button exists
        time.sleep(10)
        try:
            element = driver.execute_script("""return document.querySelector('#usercentrics-root').shadowRoot.querySelector("button[data-testid='uc-accept-all-button']")""")
            element.click()
        except:
            print('Cookies already accepted.')

        # Wait for the page to load completely
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "EWP5KKC-e-J")))
        
        # Load all items
        while True:
            show_more = driver.find_element(By.XPATH, "//*[@id='onlineGuide']/div/div[4]/div[1]/div[2]/div[4]/div[1]")
            time.sleep(0.4)
            try:
                show_more.click()
                time.sleep(1)
            except:
                print("End")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Adjust sleep time as needed
                break

        # Now go through all items and get the info
        items = driver.find_elements(By.CLASS_NAME, 'EWP5KKC-w-w')
        for item in items:
            driver.execute_script("arguments[0].scrollIntoView(true);", item)
            driver.execute_script("arguments[0].click();", item)
            # Get the necessary information (name, address, description)
            company_name = WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='onlineGuidePopup']/div/div/div[1]/div[2]/div[1]/div[2]/div[2]/div[1]/div/div/div[1]"))).get_attribute("innerHTML")
            try:
                company_country = WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='onlineGuidePopup']/div/div/div[1]/div[2]/div[1]/div[2]/div[2]/div[1]/div/div/div[3]/div[2]"))).get_attribute("innerHTML")
            except:
                print("No country provided.")
                company_country = "Unknown"
            try:
                company_stand = WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='onlineGuidePopup']/div/div/div[1]/div[2]/div[5]/div[2]/div[1]/div/div[2]/div/div[3]/div[1]"))).get_attribute("innerHTML")
            except:
                print("No stand provided.")
                company_stand = "Unknown"
            try:
                company_desc = WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='onlineGuidePopup']/div/div/div[1]/div[2]/div[2]/div/div[2]/div[1]/div/div[1]"))).get_attribute("innerHTML")
            except:
                print("No description")
                company_desc = "No description provided."
            # Put it in a JSON or smthng
            dictionary = {"company_name" : company_name, "company_country" : company_country, "company_stand" : company_stand, "company_desc" : company_desc}
            json_dump = json.dumps(dictionary)
            with open('companies', 'a') as f:
                f.write(json_dump+"\r\n")

        # Close the WebDriver
        driver.quit()

    # Call the other function to read the data
    read_companies()

def read_companies():
    print("Opening companies JSON")
    with open('companies') as f:
        for line in f:
            # Parse the JSON from the line and read the data necessary
            print("Reading line...")
            try:
                company_data = json.loads(line)
            except:
                continue
            company_name = company_data['company_name'].partition(' ')[0]
            print("Got company name: " + company_name)
            
            # Execute the function to get the uuid and other stuff
            cb_search_main(company_name)

if __name__ == "__main__":
    main()

  