import json
import urllib.request
import numpy as np
import pandas as pd
from pandas import json_normalize
from datetime import datetime
from dateutil.relativedelta import relativedelta


other_attribbutes = ['id', 'site_id', 'title', 'price', 'sold_quantity', 
                     'seller.seller_reputation.transactions.completed', 'latitude', 'longitude', 
                     'discount', 'seller_years_active', 'seller_months_active', 'seller_days_active',
                     'item_months_published', 'item_days_published', 'item_initial_quantity']

cat_attribbutes = ['condition', 'seller.seller_reputation.power_seller_status', 
                  'seller.seller_reputation.level_id', 'address.state_name', 'shipping.mode', 
                  'available_quantity', 'item_years_published', 'DISPLAY_SIZE', 
                  'DISPLAY_TYPE', 'IS_SMART', 'RESOLUTION_TYPE', 'brand']

def attributes_parser(row):
    
    displayS_exist = False
    displayT_exist = False
    isSmart_exist = False
    resT_exist = False
    brand_exist = False
    
    try:
        if pd.isna(row['body.original_price']):
            row['has_discount'] = False
            row['discount'] = 0
        else:
            row['has_discount'] = True
            row['discount'] = (row['original_price'] - row['price']) / row['original_price']
    except:
        row['has_discount'] = False
        row['discount'] = 0
          
        
    try:
        row['latitude'] = row['body.geolocation.latitude']
        row['longitude'] = row['body.geolocation.longitude']
        
    except:
        row['latitude'] = np.nan
        row['longitude'] = np.nan
        
        
    try:
        row['city'] = row['body.seller_address.city.name']
        row['state'] = row['body.seller_address.state.name']
        
    except:
        row['city'] = ""
        row['state'] = ""
        
    
    
    attr_list = row['body.attributes']
    
    for attr in attr_list:
        
        if attr['id'] == 'BRAND':
            row['brand'] = attr['value_name'].lower()
            brand_exist = True

        if attr['id'] == 'DISPLAY_SIZE':
            
            if attr['value_struct'] != None:
                
                if attr['value_struct']['number'] < 14:
                    row['DISPLAY_SIZE'] = 10 

                elif attr['value_struct']['number'] > 14 and attr['value_struct']['number'] < 24:
                    row['DISPLAY_SIZE'] = 20

                elif attr['value_struct']['number'] > 24 and attr['value_struct']['number'] < 28:
                    row['DISPLAY_SIZE'] = 32

                elif attr['value_struct']['number'] >= 28 and attr['value_struct']['number'] <= 34:
                    row['DISPLAY_SIZE'] = 32

                elif attr['value_struct']['number'] >= 35 and attr['value_struct']['number'] <= 44:
                    row['DISPLAY_SIZE'] = 40

                elif attr['value_struct']['number'] >= 45 and attr['value_struct']['number'] <= 54:
                    row['DISPLAY_SIZE'] = 50

                elif attr['value_struct']['number'] > 54 and attr['value_struct']['number'] <= 64:
                    row['DISPLAY_SIZE'] = 60

                elif attr['value_struct']['number'] >= 65 and attr['value_struct']['number'] <= 75:
                    row['DISPLAY_SIZE'] = 75

                elif attr['value_struct']['number'] > 75:
                    row['DISPLAY_SIZE'] = 80

                else:
                    row['DISPLAY_SIZE'] = attr['value_struct']['number']

                displayS_exist = True
            

        if attr['id'] == 'DISPLAY_TYPE':
            
            if attr['value_name'] != None:
                display_t = attr['value_name'].lower()
                if display_t not in  ['led', 'crt', 'lcd', 'qled', 'plana', 'oled', 'uhd']:
                    if display_t == 'FLAT':
                        row['DISPLAY_TYPE'] = 'plana'

                    elif display_t == 'Tubo':
                        row['DISPLAY_TYPE'] = 'crt'

                    elif ('4k' in display_t ) or ('uhd' in display_t ) :
                        row['DISPLAY_TYPE'] = 'uhd'

                    else:
                        row['DISPLAY_TYPE'] = 'otro'
                else:
                    row['DISPLAY_TYPE'] = display_t
                
                
                displayT_exist = True
                    
                    

        if attr['id'] == 'IS_SMART':
            row['IS_SMART'] = attr['value_name']
            isSmart_exist = True

        if attr['id'] == 'RESOLUTION_TYPE':
            
            if attr['value_name'] != None:
                
                resolution_t = attr['value_name'].lower()

                if resolution_t not in  ['4k', 'full hd', 'hd', 'sdtv', 'wvga']:
                    if ('4k' in resolution_t ) or ('uhd' in resolution_t ) or \
                        ('3840*2160' in resolution_t ) or ('ultra hd' in resolution_t ) :
                        
                        row['RESOLUTION_TYPE'] = '4k'

                    elif '1080' in resolution_t :
                        row['RESOLUTION_TYPE'] = 'full hd'

                    elif ('768' in resolution_t) or ('720' in resolution_t) :
                        row['RESOLUTION_TYPE'] = 'hd'

                    else:
                        row['RESOLUTION_TYPE'] = 'otro'

                else:
                    row['RESOLUTION_TYPE'] = resolution_t
                    
                resT_exist = True
            
        if not displayS_exist:
            row['DISPLAY_SIZE'] = 0
            
        if not displayT_exist:
            row['DISPLAY_TYPE'] = 'otro'
            
        if not resT_exist:
            row['RESOLUTION_TYPE'] = 'otro'
            
        if not isSmart_exist:
            row['IS_SMART'] = 'otro'
            
        if not brand_exist:
            row['brand'] = 'other'



    return row


