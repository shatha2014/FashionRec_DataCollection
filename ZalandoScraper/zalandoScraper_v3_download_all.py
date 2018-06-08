#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
from bs4 import BeautifulSoup
import bs4
import codecs
import requests
import json,os
from constant import *
from collections import OrderedDict
import math
import base64
from pymongo import ASCENDING
import time
from random import shuffle
import timeit
import datetime
import matplotlib.pyplot as plt
import numpy as np



ZALANDO_DATA_SET_ALL.create_index([('id', ASCENDING)], unique=True)
ZALANDO_DATA_SEARCH_KEY_PATTERN.create_index([('id', ASCENDING)], unique=True)
ZALANDO_DATA_SEARCH_KEY_MATERIAL.create_index([('id', ASCENDING)], unique=True)
ZALANDO_DATA_SEARCH_KEY_COLLAR.create_index([('id', ASCENDING)], unique=True)

class ZalandoScraper(object):
    """ZalandoScraper scrapes and downloads different categories product infomation and images"""

def get_total_product_count(r):
    '''
    get total product number
    '''
    total_prod_count = None
    data = r.text
    soup = BeautifulSoup(data,"html.parser")
    product_count = soup.findAll('h2',{'class':'z-text cat_count-1zSG1 z-text-detail-text-regular z-text-black'})
    #total_count=soup.find_all("h2")[0].get_text()


    for prod_cnt in product_count:
        total_prod_count = prod_cnt.text
    total_prod_count = total_prod_count.replace(" ", "")
    total_prod_count = total_prod_count.replace(",", "")
    total_prod_count = int(total_prod_count.replace("products",""))

    return total_prod_count

def get_sub_category_link(r):
    '''get al sub-category link'''
    link_list =[]
    link_dict = {}
    data = r.text
    soup = BeautifulSoup(data,"html.parser")
    sub_cat_links = soup.findAll('a',{'class':'cat_tag-20vv5'})
    for link in sub_cat_links:
        html_link = link.get('href')
        link_list.append(html_link)
        cat = link.text
        link_dict[link.text] =html_link
    print link_dict
    return link_dict

def url_to_get_beauty_soup(url):
    ''' take an URL and return the soup of that URl '''
    r  = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data)
    return soup

def soup_to_get_link(soup):
    ''' Take an soup input and find all links and return a  list of all links'''
    all_link= []
    for link in soup.find_all('a'):
        all_link.append(link.get('href'))
    return all_link

def soup_to_get_script_tag(soup):
    ''' Take an soup input and find an script with id and return script text '''
    script_tag_all = soup.find('script', id='z-vegas-pdp-props')
    script_text = script_tag_all.text
    return script_text

def scripttext_toget_cdata_json(script_text,filename):
    ''' Take a script text and soup it and find all text in that soup
    and then check for CData
    and then load the content of CData in as json
    and save the articleInfo of that json '''
    get_json_soup = BeautifulSoup(script_text)
    for cd in get_json_soup.findAll(text=True):
      if isinstance(cd, bs4.CData):
          json_data = json.loads(cd)
          articleInfo = json_data['model']['articleInfo']
          with open(filename, 'w') as outfile:
            json.dump(articleInfo, codecs.getwriter('utf-8')(outfile), indent=4, sort_keys=True, ensure_ascii=False)
def return_json_data(filename):
    json_data = []
    if os.path.isfile(filename) :
        json_file = open(filename)
        json_data = json.load(json_file)
        print "----"
    return json_data
def process_json_for_required_data(readfilename,category_directory,maincategory,sub_category):
    ''' store article json data in database'''
    json_data = return_json_data(readfilename)
    new_json_dict = OrderedDict()


    article_id = json_data.get('id')
    category = json_data['category_tag']
    # create article directory
    cwd = os.getcwd()
    article_directory = category_directory +category+ "/" + article_id
    if not os.path.exists(article_directory):
        os.makedirs(article_directory)
    newfilename = os.path.join(article_directory+"/",article_id + ".json")


    new_json_dict['id'] = json_data.get('id')
    new_json_dict['item_category'] = maincategory
    new_json_dict['item_subcategory'] = sub_category
    new_json_dict['name'] = json_data.get('name')# name visible in the shopURL
    new_json_dict['brand'] = json_data['brand']['name']
    new_json_dict['shopUrl'] = json_data['shopUrl']
    new_json_dict['category_tag'] = json_data.get('category_tag')# category ex-shirt
    new_json_dict['product_group'] = json_data.get('product_group')# which product_group ex- clothing
    new_json_dict['color'] = json_data.get('color')
    new_json_dict['media'] = json_data['media']['images']# all type images
    new_json_dict['material'] = json_data['attributes'][0]['data'][0]
    new_json_dict['detailattributes'] = json_data['attributes'][1]['data']
    new_json_dict['measurefittingattributes'] = json_data['attributes'][2]['data']
    now = datetime.datetime.now()
    new_json_dict['downloaddate'] = now.strftime("%Y-%m-%d %H:%M")

    #print new_json_dict

    if os.path.exists(newfilename):
        with open(newfilename, 'w') as outfile:
            json.dump(new_json_dict, codecs.getwriter('utf-8')(outfile), indent=4, sort_keys=True, ensure_ascii=False)
    else:
        with open(newfilename, 'wb') as outfile:
            json.dump(new_json_dict, codecs.getwriter('utf-8')(outfile), indent=4, sort_keys=True, ensure_ascii=False)

    image_path_list = get_media_from_link(new_json_dict['media'],article_directory)
    #add image path list
    new_json_dict['path'] = image_path_list
    print 'Download>>> {} '.format(article_id)
    ## insert data in the MongoDB
    store_in_database(article_id, new_json_dict)




def store_in_database(article_id, json_dict):
    current_article_search = ZALANDO_DATA_SET_ALL.find({"id":article_id})
    if current_article_search.count() == 0:
        ZALANDO_DATA_SET_ALL.insert(json_dict)
        print 'Saving in  in Database '.format()
    else:
        print 'ARTICLE>>>>>  {}  ALREADY INSERTED IN DATABASE '.format(article_id)



def get_media_from_link(media_list,article_directory):
    '''process image url '''
    image_path_list = []
    for item in media_list:
        #print item['type'], item['sources']
        imageurl = item['sources']['zoom']
        imagetype = item['type']

        '''"sources": {
                "color": "https://mosaic01.ztat.net/vgs/media/pdp-color/A0/M2/1E/00/SQ/11/A0M21E00S-Q11@18.jpg",
                "colorBig": "https://mosaic01.ztat.net/vgs/media/pdp-color-big/A0/M2/1E/00/SQ/11/A0M21E00S-Q11@18.jpg",
                "colorBig2x": "https://mosaic01.ztat.net/vgs/media/pdp-color-big-2x/A0/M2/1E/00/SQ/11/A0M21E00S-Q11@18.jpg",
                "gallery": "https://mosaic01.ztat.net/vgs/media/pdp-gallery/A0/M2/1E/00/SQ/11/A0M21E00S-Q11@18.jpg",
                "reco2x": "https://mosaic01.ztat.net/vgs/media/pdp-reco-2x/A0/M2/1E/00/SQ/11/A0M21E00S-Q11@18.jpg",
                "thumb": "https://mosaic01.ztat.net/vgs/media/pdp-thumb/A0/M2/1E/00/SQ/11/A0M21E00S-Q11@18.jpg",
                "zoom": "https://mosaic01.ztat.net/vgs/media/pdp-zoom/A0/M2/1E/00/SQ/11/A0M21E00S-Q11@18.jpg"
            },
            "type": "PREMIUM"
        '''

        image_download_path = download_image_in_path(imageurl,article_directory)
        #add all the image path to the list and return it to store in the database
        image_path_list.append(image_download_path)
    return image_path_list

        #convert image in base64 binary
        #with open(image_download_path, "rb") as image_file:
            #encoded_string_pic = base64.b64encode(image_file.read())



