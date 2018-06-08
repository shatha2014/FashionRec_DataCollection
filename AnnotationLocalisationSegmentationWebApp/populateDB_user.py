#!/usr/bin/python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError,CursorNotFound
import random,json,os
from PIL import Image
from bson.binary import Binary
import base64,requests
import codecs
import re
from flask import Flask
import config
import itertools
import random
from werkzeug.security import generate_password_hash
from pymongo import ASCENDING

from operator import itemgetter


annotation_app = Flask(__name__)
annotation_app.config.from_object(config)
imageidBase64BinaryDataCollection = annotation_app.config['IMAGEID_AND_BASE64_BINARY_DATA_COLLECTION']
textAnalysisDataCollection = annotation_app.config['IMAGEID_TEXT_ANALYSIS_DATA_COLLECTION']
##size = 100,100


def convert_images_to_binary(cursor):
    '''
    :param cursor:
    :return:
    function to convert images in base64 binary data and insert in database
    '''
    # read the existing file to get all image id
    cwd = os.getcwd()
    filename = os.path.join(str(cwd)+"/annotation_webapp/static/appdata","all_image_base64binary_data.json")
    json_imageid_list = []
    json_imageid_set = set()
    json_data = return_json_data(filename)

    # create thumbnail directory
    thumbnail_directory = str(cwd) + "/thumbnailDirectory"
    if not os.path.exists(thumbnail_directory):
        os.makedirs(thumbnail_directory)

    if(json_data):
        for item in json_data:
            imageid = item.get("imageid")
            json_imageid_list.append(imageid)
        print len(json_imageid_list)
        json_imageid_set = set(json_imageid_list)
        print "SET" + str(len(json_imageid_set))


    # all_image_base64binary_data
    imageid_base64binary_list = []

    for item in cursor:
        imageid_base64binary_dict = {}
        imageid = item.get("id")
        url = item.get("display_url")
        path = item.get("imagepath")


        if imageid not in json_imageid_set:
            print ' adding {} '.format(imageid)
            if(os.path.exists(path)):
                file_name = path.split('/')
                image_file_name_with_jpg = file_name[-1]
                image_file_name = image_file_name_with_jpg.split('.')[-2]
                print image_file_name[-1]
                im = Image.open(path)
                #im.thumbnail(size)
                # io = StringIO.StringIO()
                # im.save(io, format='JPEG')
                thumbnail_filename = os.path.join(str(cwd) + "/thumbnailDirectory/", image_file_name + "_thumbnail.jpg")
                print thumbnail_filename
                im.save(thumbnail_filename, im.format)

                with open(path, "rb") as image_file:
                    encoded_string_pic = base64.b64encode(image_file.read())

            else:
                file_name = path.split('/')
                image_file_name_with_jpg = file_name[-1]
                image_file_name = image_file_name_with_jpg.split('.')[-2]
                print image_file_name[-1]
                im = Image.open(path)
                #im.thumbnail(size)
                # io = StringIO.StringIO()
                # im.save(io, format='JPEG')
                thumbnail_filename = os.path.join(str(cwd) + "/thumbnailDirectory/", image_file_name + "_thumbnail.jpg")
                print thumbnail_filename
                #im.save(thumbnail_filename, im.format)

                new_path = download_image_in_path(url,path)
                with open(new_path, "rb") as image_file:
                    encoded_string_pic = base64.b64encode(image_file.read())

            if(encoded_string_pic):
                imageid_base64binary_dict["imageid"] = imageid
                imageid_base64binary_dict["base64binary"] = encoded_string_pic
                imageid_base64binary_list.append(imageid_base64binary_dict)

                #insert binary image data in database as json file could not save this large amount of data
                check_existance = imageidBase64BinaryDataCollection.find({"_id": imageid})
                if(check_existance.count()>0):
                    print 'Binary Data exist for imageid {}'.format(imageid)
                else:
                    imageidBase64BinaryDataCollection.insert({"_id": imageid, "base64binary": encoded_string_pic})


        else:
            print " already added"

    #print  ' {} -- '.format(imageid_base64binary_list)
    save_json(imageid_base64binary_list,filename)

    return imageid_base64binary_list

