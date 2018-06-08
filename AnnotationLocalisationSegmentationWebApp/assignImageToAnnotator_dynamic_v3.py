
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError,CursorNotFound
from flask import request
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
from pymongo import ASCENDING


annotation_app = Flask(__name__)
annotation_app.config.from_object(config)

annotationIdCollection = annotation_app.config['ANNOTATE_DETAIL_IAMGEID_USER_COLLECTION']
annotatorCollection = annotation_app.config['ANNOTATION_USERS_COLLECTION']
annotator_image_assign_collection = annotation_app.config['ANNOTATOR_IMAGEID_ASSIGNED_COLLECTION']
liketkitCollection = annotation_app.config['INSTAGRAM_LIKETKIT_USER_COLLECTION']
swedishCollection = annotation_app.config['INSTAGRAM_SWEDISH_USER_COLLECTION']
allinstagramuserCollection = annotation_app.config['INSTAGRAM_ALL_USER_ID_COLLECTION']
commonCount = annotation_app.config['COMMON_COUNT']
ALL_fashionistalist = annotation_app.config['ALL_FASHIONISTA_LIST']



def return_json_data(filename):
    '''get a filename and return the file data as json '''
    json_data = []
    if os.path.isfile(filename) :
        json_file = open(filename)
        json_data = json.load(json_file)
    return json_data


def save_json(data, dst='./'):
    ''' This function save data in the dst filename -if the file exists then append the data
    else create new file and add json data
    '''
    # if the file exists then append data
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

    # else create new file and add json data
    else:
        with open(dst, 'wb') as f:
            json.dump(data, codecs.getwriter('utf-8')(f), indent=4, sort_keys=True, ensure_ascii=False)


def get_imageid_list_from_cursor(instaUserCursor):
    ''' get sll the image id from cursor'''
    imageid_list =[]
    for id in instaUserCursor:
        imageid_list.append(id['id'])
    return imageid_list

def save_imageid_list_in_json(fashionistaName, userDataCursor):
    ''' get a fashionistaname and the database cursor for this fashionista data in database
        and add those data in the json file '''

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
        json_fashionistauser_set = set(json_fashionistauser_list)

    if(fashionistaName not in json_fashionistauser_set):
        print " ADD "
        imageid_list = get_imageid_list_from_cursor(userDataCursor)
        usernaem_imageid_list_dict = {}
        usernaem_imageid_list_dict["fashionistaUsername"] = fashionistaName
        usernaem_imageid_list_dict["imageidlist"] = imageid_list
        usernaem_imageid_list_dict["totalimagecount"] = len(imageid_list)
        a_list.append(usernaem_imageid_list_dict)

    else:
        pass

    save_json(a_list,filename)


def get_five_annottaor_list(annotator_list,commonCount):
    '''return random  annotator of size commonCount from total annotator list'''

    random.shuffle(annotator_list)
    five_random_annotator = random.sample(annotator_list, commonCount)
    return five_random_annotator

def get_five_annottaor_list_one_annotator_fixed(annotator_list,commonCount,annotator):
    '''return random  annotator of size commonCount from total annotator list'''
    while True:
        random.shuffle(annotator_list)
        five_random_annotator = annotator_list[:commonCount]
        #five_random_annotator = random.sample(annotator_list, commonCount)
        if(annotator in five_random_annotator):
            break
    return five_random_annotator

def get_annotator_list_from_database():
    '''return annotator list from database'''

    annotatorCursor = annotatorCollection.find()
    annotator_list =[]
    for ann in annotatorCursor:
        annotator_list.append(ann['_id'])
    return annotator_list



def insert_imageid_in_database(annotator_name,imageID,instaUserName):
    ''' insert a template for data annottaion in database 'annotatorwebapp.annotateddatadetailwithuser'
    as { "_id" : ObjectId("5a6140df25664e236eb8c5a5"), "annotatorusername" : "umu", "imageinfo" : { "fashionistausername" : "jessi_afshin", "annotateddatajson" : null, "annotated" : false }, "imageid" : "1679351995365180747" }
    '''
    db_data_image_id_list_for_annotator =[]
    db_data_cursor = annotationIdCollection.find({"annotatorusername": annotator_name})
    if db_data_cursor.count() > 0:
        for each_id in db_data_cursor:
            db_image_id = each_id["imageid"]
            db_data_image_id_list_for_annotator.append(db_image_id)
    if (imageID in db_data_image_id_list_for_annotator):
        print 'Exists {}'.format(imageID)
        pass
    else:
        image_metadata_dict = {"fashionistausername": instaUserName,"annotated":False,"annotateddatajson":None,"styles":None}
        data_dict = {}
        data_dict["annotatorusername"] = annotator_name
        data_dict["imageid"] = imageID
        data_dict["imageinfo"] = image_metadata_dict
        data_dict["fashionistausername"] = instaUserName
        annotationIdCollection.insert(data_dict)

