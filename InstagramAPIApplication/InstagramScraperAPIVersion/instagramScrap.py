#!/usr/bin/python
# -*- coding: utf-8 -*-
from constant import *
import argparse
import json
import requests
import os
import errno
import sys
import logging.config
from collections import OrderedDict
import codecs
from pymongo import MongoClient

client = MongoClient('localhost:27017')
db = client.instagramapidata

class InstagramScraper(object):

    """InstagramScraper scrapes """

    def __init__(self,userName,dst = None):
        self.userName = userName
        self.user_id_list =[]
        self.user_id_and_username = {}
        cwd = os.getcwd()
        self.dst = cwd+DEST if dst is None else dst

        # Set up a file logger.
        self.logger = InstagramScraper.get_logger(level=logging.DEBUG)


        self.session = requests.Session()
        self.login_user = LOGIN_USERNAME
        self.login_pass = LOGIN_PASSWORD
        self.logged_in = False

	#access_token from database
	checkcsr = db.useraccesstokeninfo.find({"username":userName})
	if(checkcsr):
	    for item in checkcsr:
		self.access_token = item.get("accesstoken")
		print "ACCESS TOKEN "
		print self.access_token

        #if self.login_user and self.login_pass:
            #self.login()


    def login(self):
        """Logs in to instagram"""
        self.session.headers.update({'Referer': BASE_URL})
        req = self.session.get(BASE_URL)

        self.session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})

        login_data = {'username': self.login_user, 'password': self.login_pass}
        login = self.session.post(LOGIN_URL, data=login_data, allow_redirects=True)
        self.session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        self.cookies = login.cookies

        if login.status_code == 200 and json.loads(login.text)['authenticated']:
            self.logged_in = True
            #print self.logged_in
        else:
            self.logger.exception('Login failed for ' + self.login_user)
            raise ValueError('Login failed for ' + self.login_user)

    def logout(self):
        """Logs out of instagram"""
        if self.logged_in:
            try:
                logout_data = {'csrfmiddlewaretoken': self.cookies['csrftoken']}
                self.session.post(LOGOUT_URL, data=logout_data)
                self.logged_in = False
            except requests.exceptions.RequestException:
                self.logger.warning('Failed to log out ' + self.login_user)



    def scrap(self,username):
        userList = self.parse_komma_separated_List(username)
        for user in userList:
            if user:
                #url = USER_SEARCH_URL.format(user)
                user_basic_Data = self.fetch_url(USER_BASIC_INFO+self.access_token)
                #print json.dumps(user_basic_Data)

                user_recent_media_Data = self.fetch_url(USER_RECENT_MEDIA_NEW_EP+self.access_token)
                #print json.dumps(user_recent_media_Data)

                #user_Data = self.fetch_url(url)
                user_data_list_all = user_basic_Data['data']
                #print url
                self.fetch_users_from_all_user_data(user_data_list_all)
                #print "succesfully parse the user id for : " + user + " "

        #self.print_dictionary(self.user_id_and_username)
        self.store_dictionary_db(self.user_id_and_username)

        ## parse the user recent media
        for userId in self.user_id_list:

            for key, value in self.user_id_and_username.items():
                if key == userId:
                    #print value
                    user = value

            print ' NOW RETRIEVING BASIC INFORMATION AND MEDIA OF   --> ' + user

            media_download_path = self.make_dst_dir(self.user_id_and_username.get(userId))
            #print media_download_path
            media_url = RECENT_MEDIA_URL.format(userId) + self.access_token
            print media_url
            user_media_url_parse = self.fetch_url(media_url)
            pagination = user_media_url_parse['pagination']
            all_media_data = user_media_url_parse['data']
            #print "The media data size" + str(len(all_media_data))
            self.fetch_users_recent_media_data(all_media_data,media_download_path,user_data_list_all)
            self.logout()

    def print_dictionary(self,dict):
        """function to print a dictionary"""
        for key, value in dict.items():
            #print "Dictinary" + key + ' -- '+ str(value)
            pass

    def store_dictionary_db(self,dict):
        """function to store userid and username in db """
        for key, value in dict.items():
            #print "Dictinary" + key + ' -- '+ str(value)
            userid = key
            username = value
            #c = InstagramScrapPipeline()
            #InstagramScrapPipeline.process_userid_name_data(c,userid.encode("UTF-8"),username.encode("UTF-8"))


    def parse_komma_separated_List(self,anyListwithkomma):
        """take komma separated userlist and returnuserlist """
        resultList=[]
        resultList = anyListwithkomma.split(",")
        return resultList

    def fetch_url(self,url):
        '''take url with username and return users information '''
        resp = self.session.get(url)
        if resp.status_code == 200:
            try:
                #shared_data = resp.text.split("window._sharedData = ")[1].split(";</script>")[0]
                #return json.loads(shared_data)['entry_data']['ProfilePage'][0]['user']
                #return json.loads(resp.text)
                return resp.json()
            except (TypeError, KeyError, IndexError):
                pass

    def fetch_users_from_all_user_data(self, userData):
        """function to create a dictionary of user id and username from userData list"""
        print userData
        userId = userData['id']
        name = userData['username']
        self.user_id_list.append(userId)
        self.user_id_and_username[userId] = name



    def fetch_users_recent_media_data(self, mediaData,path,userbasicdata):
        """function to parse users media data """
        all_data_dict = {}
        all_data_dict['userbasic']=userbasicdata
        count = 0
        all_media_dict = {}

        filepath = None
        for data in mediaData:
            media_Id = data['id']
            #type image or video
            media_type= data['type']
            #media location
            media_location = data['location']
            if media_location:
                pass
            else:
                media_location = 'No Location'

            #only scrap info for images
            if media_type == "image":
                #user information
                user_Info = data['user']
                username = data['user']['username']

                #media url information
                images = data['images']
                images_thumbnail_url = data['images']['thumbnail']['url']
                images_low_resolution_url = data['images']['low_resolution']['url']
                images_standard_resolution = data['images']['standard_resolution']['url']
                #d = InstagramUserInfo()

                #download the images
                image_path = self.download(images_standard_resolution,path)

                #caption information
                caption = data['caption']
                caption_Id = data['caption']['id']
                caption_text = data['caption']['text']
                caption_from = data['caption']['from']
                #likeInstagramUserInfo
                likes_count = data['likes']['count']
                #comments
                comments_count = data['comments']['count']
                #tags
                tag_List= data['tags']
                tag_list_as_list= self.parse_items_return_kommaseparated_list(tag_List)
                #print username + "  -- "+images_standard_resolution+ "Caption:"+caption_Id + caption_text + "TAGS : "+str(tag_list_as_list)
                #url to scrap the user list who liked or commented on the media
                comment_url = COMMENTS_MEDIA.format(media_Id) + self.access_token
                like_url = LIKE_MEDIA.format(media_Id)+self.access_token
                #comment and like data scrap using each of the user_media_url_parse
                comment_users,raw_comment_data = self.comment_info_scrap(media_Id, comment_url)
                ##Like retrive API link no more active
                ##liked_users,raw_like_data = self.like_info_scrap(media_Id, like_url)
                count = count +1

                new_json_dict = OrderedDict()
                all_data_dict['userinfo']=user_Info
                new_json_dict['mediaid'] = media_Id
                new_json_dict['medialocation'] = media_location
                new_json_dict['captiontext'] = caption_text
                new_json_dict['likes'] = likes_count
                new_json_dict['comments'] = comments_count
                new_json_dict['commentdetail'] = raw_comment_data
                new_json_dict['imagepath']=image_path
                all_data_dict[count]=new_json_dict

                fileName = username + '.json'
                cwd = os.getcwd()
                filepath = os.path.join(cwd+DEST+username,fileName)
                directory = cwd+DEST+username
                if not os.path.exists(filepath):
                    if not os.path.exists(directory):
                        os.makedirs(directory)
		with open(filepath, 'wb') as outfile:
                    json.dump(all_data_dict, codecs.getwriter('utf-8')(outfile), indent=4, sort_keys=True, ensure_ascii=False)


            else:
                print " Other media Type" + media_type
        
    def index(self,dir):

        for root, dirs, files in os.walk(dir, topdown=False):
            #for name in files:
               # print "file---"
               # print(os.path.join(root, name))
            for name in dirs:
                #print "dirs---" +name
                print(os.path.join(root, name))
                for path,direcs,files in os.walk(os.path.join(root, name)):
                    for name in files:
                        if ".txt" in name:
                            print(os.path.join(path, name))
                            with open(os.path.join(path, name), "r") as f:
                                content = f.read()
                                #print content


    def make_dst_dir(self, username):
        '''Creates the destination directory'''

        cwd = os.getcwd()

        if self.dst == cwd+DEST:
            dst = cwd+ DEST + username
        else:
            if self.retain_username:
                dst = self.dst + '/' + username
            else:
                dst = self.dst

        try:
            os.makedirs(dst)
        except OSError as err:
            if err.errno == errno.EEXIST and os.path.isdir(dst):
                # Directory already exists
                pass
            else:
                # Target dir exists as a file, or a different error
                raise

        return dst

    def download(self, url, save_dir):
        """Downloads the media file"""
        image_name = url.split('/')[-1]
        file_path = os.path.join(save_dir,image_name)




        if not os.path.isfile(file_path):
            with open(file_path, 'wb') as media_file:
                try:
                    content = self.session.get(url).content
                except requests.exceptions.ConnectionError:
                    time.sleep(5)
                    content = self.session.get(url).content

                media_file.write(content)
        return file_path

    def comment_info_scrap(self, media_Id, comment_url):
        comment_data = self.fetch_url(comment_url)['data']
        comment_data_all= self.fetch_url(comment_url)
        #print json.dumps(comment_data_all)
        user_id_and_comment_dict = {}

        for data in comment_data:
            comment_text_list =[]
            comment_Id = data['id']
            comment_text = data['text'].encode("UTF-8")
            comment_from = data['from']
            #comment_from_user_id = comment_from['id']
            comment_from_username = comment_from['username']
            #comment_from_fullname = comment_from['full_name']
            comment_text_list.append(comment_text)
            if not comment_from_username in user_id_and_comment_dict:
                user_id_and_comment_dict[comment_from_username.encode("UTF-8")] = comment_text_list
            else:
                text = user_id_and_comment_dict[comment_from_username]
                text.append(comment_text)
                user_id_and_comment_dict[comment_from_username ] = text
            #self.print_dictionary(user_id_and_comment_dict)
        return user_id_and_comment_dict,comment_data

    def like_info_scrap(self, media_Id, like_url):
        like_data = self.fetch_url(like_url)['data']
        liked_user_Id_List = []
        for data in like_data:
            liked_user_Id = data['id']
            liked_user_Id_List.append(liked_user_Id.encode("UTF-8"))
            #print "Who Liked--> " + data['id']+ "-- User " + data['username']
        #print str(liked_user_Id_List)
        return liked_user_Id_List,like_data

    def parse_items_return_kommaseparated_list(self,itemlists):
        single_list = []
        for item in itemlists:
            # adds the tag without the # character
            single_list.append(item.encode("UTF-8"))
        return single_list
    @staticmethod
    def get_logger(level=logging.WARNING, log_file='instagram-scraper.log'):
        '''Returns a file logger.'''
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.NOTSET)

        handler = logging.FileHandler(log_file, 'w')
        handler.setLevel(level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        return logger





def main():

    parser = argparse.ArgumentParser(description="instagram scraper download specific users image")
    parser.add_argument('-u',action='store', help='user name to scrap', dest = 'username')

    args = parser.parse_args()
    print args


    if args.username is None:
        parser.print_help()
        raise ValueError('Must provide username or usernames')


    scraper = InstagramScraper(args.username)
    scraper.scrap(args.username)
    #scraper.insert("comment_table",("id","text"),(110,"aabbaa"))
    #scraper.index("/Users/Shreyashi/wara/gitrepos/Instagram-Scraper-API/AllData")


if __name__ == '__main__':
    main()