def download_image_in_path(url,path):
    ''' this function takes a url and a path to download a image from  the url and save it in path.
     Actually this function downloads those images that may be corrupt or didnt download while we ran instagra-scraper'''

    r = requests.get(url, allow_redirects=True)
    #img = Image.open(StringIO(r.content))
    base_name = url.split('/')[-1].split('?')[0]
    seperator_str = path.split('/')
    del seperator_str[-1]
    new_path ='/'.join(seperator_str)
    new_path = new_path+'/'+base_name
    #print new_path
    open(new_path, 'wb').write(r.content)

    return new_path

def return_json_data(filename):
    json_data = []
    if os.path.isfile(filename) :
        json_file = open(filename)
        json_data = json.load(json_file)
        print "----"
    return json_data

def save_json(data, dst='./'):
    ''' This function save data in the dst filename -if the file exists then append the data
    else create new file and add json data
    '''
    #if the file exists then append data
    if os.path.isfile(dst) :
        json_file = open(dst)
        json_data_file1 = json.load(json_file)
        #total number of post  is the total media item in json file
        total_data1 = len(json_data_file1)
        if total_data1 >0:
            for each_item in data:
                json_data_file1.append(each_item)
            with open(dst, 'wb') as f:
                json.dump(json_data_file1, codecs.getwriter('utf-8')(f), indent=4, sort_keys=True, ensure_ascii=False)

    #else create new file and add json data
    else:
        with open(dst, 'wb') as f:
            json.dump(data, codecs.getwriter('utf-8')(f), indent=4, sort_keys=True, ensure_ascii=False)


