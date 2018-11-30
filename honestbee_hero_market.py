from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import pandas as pd
import numpy as np

start_time = time.time()
driver = webdriver.Chrome()
driver.switch_to_window(driver.current_window_handle)
driver.maximize_window()
driver.get('https://www.honestbee.my/en/groceries/stores/hero-market')

# GET LINKS FOR EACH-SUB CATEGORY
category = driver.find_elements_by_class_name('_3d-zCcjQD-_pBtgcchlLJ6')
outputs = []
for stage1 in category:
    main = stage1.find_elements_by_tag_name('a')[0]
    main_name = main.get_attribute('innerText')
    main_url = main.get_attribute('href')
    a_urls = stage1.find_elements_by_tag_name('a')[1:]
    for stage2 in a_urls:
        sub_url = stage2.get_attribute('href')
        sub = stage2.find_elements_by_tag_name('span')       
        sub_name = sub[0].get_attribute('innerText')
        sub_count = sub[1].get_attribute('innerText')
        outputs.append([main_name, sub_name, sub_count, sub_url])
time.sleep(1)
driver.quit()
print('*** Process Completeed ***')
print('Time used:\t',time.time()-start_time)

data = pd.DataFrame(outputs, columns=['main_cat', 'sub_cat', 'counts', 'sub_url'])
data.counts = data.counts.astype('int')
print('Dataframe shape:\t',data.shape)
data.to_csv('honestbee_hero_market_category.csv',index=False)
print(data.main_cat.unique())

wanted = ['Special Bundles','Fresh Vegetables','Fresh Fruits','Fresh Meat','Fresh Seafood',\
          'Dairy, Eggs & Chilled Food','Dry Grocery','Drinks','Frozen Food']
data2 = data[data.main_cat.isin(wanted)].reset_index(drop=True)
print(data2.shape)
print(data2.main_cat.unique())

start_time = time.time()
driver = webdriver.Chrome()
driver.switch_to_window(driver.current_window_handle)
driver.maximize_window()
driver.get('https://www.honestbee.my/en/groceries/stores/hero-market')

### EXTRACT DATA FROM EACH SUB PAGES
item_datas = []
for i, row in data2.iterrows():
	driver.get(row.sub_url)
	try:
	    if int(row.counts) > 48:
	        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	        time.sleep(2)
	    if int(row.counts) > 96:
	        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	        time.sleep(2)
	    buttons = driver.find_elements_by_tag_name('button')
	    for button in buttons:
	    	if button.find_element_by_tag_name('span').get_attribute('innerText') == 'LOAD MORE':
	    		checkpoint = button
	    while True:
	        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	        time.sleep(2)
	        checkpoint.click()
	        time.sleep(2)              
	except:
	    items = driver.find_elements_by_class_name('XaRs403S_a6U7-8Wfu_c3')
	    for stage3 in items:
	        price = stage3.find_element_by_class_name('_23g1UkP8VGFqvGuLjUsc-H').get_attribute('innerText')
	        name = stage3.find_element_by_class_name('_2UCShViKs8ydkfj-XuvUhM').get_attribute('innerText')
	        try:
	            volume = stage3.find_element_by_class_name('_3MvGCVMGqgv4KoGQ2wGzfk').get_attribute('innerText')
	        except:
	            volume = ''
	        try:
	            old_price = stage3.find_element_by_css_selector('del._1cBPpMK9Rz7AJ9O6CEdCsE').get_attribute('innerText')
	        except:
	            old_price = ''
	        extra = stage3.find_elements_by_css_selector('div._3zMyJ5m6V3lSUseYIe-Rqr')
	        if len(extra) == 1:
	            try:
	                out_of_stock = ''
	                saved_price = extra[0].find_element_by_tag_name('strong').get_attribute('innerText')
	            except:
	                out_of_stock = extra[0].get_attribute('innerText')
	                saved_price = ''
	        elif len(extra) >= 1:
	            out_of_stock = extra[0].get_attribute('innerText')
	            saved_price = extra[1].find_element_by_tag_name('strong').get_attribute('innerText') 
	        else:
	            out_of_stock = ''
	            saved_price = ''
	        item_datas.append([row.main_cat, row.sub_cat, name, price[2:], volume, old_price[2:], out_of_stock, saved_price[2:]])
	time.sleep(1)
driver.quit()
print('*** Process Completeed ***')
print('Time used:\t',time.time()-start_time)

item_df = pd.DataFrame(item_datas, columns=['main_cat','sub_cat','item_name','item_price','item_vol','item_old_price','description','saved_price'])
print('Dataframe shape:\t',item_df.shape)
item_df.to_csv('20180918_honestbee_hero_market_database.csv',index=False)
item_df.head()