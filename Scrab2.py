
# Get the URL https://webscraper.io/test-sites/e-commerce/allinone using requests library.
# You will see some selling items. Scrape the details of each item(e.g. name, price, number of reviews, ...) using BeautifulSoup. 
# Save the scraped data in a text file.
# Handle errors.
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By


def Send_Request(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(e)


url = "https://webscraper.io/test-sites/e-commerce/allinone"
text = Send_Request(url)
data_frame = pd.DataFrame()


def Scrape(text:str) -> pd.DataFrame:
    soup = BeautifulSoup(text, 'html.parser')


    important_info = soup.find_all("div", class_ = 'card-body')

    ls = []
    for info in important_info:
        title = info.find("a", class_ = "title").text

        description = info.find('p', class_="description card-text").text

        price = info.find('h4', class_ = 'float-end price card-title pull-right').text

        num_of_review = info.find('p', class_='float-end review-count').text[0]
        
        rating_div = info.find('div', class_='ratings')
        p_in_div = rating_div.find_all("p")
        rating = len(p_in_div[1].find_all('span'))

        ls.append([title,description,price,num_of_review, rating])
    data_frame = pd.DataFrame(ls, columns = ['Title','Description', "Price","Review_Count",'Rating'])
    return data_frame



def Create_DataFrame(page, Item_Info):
    data_frame = Scrape(page)
    data_frame["Gadget"] = Item_Info[0]
    data_frame["Type"] = Item_Info[1]

    return data_frame


driver = webdriver.Chrome()
driver.get(url)


Side_Menu_Items = driver.find_element(By.ID, 'side-menu').find_elements(By.CLASS_NAME, 'nav-item')

for items in Side_Menu_Items[1:]:
    gadget = items.text
    items.click()
    Sub_Items = driver.find_element(By.CSS_SELECTOR, '[class*="sidebar"]').find_element(By.CSS_SELECTOR, '[class*="active"]').find_elements(By.CLASS_NAME, "nav-item")
    for sub_item in Sub_Items:
        category = sub_item.text
        sub_item.click()
        Item_Info = [gadget, category]
        temp_df = Create_DataFrame(driver.page_source, Item_Info) 
        data_frame = pd.concat([data_frame, temp_df], ignore_index=True)

        driver.back()

    driver.back()


new_column_order = ['Gadget', 'Type'] + list(data_frame.columns[:-2]) 

data_frame = data_frame[new_column_order]
data_frame = data_frame.set_index(['Gadget','Type']) 

data_frame.to_csv("Data_From_Website.txt")
