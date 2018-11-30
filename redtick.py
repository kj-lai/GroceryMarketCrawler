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
driver.get('https://shop.redtick.com/')

category = driver.find_element_by_class_name('row-sm-height').find_elements_by_css_selector('.group.col-md-1.col-sm-2.col-sm-height.col-middle')
outputs = []
for stage1 in category[1:]:
    stage1.click()
    time.sleep(2)
    main_cat = stage1.find_element_by_tag_name('h3').get_attribute('innerText')
    next_stage1 = stage1.find_elements_by_class_name('col-sm-4')
    for stage2 in next_stage1:
        mid_cat = stage2.find_element_by_tag_name('h4').get_attribute('innerText')
        next_stage2 = stage2.find_elements_by_class_name('sub')
        for stage3 in next_stage2:
            sub_url = stage3.get_attribute('href')
            sub_cat = stage3.get_attribute('innerText')
            outputs.append([main_cat, mid_cat, sub_cat, sub_url])
time.sleep(1)
driver.quit()
print('*** Process Completeed ***')
data = pd.DataFrame(outputs, columns=['main_cat', 'mid_cat', 'sub_cat', 'sub_url'])
print('Dataframe shape:\t',data.shape)
data.to_csv('redtick_category.csv',index=False)
print(data.main_cat.unique())

wanted = ['Mid-Autumn  Festival','Fresh Market','Chilled & Frozen','Bakery','Beverages','Alcohols']
data2 = data[data.main_cat.isin(wanted)].reset_index(drop=True)
print(data2.shape)
print(data2.main_cat.unique())

start_time = time.time()
driver = webdriver.Chrome()
driver.switch_to_window(driver.current_window_handle)
driver.maximize_window()
# driver.get('https://shop.redtick.com/')

item_datas = []
item_counts = []
for i, row in data2.iterrows():
    driver.get(row.sub_url)
# driver.get('https://shop.redtick.com/store/en/instant-noodle-cupbowl')
    while True:
        item_counts.append([row.main_cat, row.mid_cat, row.sub_cat ,driver.find_element_by_css_selector('.count').text.split(' ')[0]])
        item_list = driver.find_elements_by_css_selector('.col-content')
        for item in item_list:
            item_name = item.find_element_by_tag_name('h3').text
            item_price = item.find_element_by_class_name('price').text.split(' ')[0][2:]
            item_vol = item.find_element_by_class_name('unit').text
            try:
                old_price = item.find_element_by_class_name('price-strike').text.split(' ')[0][2:]   
            except:
                old_price = '0.00'
            try:
                promo = item.find_element_by_class_name('visible-lg-inline-block').text
            except:
                promo = ''
            item_datas.append([row.main_cat, row.mid_cat, row.sub_cat, item_name, item_price, item_vol, old_price, promo])
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        try:
            buttons = driver.find_element_by_class_name('pagination').find_elements_by_tag_name('a')
            if buttons[-1].get_attribute('rel') == 'next':
                buttons[-1].click()
            else:
                break;
        except:
            break;
time.sleep(1)
driver.quit()
print('*** Process Completeed ***')
print('Time used:\t',time.time()-start_time)

item_df = pd.DataFrame(item_datas, columns=['main_cat','mid_cat','sub_cat','item_name','item_price','item_vol','item_old_price','promotion'])
print('Dataframe shape:\t',item_df.shape)
item_df.to_csv('20180922_redtick_database.csv',index=False)
print(item_df.head())

count_df = pd.DataFrame(item_counts, columns=['main_cat','mid_cat','sub_cat','counts'])
count_df.counts = count_df.counts.astype('int')
print(count_df.shape)
count_df.to_csv('redtick_subcat_count.csv',index=False)