def download_image_in_path(imageurl,article_directory):
    ''' this function takes a url and a path to download a image from  the url and save it in path
    return the new path of the image .'''

    r = requests.get(imageurl, allow_redirects=True)

    base_name = imageurl.split('/')[-1].split('?')[0]
    new_path = os.path.join(article_directory+"/",base_name)
    open(new_path, 'wb').write(r.content)

    return new_path



def scrape_sub_cat_items(category, sub_cat_name, sub_cat_url):
    ''' scrape data for a category and subcategory item'''
    total_prod_count = 0
    if sub_cat_url:
        search_url = BASE_URL+ sub_cat_url
        r  = requests.get(search_url)

        total_prod_count = get_total_product_count(r)
        print total_prod_count
        ###New product count code
        soup = url_to_get_beauty_soup(search_url)
        script_tag_all = soup.find('script', id='z-nvg-cognac-props')
        if script_tag_all:
            script_text = script_tag_all.text
            get_json_soup = BeautifulSoup(script_text)
            for cd in get_json_soup.findAll(text=True):
                if isinstance(cd, bs4.CData):
                    json_data = json.loads(cd)
                    paginationInfo = json_data['pagination']['page_count']
                    total_count = json_data['total_count']
                    print '---{}---{}'.format(paginationInfo,total_count)

                    ## for each page count loop
                    for page in range(1, paginationInfo+1):
                        new_search_url = search_url+'?p='+str(page)
                        scrape_page_product(new_search_url,category,sub_cat_name)



        ### New product count code
            print "Now scraping Total :[ "+str(total_prod_count)+"] for category: [ "+category+" ]and in subcategory:[ " + sub_cat_name+" ] "

        '''
        if total_prod_count>=84:
            print total_prod_count
            num_iteration = math.ceil(float(total_prod_count)/84)
            iteration_list = []
            for i in range(1,int(num_iteration)):#?p=5
                iteration_list.append(i)
            shuffle(iteration_list)
            while (not time.sleep(5)):
                #TODO:Need to find a break point
                current_item_count = ZALANDO_DATA_SET_ALL.find({"item_category" : category,"item_subcategory" : sub_cat_name}).count()
                if(current_item_count >= total_prod_count):
                    break
                else:
                    for i in iteration_list:
                        time.sleep(120)
                        new_search_url = search_url+'?p='+str(i)
                        scrape_page_product(new_search_url,category,sub_cat_name)
        else:#total_prod_count>8
            while (not time.sleep(5)):
                current_item_count = ZALANDO_DATA_SET_ALL.find({"item_category" : category}).count()
                if(current_item_count >= total_prod_count):
                    break
                else:
                    scrape_page_product(search_url,category,sub_cat_name)
        '''
            ## BEGIN LOOP: inside for loop to get all the products

#function to scrape item in each page
def scrape_page_product(search_url,category,sub_cat_name):
            print search_url
            soup = url_to_get_beauty_soup(search_url)
            time.sleep(50)
            all_prod_links =[]
            #prod_links = soup.findAll('a', {'class':'cat_imageLink-OPGGa'})
            #for link in prod_links:
                #time.sleep(10)
                #html_link = link.get('href')
                #full_link = BASE_URL+html_link
                #all_prod_links.append(full_link)

            ### New URl get for 84 elements add at 3rd April
            script_tag_all = soup.find('script', id='z-nvg-cognac-props')
            if script_tag_all:
                script_text = script_tag_all.text
                get_json_soup = BeautifulSoup(script_text)
                for cd in get_json_soup.findAll(text=True):
                  if isinstance(cd, bs4.CData):
                      json_data = json.loads(cd)
                      articleInfo = json_data['articles']
                      print len(articleInfo)
                      for article in articleInfo:
                          link= BASE_URL+'/'+article['url_key']+'.html'
                          all_prod_links.append(link)

            ###


            print'Will download This links>>> {}'.format(all_prod_links)

            cwd = os.getcwd()
            temp_directory = cwd+'/temp'
            if not os.path.exists(temp_directory):
                os.makedirs(temp_directory)
            #temp_file_name_4Cdata = base_name = url.split('/')[-1].split('?')[0]
            if all_prod_links:
                for each_prod_link in all_prod_links:
                    #create a temp file name
                    temp_file_name_4Cdata = base_name = each_prod_link.split('/')[-1].split('?')[0]

                    #check current article existance
                    search_id = temp_file_name_4Cdata.split('.')[0].split('-')
                    article_id = search_id[-2]+'-'+search_id[-1]
                    article_id = article_id.upper()
                    current_article_exist = ZALANDO_DATA_SET_ALL.find({"id":article_id}).count()
                    if(current_article_exist == 0):
                        temp_file_name_4Cdata = temp_file_name_4Cdata.replace(".html", "")
                        temp_file_name_4Cdata = temp_directory+"/"+temp_file_name_4Cdata+".txt"
                        #print temp_file_name_4Cdata
                        #search for the 'script' element in html
                        soup = url_to_get_beauty_soup(each_prod_link)
                        script_tag_all = soup.find('script', id='z-vegas-pdp-props')
                        if script_tag_all:
                            script_text = script_tag_all.text
                            scripttext_toget_cdata_json(script_text,temp_file_name_4Cdata)
                            main_category = category
                            cwd = os.getcwd()
                            category_directory = str(cwd) + "/"+main_category
                            if not os.path.exists(category_directory):
                                os.makedirs(category_directory)
                            process_json_for_required_data(temp_file_name_4Cdata,category_directory+"/",category,sub_cat_name)
                            ##TODO:Remove Temp file
                            os.remove(temp_file_name_4Cdata)
                    else:
                        pass