def main():

    # Connect to the DB
    #collection = MongoClient()["annotatorwebapp"]["users"]
    annotatorCollection = annotation_app.config['ANNOTATION_USERS_COLLECTION']
    instagramUserCollection = annotation_app.config['DATABASE_INSTAGRAM_USER']

    # Ask for data to store, delete and assign data
    option = raw_input(
        " Enter '1' to create user(atleast 5 user) and "
        "'2' for remove user (using Username) and"
        
        "'4' for remove all annotators image and "
        "'5' for image conversion  and"
        " '7' to get the liketoknowit link and "
        "'8' to insert tes_analysis data in database "
        "'9' to count each users comment data in database ")

    if(option == '1'):
        #take username and password

        user = raw_input("Enter your username: ")
        password = raw_input("Enter your password: ")
        pass_hash = generate_password_hash(password, method='pbkdf2:sha256')

        # Insert the user in the DB
        try:
            annotatorCollection.insert({"_id": user, "password": pass_hash})
            print "User created."
        except DuplicateKeyError:
            print "User already present in DB."
    if(option== '2'):
        # Delete the user from the DB
        user = raw_input("Enter your username to delete user: ")

        try:
            annotatorCollection.remove({"_id": user})
            print "User deleted."

        except CursorNotFound:
            print 'User didnt found in DB.'

    if(option== '3'):
        # Assign the annotator the instagram user data and keep image id in IMAGE_ANNOTATION_COLLECTION
        annotatorCollection = annotation_app.config['ANNOTATION_USERS_COLLECTION']
        annotatorCursor = annotatorCollection.find()
        totalAnnotatorCount = annotatorCursor.count()
        annotationIdCollection = annotation_app.config['ANNOTATE_DETAIL_IAMGEID_USER_COLLECTION']

        print totalAnnotatorCount
        commonCount = annotation_app.config['COMMON_COUNT']

        # Check the annotator user is equal or greater tha common number
        if(totalAnnotatorCount >= commonCount):
            allInstagramUserCursor = annotation_app.config['INSTAGRAM_ALL_USER_ID_COLLECTION'].find()
            # get each users total image and calculate annotaotor assigned image
            for instaUser in allInstagramUserCursor:
                instaUserName = instaUser['username']
                liketkit = annotation_app.config['INSTAGRAM_LIKETKIT_USER_COLLECTION'].find({'username':instaUserName})
                if(liketkit.count()>0):
                    totalImageUser = liketkit.count()
                    #assign_image_count(instaUserName,liketkit,totalImageUser,totalAnnotatorCount,annotatorCursor)
                    create_assignment_images(instaUserName,liketkit,totalImageUser,totalAnnotatorCount,annotatorCursor)

                else:
                    swedish = annotation_app.config['INSTAGRAM_SWEDISH_USER_COLLECTION'].find({'username':instaUserName})
                    totalImageUser = swedish.count()
                    #assign_image_count(instaUserName,swedish,totalImageUser,totalAnnotatorCount,annotatorCursor)
                    create_assignment_images(instaUserName,swedish,totalImageUser,totalAnnotatorCount,annotatorCursor)

            annotator_list =[]
            for ann in annotatorCursor:
                annotator_list.append(ann['_id'])

            for a in annotator_list:
                c = annotationIdCollection.find({"annotatorusername": a})
                print 'annotator :{}  Total assigned images:{}'.format(a,c.count())

    if(option== '4'):
        ##remove  all annotators image a
        annotatorCollection = annotation_app.config['ANNOTATION_USERS_COLLECTION']
        #annotationIdCollection = annotation_app.config['ANNOTATION_USER_IAMGEID_COLLECTION']

        #annotator_cursor = annotatorCollection.find()
        #for a in annotator_cursor :
            #print a["_id"]
            #c = annotationIdCollection.remove({"_id": a["_id"]})
            #print c
        annotationIdCollection = annotation_app.config['ANNOTATE_DETAIL_IAMGEID_USER_COLLECTION']
        annotator_cursor = annotatorCollection.find()
        for a in annotator_cursor :
            c = annotationIdCollection.remove({"annotatorusername": a["_id"]})
            print c


    if (option == '5'):
        #image conversion to base64 binary
        annotatorCollection = annotation_app.config['ANNOTATION_USERS_COLLECTION']
        annotatorCursor = annotatorCollection.find()
        totalAnnotatorCount = annotatorCursor.count()
        annotationIdCollection = annotation_app.config['ANNOTATE_DETAIL_IAMGEID_USER_COLLECTION']

        #print totalAnnotatorCount
        commonCount = annotation_app.config['COMMON_COUNT']


        # Check the annotator user is equal or greater tha common number
        if(totalAnnotatorCount >= commonCount):
            allInstagramUserCursor = annotation_app.config['INSTAGRAM_ALL_USER_ID_COLLECTION'].find()
            # get each users total image and calculate annotaotor assigned image
            #all_users_imageid_base64binary_list = []
            for instaUser in allInstagramUserCursor:
                instaUserName = instaUser['username']
                liketkit = annotation_app.config['INSTAGRAM_LIKETKIT_USER_COLLECTION'].find({'username':instaUserName})
                if(liketkit.count()>0):
                    totalImageUser = liketkit.count()
                    print 'TOTAL LTKIT ----- {} {} '.format(instaUserName,totalImageUser)
                    if(instaUserName == 'shortstoriesandskirts'):
                        print 'GOTTTTTTTTTTTTT'
                        imageid_base64binary_list = convert_images_to_binary(liketkit)

                else:
                    swedish = annotation_app.config['INSTAGRAM_SWEDISH_USER_COLLECTION'].find({'username':instaUserName})
                    totalImageUser = swedish.count()
                    print 'TOTAL SWEDISH -----  {}   {} '.format(instaUserName,totalImageUser)
                    #imageid_base64binary_list = convert_images_to_binary(swedish)

            #all_users_imageid_base64binary_list= all_users_imageid_base64binary_list + imageid_base64binary_list
            cwd = os.getcwd()
            filename = os.path.join(str(cwd)+"/annotation_webapp/static/appdata","all_image_base64binary_data.json")
            print filename
            all_users_imageid_base64binary_list =return_json_data(filename)
            print len(all_users_imageid_base64binary_list)

            #imageidBase64BinaryDataCollection = annotation_app.config['IMAGEID_AND_BASE64_BINARY_DATA_COLLECTION']
            #for each_data in all_users_imageid_base64binary_list:
               # imageid = each_data.get("imageid")
                #base64binary = each_data.get("base64binary")
                #imageidBase64BinaryDataCollection.insert({"_id":imageid,"base64binary":base64binary})

    if(option== '7'):
        #get the liketoknowit link
        allInstagramUserCursor = annotation_app.config['INSTAGRAM_ALL_USER_ID_COLLECTION'].find()
        # get each users total image and calculate annotaotor assigned image
        all_users_imageid_base64binary_list = []
        for instaUser in allInstagramUserCursor:
            instaUserName = instaUser['username']
            liketkit = annotation_app.config['INSTAGRAM_LIKETKIT_USER_COLLECTION'].find({'username':instaUserName})
            if(liketkit.count()>0):
                totalImageUser = liketkit.count()
                print 'TOTAL LTKIT ----- {} {} '.format(instaUserName,totalImageUser)
                store_liketokit_linkin_json_file(liketkit)

            else:
                swedish = annotation_app.config['INSTAGRAM_SWEDISH_USER_COLLECTION'].find({'username':instaUserName})
                totalImageUser = swedish.count()
                print 'TOTAL SWEDISH -----  {}   {} '.format(instaUserName,totalImageUser)

    if(option== '8'):
        #process text analysis data
        process_text_analysis_data()
    if (option == '9'):
        #Count each users comment data in database
        allInstagramUserCursor = annotation_app.config['INSTAGRAM_ALL_USER_ID_COLLECTION'].find()
        # get each users total image and calculate annotaotor assigned image

        print 'FASHIONISTA::{}   --- TOTAL POST::{} ----- TOTAL COMMENTS::{}'
        c=0
        for instaUser in allInstagramUserCursor:
            instaUserName = instaUser['username']
            liketkit = annotation_app.config['INSTAGRAM_LIKETKIT_USER_COLLECTION'].find({'username': instaUserName})
            if (liketkit.count() > 0):
                totalImageUser = liketkit.count()
                #print 'TOTAL LTKIT ----- {} {} '.format(instaUserName, totalImageUser)
                comment_count = 0
                for csr_usr in liketkit:
                    db_comment = len(csr_usr['comments']['data'])
                    comment_count = comment_count + db_comment
                c = c + 1
                print '[{}]{}   ----- {} ----- {}'.format(c,instaUserName,totalImageUser,comment_count)
            else:
                swedish = annotation_app.config['INSTAGRAM_SWEDISH_USER_COLLECTION'].find({'username':instaUserName})
                totalImageUser = swedish.count()
                #print 'TOTAL SWEDISH -----  {}   {} '.format(instaUserName,totalImageUser)
                comment_count = 0
                for csr_usr in swedish:
                    db_comment = len(csr_usr['comments']['data'])
                    comment_count = comment_count + db_comment
                #print '{}   ----- {} ----- {}'.format(instaUserName, totalImageUser, comment_count)




