from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import numpy as np

start_time = time.time()
driver = webdriver.Chrome()
driver.switch_to_window(driver.current_window_handle)
driver.maximize_window()
driver.get('https://eshop.tesco.com.my/groceries/en-GB/')
# driver.find_element_by_css_selector('.menu-tree mq-l--menu-tree--open')
# GET LINKS FOR EACH-SUB CATEGORY
category = driver.find_elements_by_class_name('menu__item--superdepartment')
wanted = ['Fresh Food','Grocery','Chilled & Frozen','Drinks']
outputs = []
for stage1 in category:
    main_cat = stage1.text.split('\n')[1]
    if main_cat in wanted:
        stage1.click()
        inner1 = stage1.find_elements_by_class_name('menu__item--department')
        for stage2 in inner1[1:]:
            sub_cat = stage2.text.split('\n')[1]
            stage2.click()
            inner2 = stage2.find_elements_by_class_name('menu__item--aisle')
            for stage3 in inner2[1:]:
                aisle = stage3.text.split('\n')[1]
                url = stage3.find_element_by_tag_name('a').get_attribute('href')
                outputs.append([main_cat, sub_cat, aisle, url])
time.sleep(1)
driver.quit()
print('*** Process Completeed ***')
print('Time used:\t',time.time()-start_time)

data = pd.DataFrame(outputs, columns=['main_cat', 'sub_cat', 'aisle', 'url'])
print('Dataframe shape:\t',data.shape)
data.to_csv('tesco_category.csv',index=False)
print(data.main_cat.unique())

start_time = time.time()
driver = webdriver.Chrome()
driver.switch_to_window(driver.current_window_handle)
driver.maximize_window()
driver.get('https://eshop.tesco.com.my/groceries/en-GB/')

item_datas = []
item_counts = []
errors = []
for i, row in data.iloc[185:].iterrows():
    driver.get(row.url)
    count = int(driver.find_element_by_class_name('pagination__results-count').find_elements_by_tag_name('strong')[-1].text.split(' ')[0])
    item_counts.append(count)
    ### CLICK THROUGH ALL THE PAGES
    while True:   
        item_list = driver.find_elements_by_css_selector('.product-list--list-item')
        if len(item_list) == count:
            break
        driver.find_elements_by_css_selector('.prev-next')[1].click()
        time.sleep(4)
    ### GATHER THE ITEM AND EXTRACT DATA
    for n in item_list:
        name = n.find_element_by_css_selector('.product-tile--title').get_attribute('innerText')
        price = n.find_element_by_class_name('price-per-quantity-weight').get_attribute('innerText')
        temp = price.split('/')
        try:
            promo = n.find_element_by_class_name('offer-text').get_attribute('innerText')
            promo_date = n.find_element_by_css_selector('span.dates').get_attribute('innerText')
        except:
            promo = ''
            promo_date = ''
        item_datas.append([row.main_cat, row.sub_cat, row.aisle, name, temp[0], temp[1], promo, promo_date])
time.sleep(1)
driver.quit()
print('*** Process Completeed ***')
print('Time used:\t',time.time()-start_time)

item_df = pd.DataFrame(item_datas, columns=['main_cat','sub_cat','aisle','item_name','item_price','item_metric','promo','promo_date'])
print('Dataframe shape:\t',item_df.shape)
item_df.to_csv('20180911_tesco_database.csv',index=False)
item_df.head()