def main():
    # Ask for data to scrape from Zalando
    option = raw_input(" Enter '1' to scrape items for 'Blouse & Tunic' and \n "
                       "'2' to scrape items for  'Dresses' and \n "
                       "'3' to scrape items for 'Coats' and \n "
                       "'4'  to scrape items for 'Jeans'  and \n "
                       "'5'  to scrape items for 'Jackets'  and \n "
                       "'6'  to scrape items for 'Jumpers and Cardigans' and \n "
                       "'7'  to scrape items for 'Skirts'  and \n "
                       "'8'  to scrape items for 'Tops and T-shirts' and\n  "
                       "'9'  to scrape items for 'Tight and Socks' and \n "
                       "'10'  to scrape items for 'Trousers and Shorts' and \n "
                       "'11'  to scrape items for 'Shoes'  and \n "
                       "'12'  to scrape items for 'Bags' \n "
                       "'13'  to count product for each category\n  "
                       "'14'  search by different options \n "
                       "'15'  searzch by different options \n ")
    if(option == '1'):
        print('Scrape Blouse And Tunic')
        url = BLOUSEAND_TUNIC
        r  = requests.get(url)

        # 1. get the subcategory lists for this category
        sub_cat_dic = get_sub_category_link(r)

        # 2. give user option to select subcategory
        cat_name = []
        cat_link = []
        print type(sub_cat_dic)

        for k in sub_cat_dic:
            cat_name.append(k)
            cat_link.append(sub_cat_dic[k])
        print cat_name,cat_link
        option2 = raw_input(" Enter '1' to scrape items for 'Blouse'  and \n "
                       " '2' to scrape items for  'Shirt' and \n "
                       " '3' to scrape items for 'Tunic' and \n "
                       " '4' to scrape all Item for Blouse & Tunics  \n")
        if(option2 == '1'):
            sub_cat_link = sub_cat_dic['Blouses']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Blouse And Tunic', 'Blouses', sub_cat_link)

        elif(option2 == '2'):
            sub_cat_link = sub_cat_dic['Shirts']
            print sub_cat_link
            scrape_sub_cat_items('Blouse And Tunic', 'Shirts', sub_cat_link)

        elif(option2 == '3'):
            sub_cat_link = sub_cat_dic['Tunics']
            print sub_cat_link
            scrape_sub_cat_items('Blouse And Tunic', 'Tunics', sub_cat_link)

        else:
            # 3. get the total product count
            total_prod_count = get_total_product_count(r)
            print total_prod_count
            #TODO: make change in the fuction to scrape all data




    if(option == '2'):
        print('Scrape Dresses')
        url = DRESSES
        r  = requests.get(url)


        # 1. get the subcategory lists for this category
        sub_cat_dic = get_sub_category_link(r)

        # 2. give user option to select subcategory
        cat_name = []
        cat_link = []
        print type(sub_cat_dic)

        for k in sub_cat_dic:
            cat_name.append(k)
            cat_link.append(sub_cat_dic[k])
        print cat_name,cat_link
        option2dress = raw_input(" Enter '1' to scrape items for 'Casual Dress'  and \n "
                       " '2' to scrape items for  'Cocktail Dresses' and \n "
                       " '3' to scrape items for 'Denim Dresses' and \n "
                       " '4' to scrape items for 'Knitted Dresses' and \n "
                       " '5' to scrape items for 'Jersey Dresses' and \n "
                       " '6' to scrape items for 'Maxi Dresses'and \n  "
                       " '7' to scrape items for 'Shirt Dresses'and \n  "
                       " '8' to scrape items for 'Work Dresses'and \n  "
                       " '9' to scrape all Item for 'Dresses' \n")
        '''[u'Work Dresses', u'Denim Dresses', u'Casual Dresses',
         u'Shirt Dresses', u'Cocktail Dresses', u'Knitted Dresses', u'Maxi Dresses', u'Jersey Dresses']'''
        if(option2dress == '1'):
            sub_cat_link = sub_cat_dic['Casual Dresses']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Dresses', 'Casual Dresses', sub_cat_link)

        elif(option2dress == '2'):
            sub_cat_link = sub_cat_dic['Cocktail Dresses']
            print sub_cat_link
            scrape_sub_cat_items('Dresses', 'Cocktail Dresses', sub_cat_link)

        elif(option2dress == '3'):
            sub_cat_link = sub_cat_dic['Denim Dresses']
            print sub_cat_link
            scrape_sub_cat_items('Dresses', 'Denim Dresses', sub_cat_link)
        elif(option2dress == '4'):
            sub_cat_link = sub_cat_dic['Knitted Dresses']
            print sub_cat_link
            scrape_sub_cat_items('Dresses', 'Knitted Dresses', sub_cat_link)

        elif(option2dress == '5'):
            sub_cat_link = sub_cat_dic['Jersey Dresses']
            print sub_cat_link
            scrape_sub_cat_items('Dresses', 'Jersey Dresses', sub_cat_link)
        elif(option2dress == '6'):
            sub_cat_link = sub_cat_dic['Maxi Dresses']
            print sub_cat_link
            scrape_sub_cat_items('Dresses', 'Maxi Dresses', sub_cat_link)

        elif(option2dress == '7'):
            sub_cat_link = sub_cat_dic['Shirt Dresses']
            print sub_cat_link
            scrape_sub_cat_items('Dresses', 'Shirt Dresses', sub_cat_link)
        elif(option2dress == '8'):
            sub_cat_link = sub_cat_dic['Work Dresses']
            print sub_cat_link
            scrape_sub_cat_items('Dresses', 'Work Dresses', sub_cat_link)

        else:
            # 3. get the total product count
            total_prod_count = get_total_product_count(r)
            print total_prod_count
            #TODO: make change in the fuction to scrape all data
    ##End of Dresses if condition

    if(option == '3'):
        print('Scrape Coats ')
        url = COATS
        r  = requests.get(url)


        # 1. get the subcategory lists for this category
        sub_cat_dic = get_sub_category_link(r)

        # 2. give user option to select subcategory
        cat_name = []
        cat_link = []
        print type(sub_cat_dic)

        for k in sub_cat_dic:
            cat_name.append(k)
            cat_link.append(sub_cat_dic[k])
        print cat_name,cat_link
        option2coat = raw_input(" Enter '1' to scrape items for 'Down Coats '  and \n "
                       " '2' to scrape items for  'Parkas ' and \n "
                       " '3' to scrape items for 'Short Coats' and \n "
                       " '4' to scrape items for 'Trench Coats' and \n "
                       " '5' to scrape items for 'Winter Coats' and \n "
                       " '6' to scrape items for 'Wool Coats'and \n  "
                       " '7' to scrape all Item for 'Coats' \n")
        '''{u'Down Coats': u'/womens-clothing-coats-down-coats/', u'Winter Coats': u'/womens-clothing-coats-winter-coats/',
         u'Wool Coats': u'/womens-clothing-coats-wool-coats/',u'Short Coats': u'/womens-clothing-coats-short-coats/',
         u'Trench Coats': u'/womens-clothing-coats-trench-coats/', u'Parkas': u'/womens-clothing-coats-parkas/'}'''

        if(option2coat == '1'):
            sub_cat_link = sub_cat_dic['Down Coats']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Coats', 'Down Coats', sub_cat_link)

        elif(option2coat == '2'):
            sub_cat_link = sub_cat_dic['Parkas']
            print sub_cat_link
            scrape_sub_cat_items('Coats', 'Parkas', sub_cat_link)
        elif(option2coat == '3'):
            sub_cat_link = sub_cat_dic['Short Coats']
            print sub_cat_link
            scrape_sub_cat_items('Coats', 'Short Coats', sub_cat_link)

        elif(option2coat == '4'):
            sub_cat_link = sub_cat_dic['Trench Coats']
            print sub_cat_link
            scrape_sub_cat_items('Coats', 'Trench Coats', sub_cat_link)

        elif(option2coat == '5'):
            sub_cat_link = sub_cat_dic['Winter Coats']
            print sub_cat_link
            scrape_sub_cat_items('Coats', 'Winter Coats', sub_cat_link)

        elif(option2coat == '6'):
            sub_cat_link = sub_cat_dic['Wool Coats']
            print sub_cat_link
            scrape_sub_cat_items('Coats', 'Wool Coats', sub_cat_link)
        else:
            # 3. get the total product count
            total_prod_count = get_total_product_count(r)
            print total_prod_count
            #TODO: make change in the fuction to scrape all data

    ##End of if condition for Coats

    if(option =='4'):
        print('Scrape Jeans ')
        url = JEANS
        r  = requests.get(url)

        # 1. get the subcategory lists for this category
        sub_cat_dic = get_sub_category_link(r)

        # 2. give user option to select subcategory
        cat_name = []
        cat_link = []

        for k in sub_cat_dic:
            cat_name.append(k)
            cat_link.append(sub_cat_dic[k])
        print cat_name,cat_link
        option2jeans = raw_input(" Enter '1' to scrape items for 'Flares '  and \n "
                       " '2' to scrape items for  'Skinny Fit ' and \n "
                       " '3' to scrape items for 'Bootcut' and \n "
                       " '4' to scrape items for 'Denim Shorts' and \n "
                       " '5' to scrape items for 'Loose Fit' and \n "
                       " '6' to scrape items for 'Slim Fit'and \n  "
                       " '7' to scrape items for 'Straight Leg'and \n"
                       " '8' to scrape all Item for 'Jeans' \n")
        '''{u'Denim Shorts': u'/denim-shorts/', u'Slim Fit': u'/womens-clothing-jeans-slim-fit/', u'Skinny Fit': u'/womens-clothing-jeans-skinny-fit/',
        u'Flares': u'/womens-clothing-jeans-flares/', u'Straight Leg': u'/womens-clothing-jeans-straight-leg/',
         u'Loose Fit': u'/womens-clothing-jeans-loose-fit/', u'Bootcut': u'/womens-clothing-jeans-bootcut/'}'''
        if(option2jeans == '1'):
            sub_cat_link = sub_cat_dic['Flares']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Jeans', 'Flares', sub_cat_link)

        elif(option2jeans == '2'):
            sub_cat_link = sub_cat_dic['Skinny Fit']
            print sub_cat_link
            scrape_sub_cat_items('Jeans', 'Skinny Fit', sub_cat_link)
        elif(option2jeans == '3'):
            sub_cat_link = sub_cat_dic['Bootcut']
            print sub_cat_link
            scrape_sub_cat_items('Jeans', 'Bootcut', sub_cat_link)

        elif(option2jeans == '4'):
            sub_cat_link = sub_cat_dic['Denim Shorts']
            print sub_cat_link
            scrape_sub_cat_items('Jeans', 'Denim Shorts', sub_cat_link)

        elif(option2jeans == '5'):
            sub_cat_link = sub_cat_dic['Loose Fit']
            print sub_cat_link
            scrape_sub_cat_items('Jeans', 'Loose Fit', sub_cat_link)

        elif(option2jeans == '6'):
            sub_cat_link = sub_cat_dic['Slim Fit']
            print sub_cat_link
            scrape_sub_cat_items('Jeans', 'Slim Fit', sub_cat_link)
        elif(option2jeans == '7'):
            sub_cat_link = sub_cat_dic['Straight Leg']
            print sub_cat_link
            scrape_sub_cat_items('Jeans', 'Straight Leg', sub_cat_link)

        else:
            # 3. get the total product count
            total_prod_count = get_total_product_count(r)
            print total_prod_count
            #TODO: make change in the fuction to scrape all data

    ##End of if condition for Jeans
    if(option =='5'):
        print('Scrape Jackets ')
        url = JACKETS
        r  = requests.get(url)

        # 1. get the subcategory lists for this category
        sub_cat_dic = get_sub_category_link(r)

        # 2. give user option to select subcategory
        cat_name = []
        cat_link = []

        for k in sub_cat_dic:
            cat_name.append(k)
            cat_link.append(sub_cat_dic[k])
        print cat_name,cat_link
        '''{u'Winter Jackets': u'/womens-clothing-jackets-winter-jackets/', u'Athletic Jackets': u'/womens-clothing-jackets-athletic-jackets/',
         u'Fleece Jackets': u'/womens-clothing-jackets-fleeces/', u'Leather Jackets': u'/womens-clothing-jackets-leather-jackets/',
         u'Denim Jackets': u'/womens-clothing-jackets-denim-jackets/', u'Outdoor Jackets': u'/womens-waterproof-jackets/',
         u'Gilets & Waistcoats': u'/womens-clothing-jackets-gilets-waistcoats/', u'Lightweight Jackets': u'/womens-clothing-jackets-lightweight-jackets/',
         u'Blazers': u'/womens-clothing-jackets-blazers/',
         u'Down Jackets': u'/womens-clothing-jackets-down-jackets/', u'Capes': u'/womens-clothing-jackets-capes/'}
        '''


        option2jackets = raw_input(" Enter '1' to scrape items for 'Athletic Jackets '  and \n "
                       " '2' to scrape items for  'Leather Jackets ' and \n "
                       " '3' to scrape items for 'Denim Jackets' and \n "
                       " '4' to scrape items for 'Lightweight Jackets' and \n "
                       " '5' to scrape items for 'Blazers' and \n "
                       " '6' to scrape items for 'Gilets & Waistcoats'and \n  "
                       " '7' to scrape items for 'Capes'and \n"
                       " '8' to scrape items for 'Down Jackets'and \n"
                       " '9' to scrape items for 'Fleece Jackets'and \n"
                       " '10' to scrape items for 'Outdoor Jackets'and \n"
                       " '11' to scrape all Item for 'Winter Jackets' \n")

        if(option2jackets == '1'):
            sub_cat_link = sub_cat_dic['Athletic Jackets']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Jackets', 'Athletic Jackets', sub_cat_link)
        elif(option2jackets == '2'):
            sub_cat_link = sub_cat_dic['Leather Jackets']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Jackets', 'Leather Jackets', sub_cat_link)
        elif(option2jackets == '3'):
            sub_cat_link = sub_cat_dic['Denim Jackets']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Jackets', 'Denim Jackets', sub_cat_link)
        elif(option2jackets == '4'):
            sub_cat_link = sub_cat_dic['Lightweight Jackets']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Jackets', 'Lightweight Jackets', sub_cat_link)

        elif(option2jackets == '5'):
            sub_cat_link = sub_cat_dic['Blazers']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Jackets', 'Blazers', sub_cat_link)
        elif(option2jackets == '6'):
            sub_cat_link = sub_cat_dic['Gilets & Waistcoats']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Jackets', 'Gilets & Waistcoats', sub_cat_link)
        elif(option2jackets == '7'):
            sub_cat_link = sub_cat_dic['Capes']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Jackets', 'Capes', sub_cat_link)
        elif(option2jackets == '8'):
            sub_cat_link = sub_cat_dic['Down Jackets']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Jackets', 'Down Jackets', sub_cat_link)
        elif(option2jackets == '9'):
            sub_cat_link = sub_cat_dic['Fleece Jackets']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Jackets', 'Fleece Jackets', sub_cat_link)
        elif(option2jackets == '10'):
            sub_cat_link = sub_cat_dic['Outdoor Jackets']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Jackets', 'Outdoor Jackets', sub_cat_link)
        elif(option2jackets == '11'):
            sub_cat_link = sub_cat_dic['Winter Jackets']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Jackets', 'Winter Jackets', sub_cat_link)

        else:
            # 3. get the total product count
            total_prod_count = get_total_product_count(r)
            print total_prod_count
            #TODO: make change in the fuction to scrape all data
    ##End of if condition for Jackets

    if(option =='6'):
        print('Scrape Jumper And Cargigans ')
        url = JUMPER_AND_CARDIGAN
        r  = requests.get(url)

        # 1. get the subcategory lists for this category
        sub_cat_dic = get_sub_category_link(r)

        # 2. give user option to select subcategory
        cat_name = []
        cat_link = []

        for k in sub_cat_dic:
            cat_name.append(k)
            cat_link.append(sub_cat_dic[k])
        print cat_name,cat_link
        '''{u'Athletic Jackets': u'/womens-clothing-athletic-jackets/', u'Hoodies': u'/womens-clothing-hoodies/',
        u'Sweatshirts': u'/womens-clothing-sweatshirts/', u'Fleece Jumpers': u'/womens-clothing-fleece-jumpers/',
        u'Cardigans': u'/womens-clothing-cardigans/', u'Jumpers': u'/womens-clothing-jumpers/'}'''


        option2jumper = raw_input(" Enter '1' to scrape items for 'Athletic Jackets '  and \n "
                       " '2' to scrape items for  'Hoodies' and \n "
                       " '3' to scrape items for 'Sweatshirt' and \n "
                       "'4' to scrape items for 'Fleece Jumpers ' and \n"
                       " '5' to scrape items for 'Cardigans' and \n "
                       " '6' to scrape items for 'Jumpers'and \n  "
                       " '7' to scrape all Item for 'Jumper And Cardigans' \n")

        if(option2jumper == '1'):
            sub_cat_link = sub_cat_dic['Athletic Jackets']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Jumper And Cardigans', 'Athletic Jackets', sub_cat_link)

        elif(option2jumper == '2'):
            sub_cat_link = sub_cat_dic['Hoodies']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Jumper And Cardigans', 'Hoodies', sub_cat_link)
        elif(option2jumper == '3'):
            sub_cat_link = sub_cat_dic['Sweatshirts']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Jumper And Cardigans', 'Sweatshirts', sub_cat_link)
        elif(option2jumper == '4'):
            sub_cat_link = sub_cat_dic['Fleece Jumpers']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Jumper And Cardigans', 'Fleece Jumpers', sub_cat_link)
        elif(option2jumper == '5'):
            sub_cat_link = sub_cat_dic['Cardigans']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Jumper And Cardigans', 'Cardigans', sub_cat_link)
        elif(option2jumper == '6'):
            sub_cat_link = sub_cat_dic['Jumpers']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Jumper And Cardigans', 'Jumpers', sub_cat_link)
        else:
            # 3. get the total product count
            total_prod_count = get_total_product_count(r)
            print total_prod_count
            #TODO: make change in the fuction to scrape all data
    ##End of if condition for Jumpers and Cardigans
    if(option =='7'):
        print('Scrape Skirts ')
        url = SKIRTS
        r  = requests.get(url)

        # 1. get the subcategory lists for this category
        sub_cat_dic = get_sub_category_link(r)

        # 2. give user option to select subcategory
        cat_name = []
        cat_link = []

        for k in sub_cat_dic:
            cat_name.append(k)
            cat_link.append(sub_cat_dic[k])
        print cat_name,cat_link
        '''{u'Maxi Skirts': u'/womens-clothing-maxi-skirts/', u'Pleated Skirts': u'/womens-clothing-pleated-skirts/',
        u'A-Line Skirts': u'/womens-clothing-a-line-skirts/', u'Pencil Skirts': u'/womens-clothing-pencil-skirts/',
        u'Mini Skirts': u'/womens-clothing-mini-skirts/',
        u'Denim Skirts': u'/womens-clothing-denim-skirts/', u'Leather Skirts': u'/womens-clothing-leather-skirts/'}'''

        option2skirt = raw_input(" Enter '1' to scrape items for 'Maxi Skirts'  and \n "
                       " '2' to scrape items for  'Pleated Skirts' and \n "
                       " '3' to scrape items for 'Denim Skirts ' and \n "
                       " '4' to scrape items for 'Leather skirts' and \n "
                       " '5' to scrape items for 'Bubble Hem Skirts' and \n "
                       " '6' to scrape items for 'A-Line Skirts'and \n  "
                       " '7' to scrape items for 'Pencil Skirts'and \n"
                       " '8' to scrape items for 'Mini Skirts'and \n"
                       " '9' to scrape all Item for 'Skirts' \n")

        if(option2skirt == '1'):
            sub_cat_link = sub_cat_dic['Maxi Skirts']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Skirts', 'Maxi Skirts', sub_cat_link)
        elif(option2skirt == '2'):
            sub_cat_link = sub_cat_dic['Pleated Skirts']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Skirts', 'Pleated Skirts', sub_cat_link)
        elif(option2skirt == '3'):
            sub_cat_link = sub_cat_dic['Denim Skirts']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Skirts', 'Denim Skirts', sub_cat_link)
        elif(option2skirt == '4'):
            sub_cat_link = sub_cat_dic['Leather Skirts']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Skirts', 'Leather Skirts', sub_cat_link)
        elif(option2skirt == '5'):
            sub_cat_link = sub_cat_dic['Bubble Hem Skirts']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Skirts', 'Bubble Hem Skirts', sub_cat_link)
        elif(option2skirt == '6'):
            sub_cat_link = sub_cat_dic['A-Line Skirts']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Skirts', 'A-Line Skirts', sub_cat_link)
        elif(option2skirt == '7'):
            sub_cat_link = sub_cat_dic['Pencil Skirts']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Skirts', 'Pencil Skirts', sub_cat_link)
        elif(option2skirt == '8'):
            sub_cat_link = sub_cat_dic['Mini Skirts']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Skirts', 'Mini Skirts', sub_cat_link)
        else:
            # 3. get the total product count
            total_prod_count = get_total_product_count(r)
            print total_prod_count
            #TODO: make change in the fuction to scrape all data
    ##End of if condition for Skirts
    if(option =='8'):
        print('Scrape Tops and T-shirts')
        url = TOPS_AND_TSHIRTS
        r  = requests.get(url)

        # 1. get the subcategory lists for this category
        sub_cat_dic = get_sub_category_link(r)

        # 2. give user option to select subcategory
        cat_name = []
        cat_link = []

        for k in sub_cat_dic:
            cat_name.append(k)
            cat_link.append(sub_cat_dic[k])
        print cat_name,cat_link
        '''{u'Long Sleeve Tops': u'/womens-clothing-tops-long-sleeve-tops/',
        u'Vest Tops': u'/womens-clothing-tops-tops/',
         u'Polo Shirts': u'/womens-clothing-tops-polo-shirts/',
        u'T-Shirts': u'/womens-clothing-tops-t-shirts/'}'''
        option2tops = raw_input(" Enter '1' to scrape items for 'Long Sleeve Tops'  and \n "
                       " '2' to scrape items for  'Vest Tops' and \n "
                       " '3' to scrape items for 'Polo Shirts' and \n "
                       " '4' to scrape items for 'T-Shirts' and \n "
                       " '5' to scrape all Item for 'Tops & Tshirt' \n ")

        if(option2tops == '1'):
            sub_cat_link = sub_cat_dic['Long Sleeve Tops']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Tops And Tshirts', 'Long Sleeve Tops', sub_cat_link)

        elif(option2tops == '2'):
            sub_cat_link = sub_cat_dic['Vest Tops']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Tops And Tshirts', 'Vest Tops', sub_cat_link)
        elif(option2tops == '3'):
            sub_cat_link = sub_cat_dic['Polo Shirts']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Tops And Tshirts', 'Polo Shirts', sub_cat_link)

        elif(option2tops == '4'):
            sub_cat_link = sub_cat_dic['T-Shirts']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Tops And Tshirts', 'T-Shirts', sub_cat_link)
        else:
            total_prod_count = get_total_product_count(r)
            print total_prod_count
            #TODO: make change in the fuction to scrape all data
    ##End of if condition for Tops And T-shirts
    if(option =='9'):
        print('Scrape Tight And Socks ')
        url = TIGHT_AND_SOCKS
        r  = requests.get(url)

        # 1. get the subcategory lists for this category
        sub_cat_dic = get_sub_category_link(r)

        # 2. give user option to select subcategory
        cat_name = []
        cat_link = []

        for k in sub_cat_dic:
            cat_name.append(k)
            cat_link.append(sub_cat_dic[k])
        print cat_name,cat_link
        '''{u'Suspenders': u'/womens-clothing-tights-socks-suspenders/',
        u'Thigh High Socks': u'/thigh-high-socks/',
         u'Tights': u'/tights/',
         u'Socks': u'/socks/',
          u'Knee High Socks': u'/knee-high-socks/',
         u'Leggings': u'/leggings/',
         u'Sports Socks': u'/sports-socks/',
         u'Leg Warmers': u'/warmers/'}'''
        option2skirt = raw_input(" Enter '1' to scrape items for 'Knee High Socks'  and \n "
                       " '2' to scrape items for  'Leggings' and \n "
                       " '3' to scrape items for 'Socks' and \n "
                       " '4' to scrape items for 'Thigh High Socks' and \n "
                       " '5' to scrape items for 'Tights' and \n "
                       " '6' to scrape all Item for 'Tight & Socks' \n")

        if(option2skirt == '1'):
            sub_cat_link = sub_cat_dic['Knee High Socks']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Tight And Socks', 'Knee High Socks', sub_cat_link)
        elif(option2skirt == '2'):
            sub_cat_link = sub_cat_dic['Leggings']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Tight And Socks', 'Leggings', sub_cat_link)
        elif(option2skirt == '3'):
            sub_cat_link = sub_cat_dic['Socks']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Tight And Socks', 'Socks', sub_cat_link)
        elif(option2skirt == '4'):
            sub_cat_link = sub_cat_dic['Thigh High Socks']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Tight And Socks', 'Thigh High Socks', sub_cat_link)
        elif(option2skirt == '5'):
            sub_cat_link = sub_cat_dic['Tights']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Tight And Socks', 'Tights', sub_cat_link)

        else:
            total_prod_count = get_total_product_count(r)
            print total_prod_count
            #TODO: make change in the fuction to scrape all data
    ##End of if condition for Tops And T-shirts
    if(option =='10'):
        print('Scrape Trousers and Shorts')
        url = TROUSER_AND_SHORTS
        r  = requests.get(url)

        # 1. get the subcategory lists for this category
        sub_cat_dic = get_sub_category_link(r)

        # 2. give user option to select subcategory
        cat_name = []
        cat_link = []

        for k in sub_cat_dic:
            cat_name.append(k)
            cat_link.append(sub_cat_dic[k])
        print cat_name,cat_link
        '''{u'Joggers & Sweats': u'/womens-clothing-joggers-sweats/',
        u'Shorts': u'/womens-clothing-shorts/',
         u'Chinos': u'/womens-clothing-chinos/',
         u'Playsuits & Jumpsuits': u'/womens-clothing-playsuits-jumpsuits/',
         u'Leggings': u'/womens-clothing-leggings/',
         u'Trousers': u'/womens-clothing-trousers/'}
        '''
        option2trouser = raw_input(" Enter '1' to scrape items for 'Chinos'  and \n "
                       " '2' to scrape items for  'Joggers ans Sweats' and \n "
                       " '3' to scrape items for 'Leggings' and \n "
                       " '4' to scrape items for 'Playsuit and Jumpsuits' and \n "
                       " '5' to scrape items for 'Shorts' and \n "
                       " '6' to scrape items for 'Trousers' and \n "
                       " '7' to scrape all Item for 'Trousers and Shorts' \n")

        if(option2trouser == '1'):
            sub_cat_link = sub_cat_dic['Chinos']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Trouser And Shorts', 'Chinos', sub_cat_link)
        elif(option2trouser == '2'):
            sub_cat_link = sub_cat_dic['Joggers & Sweats']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Trouser And Shorts', 'Joggers & Sweats', sub_cat_link)
        elif(option2trouser == '3'):
            sub_cat_link = sub_cat_dic['Leggings']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Trouser And Shorts', 'Leggings', sub_cat_link)
        elif(option2trouser == '4'):
            sub_cat_link = sub_cat_dic['Playsuits & Jumpsuits']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Trouser And Shorts', 'Playsuits & Jumpsuits', sub_cat_link)
        elif(option2trouser == '5'):
            sub_cat_link = sub_cat_dic['Shorts']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Trouser And Shorts', 'Shorts', sub_cat_link)
        elif(option2trouser == '6'):
            sub_cat_link = sub_cat_dic['Trousers']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Trouser And Shorts', 'Trousers', sub_cat_link)
        else:
            total_prod_count = get_total_product_count(r)
            print total_prod_count
            #TODO: make change in the fuction to scrape all data
    ##End of if condition for Trousers and Shorts
    if(option =='11'):
        print('Scrape Shoes')
        url = SHOES
        r  = requests.get(url)

        # 1. get the subcategory lists for this category
        sub_cat_dic = get_sub_category_link(r)

        # 2. give user option to select subcategory
        cat_name = []
        cat_link = []

        for k in sub_cat_dic:
            cat_name.append(k)
            cat_link.append(sub_cat_dic[k])
        print cat_name,cat_link
        '''{u'Sports Shoes': u'/womens-sports-shoes/',
        u'Flip Flops & Beach Shoes': u'/flip-flops-beach-shoes/',
        u'Ballet Pumps': u'/womens-shoes-ballet-pumps/',
         u'Flats & Lace-Ups': u'/womens-shoes-flats-lace-ups/',
         u'Boots': u'/womens-shoes-boots/',
          u'Trainers': u'/womens-shoes-trainers/',
          u'Outdoor Shoes': u'/womens-outdoor-shoes/',
           u'Heels': u'/womens-shoes-heels/',
           u'Sandals': u'/womens-shoes-sandals/',
            u'Ankle Boots': u'/womens-shoes-ankle-boots/',
            u'Slippers': u'/womens-shoes-slippers/',
         u'Mules & Clogs': u'/womens-shoes-mules-clogs/'}
        '''
        option2shoes = raw_input(" Enter '1' to scrape items for 'Ankle Boots'  and \n "
                       " '2' to scrape items for  'Ballet Pumps' and \n "
                       " '3' to scrape items for 'Boots' and \n "
                       " '4' to scrape items for 'Flats & Lace-Ups' and \n "
                       " '5' to scrape items for 'Flip Flops & Beach Shoes' and \n "
                       " '6' to scrape items for 'Heels' and \n "
                        " '7' to scrape items for 'Mules & Clogs' and \n "
                        " '8' to scrape items for 'Outdoor Shoes' and \n "
                        " '9' to scrape items for 'Sports Shoes' and \n "
                        " '10' to scrape items for 'Slippers' and \n "
                        " '11' to scrape items for 'Trainers' and \n "
                        " '12' to scrape items for 'Sandals' and \n "
                       " '13' to scrape all Item for 'Shoes' \n")

        if(option2shoes == '1'):
            sub_cat_link = sub_cat_dic['Ankle Boots']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Shoes', 'Ankle Boots', sub_cat_link)

        elif(option2shoes == '2'):
            sub_cat_link = sub_cat_dic['Ballet Pumps']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Shoes', 'Ballet Pumps', sub_cat_link)
        elif(option2shoes == '3'):
            sub_cat_link = sub_cat_dic['Boots']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Shoes', 'Boots', sub_cat_link)
        elif(option2shoes == '4'):
            sub_cat_link = sub_cat_dic['Flats & Lace-Ups']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Shoes', 'Flats & Lace-Ups', sub_cat_link)
        elif(option2shoes == '5'):
            sub_cat_link = sub_cat_dic['Flip Flops & Beach Shoes']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Shoes', 'Flip Flops & Beach Shoes', sub_cat_link)
        elif(option2shoes == '6'):
            sub_cat_link = sub_cat_dic['Heels']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Shoes', 'Heels', sub_cat_link)
        elif(option2shoes == '7'):
            sub_cat_link = sub_cat_dic['Mules & Clogs']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Shoes', 'Mules & Clogs', sub_cat_link)
        elif(option2shoes == '8'):
            sub_cat_link = sub_cat_dic['Outdoor Shoes']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Shoes', 'Outdoor Shoes', sub_cat_link)
        elif(option2shoes == '9'):
            sub_cat_link = sub_cat_dic['Sports Shoes']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Shoes', 'Sports Shoes', sub_cat_link)

        elif(option2shoes == '10'):
            sub_cat_link = sub_cat_dic['Slippers']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Shoes', 'Slippers', sub_cat_link)
        elif(option2shoes == '11'):
            sub_cat_link = sub_cat_dic['Trainers']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Shoes', 'Trainers', sub_cat_link)
        elif(option2shoes == '12'):
            sub_cat_link = sub_cat_dic['Sandals']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Shoes', 'Sandals', sub_cat_link)
        else:
            total_prod_count = get_total_product_count(r)
            print total_prod_count
            #TODO: make change in the fuction to scrape all data
    ##End of if condition for Shoes

    if(option =='12'):
        print('Scrape Bags')
        url = BAGS
        r  = requests.get(url)

        # 1. get the subcategory lists for this category
        sub_cat_dic = get_sub_category_link(r)

        # 2. give user option to select subcategory
        cat_name = []
        cat_link = []

        for k in sub_cat_dic:
            cat_name.append(k)
            cat_link.append(sub_cat_dic[k])
        print cat_name,cat_link
        '''
        {u'Phone Cases': u'/phone-cases/',
         u'Wash bags': u'/wash-bags/', u'Handbags': u'/handbags/',
         u'Tote Bags': u'/shopping-bags/',
          u'Sport- & Travel Bags': u'/sports-travel-bags/',
          u'Laptop Bags': u'/laptop-bags/',
           u'Shoulder Bags': u'/shoulder-bags/',
         u'Rucksacks': u'/rucksacks/',
          u'Clutch Bags': u'/clutch-bags/'}
        '''
        option2bag = raw_input(" Enter '1' to scrape items for 'Clutch Bags'  and \n "
                       " '2' to scrape items for  'Hand Bags' and \n "
                       " '3' to scrape items for 'Tote Bags' and \n "
                       " '4' to scrape items for 'Shoulder Bags' and \n "
                       " '5' to scrape items for 'Rucksacks' and \n "
                       " '6' to scrape items for 'Sport & Travel Bag' and \n "
                        " '7' to scrape items for 'Laptop Bag' and \n "
                       )

        if(option2bag == '1'):
            sub_cat_link = sub_cat_dic['Clutch Bags']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Bags', 'Clutch Bags', sub_cat_link)
        elif(option2bag == '2'):
            sub_cat_link = sub_cat_dic['Handbags']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Bags', 'Handbags', sub_cat_link)
        elif(option2bag == '3'):
            sub_cat_link = sub_cat_dic['Tote Bags']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Bags', 'Tote Bags', sub_cat_link)
        elif(option2bag == '4'):
            sub_cat_link = sub_cat_dic['Shoulder Bags']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Bags', 'Shoulder Bags', sub_cat_link)
        elif(option2bag == '5'):
            sub_cat_link = sub_cat_dic['Rucksacks']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Bags', 'Rucksacks', sub_cat_link)
        elif(option2bag == '6'):
            sub_cat_link = sub_cat_dic['Sport- & Travel Bags']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Bags', 'Sport- & Travel Bags', sub_cat_link)
        elif(option2bag == '7'):
            sub_cat_link = sub_cat_dic['Laptop Bags']
            print sub_cat_link
            #calling function to do scrape on  sub_cat_link for Blouses
            scrape_sub_cat_items('Bags', 'Laptop Bags', sub_cat_link)
        else:
            total_prod_count=get_total_product_count()
            print total_prod_count
            #TODO: make change in the fuction to scrape all data
    ##End of if condition for Bags
    if (option == '13'):
        category_list = ['Blouse And Tunic','Dresses','Coats','Jeans','Jackets','Jumper And Cardigans','Skirts','Tops And Tshirts','Tight And Socks','Trouser And Shorts','Shoes','Bags']
        cwd = os.getcwd()
        for cat in category_list:
            files = folders = 0
            path = cwd +'/'+cat+'/'
            if os.path.exists(path):
                for _, dirnames, filenames in os.walk(path):
                    # ^ this idiom means "we won't be using this value"
                    files += len(filenames)
                    folders += len(dirnames)
                #print path,files,folders

        for cat in category_list:
            item_count_csr = ZALANDO_DATA_SET_ALL.find({'item_category':cat}).count()

            print 'Item-Category: [ {} ]      >>> Count :[ {} ]'.format(cat, item_count_csr)
            if (cat == 'Blouse And Tunic'):
                subcat_list_blouses = ['Blouses', 'Shirts', 'Tunic']
                for subcat in subcat_list_blouses:
                    count = get_item_count(cat, subcat)
                    str = '[' + subcat + ']'
                    print'     {}      >>> Count :[ {} ]'.format(str, count)

            elif (cat == 'Dresses'):
                subcat_list_dresses = ['Work Dresses', 'Denim Dresses', 'Casual Dresses','Shirt Dresses', 'Cocktail Dresses', 'Knitted Dresses', 'Maxi Dresses', 'Jersey Dresses']
                for subcat in subcat_list_dresses:
                    count = get_item_count(cat, subcat)
                    str = '[' + subcat + ']'
                    print'     {}      >>> Count :[ {} ]'.format(str, count)

            elif (cat == 'Coats'):
                subcat_list_coats = ['Down Coats', 'Winter Coats',  'Wool Coats', 'Short Coats','Trench Coats', 'Parkas']
                for subcat in subcat_list_coats:
                    count = get_item_count(cat, subcat)
                    str = '[' + subcat + ']'
                    print'     {}      >>> Count :[ {} ]'.format(str, count)

            elif (cat == 'Jeans'):
                subcat_list_jeans = ['Denim Shorts', 'Slim Fit',  'Skinny Fit', 'Flares','Straight Leg', 'Loose Fit', 'Bootcut']
                for subcat in subcat_list_jeans:
                    count = get_item_count(cat, subcat)
                    str = '[' + subcat + ']'
                    print'     {}      >>> Count :[ {} ]'.format(str, count)

            elif (cat == 'Jackets'):

                subcat_list_jackets = ['Winter Jackets', 'Athletic Jackets',  'Fleece Jackets', 'Leather Jackets','Denim Jackets', 'Outdoor Jackets', 'Gilets & Waistcoats', 'Lightweight Jackets','Blazers','Down Jackets', 'Capes']
                for subcat in subcat_list_jackets:
                    count = get_item_count(cat, subcat)
                    str = '[' + subcat + ']'
                    print'     {}      >>> Count :[ {} ]'.format(str, count)

            elif(cat == 'Jumper And Cardigans'):

                subcat_list_jumper = ['Athletic Jackets', 'Hoodies', 'Sweatshirts', 'Fleece Jumpers', 'Cardigans',
                                     'Jumpers']
                for subcat in subcat_list_jumper:
                    count = get_item_count(cat, subcat)
                    str = '[' + subcat + ']'
                    print'     {}      >>> Count :[ {} ]'.format(str, count)

            elif(cat == 'Skirts'):
                # Skirts
                subcat_list_skirt = ['Maxi Skirts', 'Pleated Skirts', 'A-Line Skirts', 'Pencil Skirts','Mini Skirts','Denim Skirts','Leather Skirts']
                for subcat in subcat_list_skirt:
                    count = get_item_count(cat, subcat)
                    str = '[' + subcat + ']'
                    print'     {}      >>> Count :[ {} ]'.format(str, count)


            elif(cat == 'Tops And Tshirts'):
                subcat_list_top = ['Long Sleeve Tops', 'Vest Tops','Polo Shirts', 'T-Shirts']
                for subcat in subcat_list_top:
                    count = get_item_count(cat,subcat)
                    str = '['+subcat+']'
                    print'     {}      >>> Count :[ {} ]'.format(str, count)
            elif(cat =='Shoes'):
                subcat_list_shoes = ['Sports Shoes', 'Flip Flops & Beach Shoes', 'Ballet Pumps','Flats & Lace-Ups', 'Boots','Trainers', 'Outdoor Shoes','Heels', 'Sandals','Ankle Boots', 'Slippers','Mules & Clogs']
                for subcat in subcat_list_shoes:
                    count = get_item_count(cat,subcat)
                    str = '['+subcat+']'
                    print '     {}      >>> Count :[ {} ]'.format(str, count)
            elif(cat == 'Bags'):
                subcat_list_bag =['Tote Bags', 'Sport- & Travel Bags', 'Laptop Bags', 'Shoulder Bags',
                 'Rucksacks', 'Clutch Bags']
                for subcat in subcat_list_bag:
                    count = get_item_count(cat,subcat)
                    str = '['+subcat+']'
                    print '     {}      >>> Count :[ {} ]'.format(str, count)
            elif(cat == 'Trouser And Shorts'):
                subcat_list_trouser = ['Joggers & Sweats','Shorts','Chinos','Playsuits & Jumpsuits','Leggings','Trousers']
                for subcat in subcat_list_trouser:
                    count = get_item_count(cat,subcat)
                    str = '['+subcat+']'
                    print '     {}      >>> Count :[ {} ]'.format(str, count)
            elif(cat == 'Tight And Socks'):
                subcat_list_tight = ['Knee High Socks','Leggings','Socks','Thigh High Socks','Tights','Tight & Socks']
                for subcat in subcat_list_tight:
                    count = get_item_count(cat,subcat)
                    str = '['+subcat+']'
                    print '     {}      >>> Count :[ {} ]'.format(str, count)


    ## Different serch options
    if (option == '14'):
        print '14'
        option2search = raw_input(" Enter '1' to search by 'Pattern' \n"
                       " '2' to search by 'Collar' and \n "
                       " '3' to search by 'Brand' and \n "
                       " '4' to search by 'Color' and \n "
                       " '5' to search by 'Material'and \n  "
                       " '7' to scrape all Item for 'Coats' \n")

        if(option2search == '1'):
            option2pattern = raw_input(" Enter pattern name [animal print,camouflage,checked,colour gradient,colourful, floral, herringbone,marl, paisley,photo print, printstriped,plain,striped] \n ")
            option2item = raw_input(" Enter item category[Dresses,blouses&tunics, coats]")
            items = get_item_cat_pattern(option2item,option2pattern)
        if(option2search == '2'):
            option2collar = raw_input(" Enter collar name [backless,boat neck,button down,cache-coeur,contrast collar, cowl neck, cup-shaped collar, envelop, henley, high collar, hood, lapel collar, low round neck, low v-neck, mandarin collar, mao collar, off-the-shoulder, peter pan collar, polo neck, polo shirt, round neck, shawl collar, shirt collar, square neck, turn-down collar] \n ")
            option2item = raw_input(" Enter item category[Dresses,blouses&tunics, coats]")
            items = get_item_cat_collar(option2item,option2collar)

        if(option2search == '3'):
            option2brand = raw_input(" Enter brand name [ Aaiko, Abercrombie & Fitch, ADIA, addidas Originals] \n ")
            option2item = raw_input(" Enter item category[Dresses,blouses&tunics, coats]")
            items = get_item_cat_brand(option2item,option2brand)


        if(option2search == '4'):
            option2color = raw_input(" Enter color name [black, brown,beige,grey,white,blue,petrol,turquoise,green,olive,yellow,orange,red,pink, lilac,gold,silver,multi-coloured] \n ")
            option2item = raw_input(" Enter item category[Dresses,blouses&tunics, coats]")
            items = get_item_cat_color(option2item,option2color)
        if(option2search == '5'):
            option2material = raw_input(" Enter material name [Braided,Cashmere,cord,cotton,crocheted,denim,imitation leather, jersey, lace,leather,] \n ")
            option2item = raw_input(" Enter item category[Dresses,blouses&tunics, coats]")
            items = get_item_cat_material(option2item,option2material)
    #sort to different collection
    if (option == '15'):

        #for item in PATTERN:
        items = ZALANDO_DATA_SET_ALL.find()
        pat_list = []
        neck_list =[]
        #print
        total = 0
        total2=0
        for item in items:
            attributes =  item.get('detailattributes')
            article_id = item.get('id')
            current_article_search = ZALANDO_DATA_SEARCH_KEY_MATERIAL.find({"id":article_id})

            '''
            1. insert data to 'pattern' from 'detailattributes'
            
            '''
            current_article_search = ZALANDO_DATA_SEARCH_KEY_PATTERN.find({"id":article_id})

            for attribute in attributes:
                if(attribute.get('name') == 'Pattern'):
                    current_pattern = attribute['values'].lower()
                    total = total + 1
                    if current_pattern not in pat_list:
                        pat_list.append(current_pattern)
                    item.update({'pattern':current_pattern})
                    if current_article_search.count() == 0:
                        ZALANDO_DATA_SEARCH_KEY_PATTERN.insert(item)


            '''2. insert material to 'materialupdate' from the dict 
                 "material": {
                 "name": "Outer fabric material", 
                "values": "100% polyester" }
            '''
            material = item.get('material')
            if (material.get('name')=='Outer fabric material'):
                print material.get('values')
                item.update({'materialupdate':material.get('values')})
                if current_article_search.count() == 0:
                    ZALANDO_DATA_SEARCH_KEY_MATERIAL.insert(item)

            '''
            3. insert data to 'collar' from 'detailattributes'
                
            '''
            attributes =  item.get('detailattributes')
            article_id = item.get('id')
            for attribute in attributes:
                if(attribute.get('name') == 'Neckline' ):
                    current_neck = attribute['values'].lower()
                    if current_neck not in neck_list:
                        neck_list.append(current_neck)
                    item.update({'collartype':current_neck})
                    if current_article_search.count() == 0:
                        ZALANDO_DATA_SEARCH_KEY_COLLAR.insert(item)