def store_liketokit_linkin_json_file(userdata_as_cursor):

    cwd = os.getcwd()
    filename = os.path.join(str(cwd)+"/annotation_webapp/static/appdata","all_image_liketkiturls_data.json")
    json_imageid_list = []
    json_imageid_set = set()
    json_data = return_json_data(filename)

    if(json_data):
        for item in json_data:
            imageid = item.get("imageid")
            json_imageid_list.append(imageid)
        print len(json_imageid_list)
        json_imageid_set = set(json_imageid_list)
        print "SET" + str(len(json_imageid_set))

    url_data  = []
    for each_data in userdata_as_cursor:
        imageid = each_data.get("id")
        edge_media_to_caption = each_data.get("edge_media_to_caption")
        edges = edge_media_to_caption.get("edges")

        if imageid not in json_imageid_set:

            for each_node in edges:
                node = each_node.get("node")
                text= node.get("text")
                urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)

            imageid_liiketkit_url_dict = {}
            imageid_liiketkit_url_dict["imageid"] = imageid
            imageid_liiketkit_url_dict["liketkiturl"] = urls
            url_data.append(imageid_liiketkit_url_dict)

        #print '{}----{}'.format(imageid,urls)
    save_json(url_data,filename)
    print url_data

def get_imageid_list_from_cursor(instaUserCursor):
    imageid_list =[]
    for id in instaUserCursor:
        imageid_list.append(id['id'])
    return imageid_list