def seller_attributes(row):
    seller_addr = 'https://api.mercadolibre.com/users/'
    seller_id = str(row['body.seller_id'])
    
    with urllib.request.urlopen(seller_addr + seller_id) as seller_url:
        seller_dict = json.loads(seller_url.read().decode())
   
    row['seller.seller_reputation.transactions.completed'] = seller_dict['seller_reputation']['transactions']['completed']
    row['seller.seller_reputation.power_seller_status'] = seller_dict['seller_reputation']['power_seller_status']
    row['seller.seller_reputation.level_id'] = seller_dict['seller_reputation']['level_id']
    row['seller_registration_date'] = seller_dict['registration_date']
    
    return row


def date(row):
    s_registration_timestamp = pd.Timestamp(row['seller_registration_date']).tz_convert(None)
    row['seller_registration_year'] = s_registration_timestamp.year
    row['seller_registration_month'] = s_registration_timestamp.month
    row['seller_registration_day'] = s_registration_timestamp.month
    
    now = datetime.now()
    end_date = datetime.fromtimestamp(datetime.now().timestamp())
    try:
        #if timestamp is none
        start_date = datetime.fromtimestamp(s_registration_timestamp.timestamp())
        
        difference_in_years = relativedelta(end_date, start_date).years
        difference_in_months = relativedelta(end_date, start_date).months
        #difference_in_days = relativedelta(end_date, start_date).days

        month_diff = difference_in_years * 12 + difference_in_months

        row['seller_years_active'] = difference_in_years
        row['seller_months_active'] = month_diff

        time_diff = now - s_registration_timestamp
        row['seller_days_active'] = time_diff.days
    
    except:
        #all nan
        row['seller_years_active'] = s_registration_timestamp.year
        row['seller_months_active'] = s_registration_timestamp.year
        row['seller_days_active'] = s_registration_timestamp.year
        
        
    
    
    
    item_pub_startt = pd.Timestamp(row['publication_start_time']).tz_convert(None)
    row['item_publication_year'] = item_pub_startt.year
    row['item_publication_month'] = item_pub_startt.month
    row['item_publication_day'] = item_pub_startt.month

    try:
        #if timestamp is none
        start_date = datetime.fromtimestamp(item_pub_startt.timestamp())

        difference_in_years = relativedelta(end_date, start_date).years
        difference_in_months = relativedelta(end_date, start_date).months
        #difference_in_days = relativedelta(end_date, start_date).days

        month_diff = difference_in_years * 12 + difference_in_months

        row['item_years_published'] = difference_in_years
        row['item_months_published'] = month_diff

        time_diff = now - item_pub_startt
        row['item_days_published'] = time_diff.days

    except:
        #all nan
        row['item_years_published'] = item_pub_startt.year
        row['item_months_published'] = item_pub_startt.year
        row['item_days_published'] = item_pub_startt.year

    return row
    

   
#
# args: lista conteniendo el id de los items a clasificar
# returns: dataframe con los atributos del item
#
def get_items(items):
    
    multi_get_addr = 'https://api.mercadolibre.com/items?ids='

    n_batch = len(items) // 20
    if len(items) % 20 > 0:
        n_batch = n_batch +1

    items_df = pd.DataFrame()
    for item_batch in range(n_batch):
        items_subset = items[item_batch * 20 : (item_batch * 20) + 20]
        items_str =  ""
        for x in items_subset:
            items_str = items_str + x + ','


        with urllib.request.urlopen(multi_get_addr + items_str[:-1]) as item_url:

            item_dict = json.loads(item_url.read().decode())
            df = json_normalize(item_dict)

            if items_df.empty:
                items_df = df.copy()
            else:
                items_df = pd.concat([items_df, df], ignore_index=True)
                
                
    items_df = items_df.reset_index(drop=True)

    
    items_df = items_df.apply(attributes_parser, axis=1)
    items_df = items_df.apply(seller_attributes, axis=1)
    
    items_df = items_df.rename(columns={"body.start_time": "publication_start_time", 
                                        "body.initial_quantity": "item_initial_quantity",
                                        "body.seller_address.state.name": "address.state_name"})
    
    items_df = items_df.apply(date, axis=1)
    
    columns = list(items_df.columns)
    new_columns = []
    for column_name in columns:
        new_columns.append(column_name.replace("body.",""))
    
    items_df.columns = new_columns
    
    items_df = items_df[other_attribbutes + cat_attribbutes]
    
    
    return items_df
    
    
    