def get_item_cat_pattern(cat, pattern):
    print cat, pattern
    match_item_list = []
    items = ZALANDO_DATA_SET_ALL.find({'item_category': cat})

    for item in items:
        attributes =  item.get('detailattributes')
        print attributes
        #article_id = item.get('id')
        for attribute in attributes:
            if(attribute.get('name') == 'Pattern'):
                if pattern in attribute['values'].lower():
                    print attribute
                    match_item_list.append(item)
                    #current_article_search = ZALANDO_DATA_SEARCH_KEY_PATTERN.find({"id":article_id})
                    #if current_article_search.count() == 0:
                        #item.update({'searchkey':cat+'.'+pattern})
                        #ZALANDO_DATA_SEARCH_KEY_PATTERN.insert(item)
                    break
    #print ZALANDO_DATA_SEARCH_KEY_PATTERN.find({'searchkey':cat+'.'+pattern}).count()
    print len(match_item_list)

def get_item_cat_collar(cat, collar):
    print cat, collar+'collar'
    match_item_list = []
    items = ZALANDO_DATA_SET_ALL.find({'item_category': cat})
    for item in items:
        attributes =  item.get('detailattributes')

        for attribute in attributes:
            if(attribute.get('name') == 'Collar') or (attribute.get('name') == 'Neckline'):
                if collar in attribute['values'].lower():
                    print attribute
                    match_item_list.append(item)
                    break
    print len(match_item_list)

def get_item_cat_brand(cat, brand):
    print cat, brand

    match_item_list = []
    items = ZALANDO_DATA_SET_ALL.find({'item_category': cat})
    for item in items:
        itm_brand  =  item.get('brand')
        if brand.lower() in itm_brand.lower():
            match_item_list.append(item)
    print len(match_item_list)


def get_item_cat_color(cat,color):
    print cat, color
    items = ZALANDO_DATA_SET_ALL.find({'item_category': cat,'color': color})
    print items.count()

def get_item_cat_material(cat,material):
    print cat, material

    match_item_list = []
    items = ZALANDO_DATA_SET_ALL.find({'item_category': cat})
    for item in items:
        itm_materials =  item.get('material')
        if material.lower() in itm_materials['values']:
            print itm_materials
            match_item_list.append(item)

    print len(match_item_list)

def get_item_count(cat, subcat):
    count = ZALANDO_DATA_SET_ALL.find({'item_category': cat, 'item_subcategory': subcat}).count()
    return count


if __name__ == '__main__':
    start = timeit.default_timer()
    main()
    #Your statements here

    stop = timeit.default_timer()

    print stop - start