def save_imageid_list_in_json(fashionistaName,userDataCursor):
    a_list = []

    cwd = os.getcwd()
    filename = os.path.join(str(cwd)+"/annotation_webapp/static/appdata","all_fashionistauser_imageidlist_data.json")
    json_fashionistauser_list = []
    json_fashionistauser_set = set()
    json_data = return_json_data(filename)

    if(json_data):
        for item in json_data:
            username = item.get("fashionistaUsername")
            json_fashionistauser_list.append(username)
        #print len(json_fashionistauser_list)
        json_fashionistauser_set = set(json_fashionistauser_list)
        #print "SET" + str(len(json_fashionistauser_set))

    if(fashionistaName not in json_fashionistauser_set):
        print " ADD "
        imageid_list = get_imageid_list_from_cursor(userDataCursor)
        usernaem_imageid_list_dict = {}
        usernaem_imageid_list_dict["fashionistaUsername"] = fashionistaName
        usernaem_imageid_list_dict["imageidlist"] = imageid_list
        usernaem_imageid_list_dict["totalimagecount"] = len(imageid_list)

        a_list.append(usernaem_imageid_list_dict)

        #print usernaem_imageid_list_dict

    else:
        print "Already ADDED"
        pass

    save_json(a_list,filename)

def process_text_analysis_data():

    print 'processing test _analysis json'
    cwd = os.getcwd()
    #filename = os.path.join(str(cwd) + "/annotation_webapp/static/appdata", "text_analysis.json")

    #filename = os.path.join(str(cwd) + "/annotation_webapp/static/appdata", "text_analysis_65k.json")
    filename = os.path.join(str(cwd) + "/annotation_webapp/static/appdata", "text_analysis_v2_70k.json")

    json_data = return_json_data(filename)
    '''Current json length > 26149 len(json_data)'''

    for item in json_data:
        imageid = item["id"]
        testanalysis_data_csr = textAnalysisDataCollection.find({"_id":imageid})
        if(testanalysis_data_csr.count() == 1):
            print  'Image id Already inserted {} '.format(imageid)
        else:
            try:
                insert_item_in_database(item)
            except DuplicateKeyError:
                print 'Image id already inserted {}'.format(imageid)



# def insert_item_in_database(item):
#     each_image_text_analysis_dict = {}
#     hashtags = None
#     links = None
#     for data_k, data_v in item.items():
#         print data_k
#         print data_v
#         all_category = []
#         category_related_word = []
#         frequency_count = 0
#         if (data_k == 'id'):
#             imageid = data_v
#             each_image_text_analysis_dict["_id"] = imageid
#         elif (data_k == 'hashtags'):
#             hashtags = data_v
#             each_image_text_analysis_dict["hashtags"] = hashtags
#         elif (data_k == 'links'):
#             links = data_v
#             each_image_text_analysis_dict["links"] = links
#         elif (type(data_v) == dict):
#             data_count_dict = {}
#             for k, v in data_v.items():
#                 all_category.append(k)
#                 frequency_count = frequency_count + v
#                 frequency_count = frequency_count / 10
#                 data_count_dict["data"] = all_category
#                 data_count_dict["count"] = frequency_count
#                 each_image_text_analysis_dict[data_k] = data_count_dict
#         else:
#             print ' Didnt find "id", "hashtags" and "dictionary" '
#
#     print each_image_text_analysis_dict
#     textAnalysisDataCollection.insert(each_image_text_analysis_dict)
#     print  'Image idinserted {} '.format(imageid)

def insert_item_in_database(item):
    print 'inserting item'
    #retrieve data and create dict to store in database
    each_image_text_analysis_dict = {}
    hashtags = None
    links = None
    for data_k, data_v in item.items():
        all_category = []
        category_related_word = []
        frequency_count = 0
        if (data_k == 'id'):
            imageid = data_v
            each_image_text_analysis_dict["_id"] = imageid
        elif (data_k == 'hashtags'):
            hashtags = data_v
            each_image_text_analysis_dict["hashtags"] = hashtags
        elif (data_k == 'links'):
            links = data_v
            each_image_text_analysis_dict["links"] = links
        elif (type(data_v) == dict):
            data_count_dict = {}
            #print '>>>>>>>> {}'.format(data_v)
            ##########################################################
            # sorted according to value.output small to large
            kk = sorted(data_v.items(), key=itemgetter(1))
            #print '----------- {} len: {}'.format(kk ,len(kk))

            #take last three data so that highest count get first position
            last_three_data= []
            last_three_data.append(kk[-1])
            last_three_data.append(kk[-2])
            last_three_data.append(kk[-3])
            last_three_data.append(kk[-4])
            print ':::::::::::::::: {} len: {}'.format(last_three_data ,len(last_three_data))
            totalCount = 0
            for k,v in last_three_data:
                totalCount = totalCount + v
            for k, v in last_three_data:
                if totalCount > 0:
                    all_category.append(k+':%.2f' % ((v/totalCount)*100) + "%")
                else:
                    all_category.append(k + ':%.2f' % (v) + "%")
                frequency_count = frequency_count + v
                frequency_count = frequency_count
                data_count_dict["data"] = all_category
                data_count_dict["count"] = frequency_count
                each_image_text_analysis_dict[data_k] = data_count_dict


            #print data_count_dict["data"]
            ########################################################
            #this loop does not sort the data
            #for k, v in data_v.items():

                #kk = sorted(k.items(), key=itemgetter(1))
                #print '----------- {}'.format()
                #all_category.append(k)
                #frequency_count = frequency_count + v
                #frequency_count = frequency_count / 10
                #data_count_dict["data"] = all_category
                #data_count_dict["count"] = frequency_count
                #each_image_text_analysis_dict[data_k] = data_count_dict

        #else:
            #print ' Didnt find "id", "hashtags" and "dictionary" '

    #print each_image_text_analysis_dict
    textAnalysisDataCollection.insert(each_image_text_analysis_dict)
    #print  'Image idinserted {} '.format(imageid)