def find_annotator(annottaor_name):
    '''get a annottaor name and return true or false according to the existance of the annottaorusername in database'''
    exist = False
    if(annotatorCollection.find({"_id":annottaor_name})):
        exist = True
    return exist

def get_unique_imageidlist(imageList_in_DB):
    '''  [ { "fashionistausername" : "lolariostyle", "annotated" : false, "imageid" : "1662569323480290687" }, { "fashionistausername" : "lolariostyle", "annotated" : false, "imageid" : "1662095687640400122" }]'''
    #id_set = set()
    id_list = []

    #for item in imageList_in_DB:
    for k,data in enumerate(imageList_in_DB):
        id_list.append(data["imageid"])

    id_set = set(id_list)
    print id_set
    return id_set
def create_assignment_images_3(id_list,annotator_list,commonCount,instaUserName,annotator_image_assign_collection,annotator,assign_count):
    """ Version test For each instagramuser  assign first 100 images to each annotator such that each image is assigned to atleast five annotators.
    After all the images annotated then add another 50 images and continue until all annotated
    parameter: instagram user and cursor that contains all the images of this user
    function: insert data in if all the previou'annotatorwebapp.annotateddatadetailwithuser'
    as { "_id" : ObjectId("5a6140df25664e236eb8c5a5"), "annotatorusername" : "umu", "imageinfo" : { "fashionistausername" : "jessi_afshin", "annotateddatajson" : null, "annotated" : false }, "imageid" : "1679351995365180747" }
    """

    assign_count = int(assign_count)
    assign_list = itertools.islice(id_list, assign_count +1)
    ##3. getthe collection to save assigned image id for each of the annotator
    if len(id_list)>= assign_count:
    #this loop should be in range of len(id_list)
        #for id in id_list:
        for i,id in enumerate(assign_list):
            user_id_dict = {}
            id_set = set()

            #4. read random 5 annotators from the list of all annotators
            #rand_items = random.sample(annotator_list, commonCount)
            rand_items = get_five_annottaor_list_one_annotator_fixed(annotator_list,commonCount,annotator)
            print rand_items
            #5. for each of the annotator in the random annotator selector list assing the same imageid in 'imageID' variable
            for ann_index in range(0,len(rand_items)):
                imageList = []

                #print 'ID: {} ---- ANN: {}'.format(id_list[id], rand_items[ann_index])
                annotator_name =  rand_items[ann_index]
                imageID = id

                ''' ------------------------------'''
                get_annotator_assign_imageidlist_cursor = annotator_image_assign_collection.find({"_id":annotator_name})
                cursor_count = get_annotator_assign_imageidlist_cursor.count()

                if(cursor_count == 1):
                    user_id_dict['fashionistausername'] = instaUserName
                    user_id_dict['annotated'] = False
                    user_id_dict['imageid'] = id

                    for each_item in get_annotator_assign_imageidlist_cursor:
                        imageList_in_DB = each_item.get("imageList")

                        print 'IIIIIIIiiiiii{}'.format(imageList_in_DB)
                        id_set = get_unique_imageidlist(imageList_in_DB)
                        if(id not in id_set):
                            imageList_in_DB.append(user_id_dict)
                            annotator_image_assign_collection.update({"_id":annotator_name},{"$set":{"imageList":imageList_in_DB}})
                            print 'update id: {} For annotator: {} to :{}'.format(imageID,annotator_name,len(imageList_in_DB))
                        else:
                            pass
                elif(cursor_count == 0):
                    user_id_dict['fashionistausername'] = instaUserName
                    user_id_dict['annotated'] = False
                    user_id_dict['imageid'] = id

                    #imageList.append(imageID)
                    imageList.append(user_id_dict)
                    annotator_image_assign_collection.insert({"_id":annotator_name, "imageList":imageList})

                    ''' ------------------------------'''
                    print 'Insert image id: {} For annotator: {} '.format(imageID,annotator_name)