def create_assignment_images(instaUserName,instaUserCursor,totalImageUser,totalAnnotator,annotatorCursor):
    """ For each instagramuser  assign their images to each annotator such that each image is assigned to atleast five annotators
    parameter: instagram user and cursor that contains all the images of this user
    function: insert data in 'annotatorwebapp.annotateddatadetailwithuser'
    as { "_id" : ObjectId("5a6140df25664e236eb8c5a5"), "annotatorusername" : "umu", "imageinfo" : { "fashionistausername" : "jessi_afshin", "annotateddatajson" : null, "annotated" : false }, "imageid" : "1679351995365180747" }

    """
    commonCount = annotation_app.config['COMMON_COUNT']
    print instaUserName

    ## 1. get all the images for the instagram user instaUserName
    id_list =[]
    for id in instaUserCursor:
        id_list.append(id['id'])
    print id_list

    annotatorCollection = annotation_app.config['ANNOTATION_USERS_COLLECTION']
    annotator_cursor = annotatorCollection.find()

    #2. get all annotator list from annotator collection
    annotator_list =[]
    for ann in annotator_cursor:
        annotator_list.append(ann['_id'])
    print annotator_list

    ##3. getthe collection to save assigned image id for each of the annotator
    annotationIdCollection = annotation_app.config['ANNOTATE_DETAIL_IAMGEID_USER_COLLECTION']
    if len(id_list) > 5 and len(annotator_list)> 5:
    #this loop should be in range of len(id_list)
        for id in range(0,len(id_list)):
            #4. read random 5 annotators from the list of all annotators
            rand_items = random.sample(annotator_list, commonCount)
            #5. for each of the annotator in the random annotator selector list assing the same imageid in 'imageID' variable
            for ann_index in range(0,len(rand_items)):
                #print 'ID: {} ---- ANN: {}'.format(id_list[id], rand_items[ann_index])
                annotator_name =  rand_items[ann_index]
                imageID = id_list[id]

                db_data_image_id_list_for_annotator =[]
                db_data_cursor = annotationIdCollection.find({"annotatorusername": annotator_name})
                if db_data_cursor.count() > 0:
                    for each_id in db_data_cursor:
                        db_image_id = each_id["imageid"]
                        db_data_image_id_list_for_annotator.append(db_image_id)
                if (imageID == db_data_image_id_list_for_annotator):
                    print 'Exists {}'.format(imageID)
                    pass
                else:
                    image_metadata_dict = {"fashionistausername": instaUserName,"annotated":False,"annotateddatajson":None}
                    data_dict = {}
                    data_dict["annotatorusername"] = annotator_name
                    data_dict["imageid"] = imageID
                    data_dict["imageinfo"] = image_metadata_dict
                    data_dict["fashionistausername"] = instaUserName
                    annotationIdCollection.insert(data_dict)

    for a in annotator_list:
        c = annotationIdCollection.find({"annotatorusername": a})
        print 'a :{}  len:{}'.format(a,c.count())




if __name__ == '__main__':

    main()