def main():
    # Ask for data to store, delete and assign data
    option = raw_input(" Enter '1'  for assign annotator a number of images( annotator, fashionista,count)imagelist with FSHIONISTA-USER ")


    if(option == '1'):
        # Assign the annotator the instagram user image
        # Add imageid info in ANNOTATOR_IMAGEID_ASSIGNED_COLLECTION
        # Add annotation template and detail in ANNOTATE_DETAIL_IAMGEID_USER_COLLECTION
        assign_count = None
        fashionista_name=None

        annotator_to_assign = raw_input("Enter the correct annotator name you want to assign image?")
        if(find_annotator(annotator_to_assign)):
            fashionista_name = raw_input("Enter fashionista name to assign image to -  "+ annotator_to_assign)
            if (fashionista_name in ALL_fashionistalist):
                pass
            else:
                fashionista_name = raw_input("Enter correct fashionista name to assign image to  -  "+ annotator_to_assign)


        else:
            annotator_to_assign = raw_input("Enter correct annotator user name ?")
            if(find_annotator(annotator_to_assign)):
                fashionista_name = raw_input("Enter fashionista name to assign image  to - "+ annotator_to_assign)

        #fashionista_name = raw_input("Enter fashionista name to assign image   "+ annotator_to_assign)

        assign_count = raw_input("Enter how many data do you want to assign the annotator - "+ annotator_to_assign)
        #read the created json file and assign image to annottaor
        cwd = os.getcwd()
        filename = os.path.join(str(cwd)+"/annotation_webapp/static/appdata","all_fashionistauser_imageidlist_data.json")
        json_data = return_json_data(filename)

        username_imageset_dict={}
        imageset = set([])

        for each_user in json_data:
            total_image_of_fashionista = each_user.get("totalimagecount")
            username = each_user.get("fashionistaUsername")
            imageidset = each_user.get("imageidlist")
            if(username == fashionista_name):
                #only get the requested users data
                username_imageset_dict[username]= imageidset
                break
        annotator_list = get_annotator_list_from_database()

        if(username_imageset_dict):
            create_assignment_images_3(username_imageset_dict[fashionista_name],annotator_list,commonCount,fashionista_name,annotator_image_assign_collection,annotator_to_assign,assign_count)

        annotator_image_assign_collection_cursor = annotator_image_assign_collection.find({"_id":annotator_to_assign})
        assigned_data = annotator_image_assign_collection_cursor.count()


        if assigned_data > 0:
            print 'Already assigned image list now add data in the imageannottaedDetail collection'.format(assigned_data)
            imageList = set([])
            current_fashionista_list = []

            for item in annotator_image_assign_collection_cursor:
                imageList =  item.get('imageList')
                print imageList
                for data in imageList:
                    if(fashionista_name in data.values()):
                        print data
                        current_fashionista_list.append(data)
            print len(current_fashionista_list)
            annotated_list=[]
            non_annotated_list=[]
            for each_data in current_fashionista_list:
                if(each_data.get("annotated")):
                    annotated_list.append(each_data)
                else:
                    non_annotated_list.append(each_data)

            # if there is data in the non_annotated_list then assign to annottaor
            if(non_annotated_list):
                length_imageList = len(non_annotated_list)
                int_assign_count = int(assign_count)

                #slice imageidlist and then insert in database
                for i,imagedata in enumerate(non_annotated_list):
                    fashionista = imagedata.get("fashionistausername")
                    imageid = imagedata.get("imageid")
                    insert_imageid_in_database(annotator_to_assign,imageid,fashionista)
            # if there is no data in the non_annotated_list for the annottaor
            else:
                print 'All the data is annotated by the annottaor and there is no unannotated data for this fashionista'

        else:
            print "THERE IS NO DATA IN COLLECTION" + str(annotator_image_assign_collection)

def get_fashionistaname_for_imageid(imageID):
    '''get a imageid return the fashinistausername to whom the id belongs to'''
    username = None
    search_id = liketkitCollection.find({"id":imageID})
    if(search_id.count()>0):
        for item in search_id:
            username = item.get("username")
    else:
        search_id = swedishCollection.find({"id":imageID})
        if(search_id.count()>0):
            for item in search_id:
                username = item.get("username")
    #print username
    return username


if __name__ == '__main__':
    main()
