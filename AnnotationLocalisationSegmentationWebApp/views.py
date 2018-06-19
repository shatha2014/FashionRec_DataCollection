#!/usr/bin/python
# -*- coding: utf-8 -*-

#from annotation_webapp import annotation_app,lm

from flask import request,Response, redirect, render_template, url_for, flash,session,jsonify
from flask_login import login_user, logout_user, login_required
from user import User,LoginForm
from werkzeug.exceptions import BadRequest
import random
import ast
import json,os
import requests
import config
import PIL
from PIL import Image
import StringIO
import base64, io
import jinja2
import boto3
import xmltodict
import ast
import cv2
import numpy as np
from werkzeug.serving import make_ssl_devcert
from werkzeug.serving import run_simple

from flask import Flask
from flask_login import LoginManager

annotation_app = Flask(__name__)
annotation_app.config.from_object('config')
#images = Images(annotation_app)

#login manager instance which provides session management for for Flask.
lm = LoginManager()
lm.init_app(annotation_app)
lm.login_view = 'login'


#temporary added by ShathaJ
region_name = 'us-east-1'
aws_access_key_id = 'AKIAIN65GSZTO2UVW57Q'
aws_secret_access_key = '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'
#end temporary by ShathaJ


#### BEGIN database info for annotation-webapp
liketkitCollection = annotation_app.config['INSTAGRAM_LIKETKIT_USER_COLLECTION']
swedishCollection = annotation_app.config['INSTAGRAM_SWEDISH_USER_COLLECTION']
annotatorAssignedIdCollection = annotation_app.config['ANNOTATE_DETAIL_IAMGEID_USER_COLLECTION']
imagebase64binarycollection = annotation_app.config['IMAGEID_AND_BASE64_BINARY_DATA_COLLECTION']
textAnalysisDataCollection = annotation_app.config['IMAGEID_TEXT_ANALYSIS_DATA_COLLECTION']
annotatorassignedimagelist = annotation_app.config['ANNOTATOR_IMAGEID_ASSIGNED_COLLECTION']
#### END database info for annotation-webapp

#### BEGIN database info for localisation-segmentation
localiseddata = annotation_app.config['LOCALISATION_DATA']
segmenteddata = annotation_app.config['SEGMENTATION_DATA']
imagesegdata = annotation_app.config['IMG_BIN_SEG']
imagelocdata = annotation_app.config['IMG_BIN_LOC']
#### END database info for localisation-segmentation

@annotation_app.template_filter()
def str_to_dict_object(value):
    return ast.literal_eval(value)

#### BEGIN[appRoute] application home page
#@annotation_app.route('/')
@annotation_app.route('/', methods=['GET','POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        print 'POST in [login] '.format()
        user = annotation_app.config['ANNOTATION_USERS_COLLECTION'].find({"_id": form.username.data})
        if(user.count()==1):
            for item in user:
                userid_db = item["_id"]
                password_db = item["password"]
                if User.validate_login(password_db, form.password.data):
                    user_obj = User(userid_db)
                    #print(user_obj.get_id())

                    login_user(user_obj)
                    # temporary by ShathaJ
                    #flash("Logged in successfully!", category='success')

                    #testing by ShathaJ
                    endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
                    client = boto3.client(
                        'mturk',
                        endpoint_url=endpoint_url,
                        region_name=region_name,
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                    )

                    # This will return $10,000.00 in the MTurk Developer Sandbox
                    #flash(client.get_account_balance()['AvailableBalance'] , category='success')
                    # external_content = """
                    #  <ExternalQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd">
                    #    <ExternalURL>https://shatha2.it.kth.se</ExternalURL>
                    #    <FrameHeight>400</FrameHeight>
                    #  </ExternalQuestion>
                    # """
                    # #
                    # response = client.create_hit(
                    #      Question=external_content,
                    #      LifetimeInSeconds=60 * 60 * 24,
                    #      Title="Answer a simple question",
                    #      Description="Help research a topic",
                    #      Keywords="question, answer, research",
                    #      AssignmentDurationInSeconds=120,
                    #      Reward='0.05'
                    # )
                    #
                    # # The response included several helpful fields
                    # hit_group_id = response['HIT']['HITGroupId']
                    # hit_id = response['HIT']['HITId']

                    # Let's construct a URL to access the HIT
                    #sb_path = "https://workersandbox.mturk.com/mturk/preview?groupId={}"
                    #hit_url = sb_path.format(hit_group_id)

                    #flash(hit_url, category='success')


                    #end testing by ShathaJ



                    return redirect(url_for("mainpage",annotator_username = userid_db ))
    if request.method == 'GET':
        print 'GET in [login] '.format()
        return render_template('login.html', title='Webapp login', form=form)
#### END[appRoute] application home page


#### BEGIN[appRoute] applications all User profile page
@annotation_app.route('/allUserFolder/<annotator_username>', methods=['GET', 'POST'])
@login_required
def allUserFolder(annotator_username):
    ''' This function use the static/appdata/username_profilepicurl_annotationcomplete.json
      file to create the gallery of all fashionista users
      '''
    if request.method =='GET':
        print 'GET in [allUserFolder] '.format()
	option = request.args.get('option')
	print option
        redirect(request.path)

    if request.method=='POST':
        print 'POST in [allUserFolder]'

    #annotation_app.root_path =/var/www/annotation_webapp/
    #1. Read the json file from app root satic folder to get the base64 data and fashinista name
    app_root_path = annotation_app.root_path
    # 2. open json file in read mode
    json_url = os.path.join(app_root_path, "static/appdata", "username_profilepicurl_annotationcomplete.json")

    #open json file in read mode
    with open(json_url, "r") as jsonFile:
        name_propic_json = json.load(jsonFile)
    # 3. update json file according to different annotator image annotated data	95
    annottaion_complete_boolean = check_annotation_completion_for_each_fashionista(name_propic_json,annotator_username,option)

    return render_template('allUserFolder.html', annotator_username = annotator_username,name_propic_json = annottaion_complete_boolean, option = option)
#### END[appRoute] applications all User profile page


#### BEGIN[appRoute] applications Single Users Gallery page
@annotation_app.route('/singleUserFolder/<insta_username>', methods=['GET', 'POST'])
@login_required
def singleUserFolder(insta_username):
    if request.method == "POST":
        print "POST in [singleUserFolder]"

    if request.method == "GET":
        annotator_username = request.args.get('annotator_username')
	option = request.args.get('option')

        #check the value annotator_usename is provided by the requester
        if (annotator_username):
            print 'GET in [singleUserFolder] with args param: annotator_username'
            imageid = request.args.get('id')

            if imageid:
                print 'GET in [singleUserFolder] with args param: annotator_username annotator_username,imageid'

            ''' Generating  a dictionary({'id':'12734734','base64AnnotatedInfo':{'base64binary':'http:/.....','annotated':Ture/false}}) for the current instagram user in(insta_username)
                        The purpose of this dictionary is to display all the instagram users picture
                        Everytime its loads the data from MOngodb
                        so it will get tha latest updated annotated information.
                        '''

            # id_annotated_info_dict_list = annotatorAssignedIdCollectionProcessFunction(annotator_username,insta_username)
            id_annotated_info_dict_list = annotatorAssignedIdCollectionProcessFunctionForBaseBinarydataAndAnnotatedInfo(
                annotator_username, insta_username)

            return render_template('singleUserFolder.html', insta_username=insta_username,
                                   annotator_username=annotator_username,
                                   id_annotated_info_dict_list=id_annotated_info_dict_list, option = option)
#### END[appRoute] applications Single Users Gallery page

#### BEGIN[appRoute] applications Image Annotation page
@annotation_app.route('/fashionistasImageAnnotation', methods=['GET', 'POST'])
@login_required
def fashionistasImageAnnotation():

    # POST -handling annotated json data from the  annotator #
    if request.method == "POST":
        print "POST in [fashionistasImageAnnotation]"
        annotation_json = request.json
        annotated_image_id = annotation_json.get("imageid")
        annotated_insta_username = annotation_json.get("instagramuser")
        annotator_username = annotation_json.get("annotator")
        annotated_data = annotation_json.get("annotated_data")
        save_item_check = annotation_json.get("save_item")
        finalize_annotation_check = annotation_json.get("finalizeannotation")
        styles = annotation_json.get("styles")
        non_fashion_item = annotation_json.get("nonfashionitem")
        annotated_image_url = annotation_json.get("image_url")
        all_id_annotated_info_dict_list = annotation_json.get("all_id_annotated_info_dict_list")
        deleteitem = annotation_json.get("deleteitem")
	option = '1'

        all_id_annotated_info_dict_list = annotatorAssignedIdCollectionProcessFunctionForBaseBinarydataAndAnnotatedInfo(annotator_username, annotated_insta_username)
        print len(all_id_annotated_info_dict_list)

        for i in all_id_annotated_info_dict_list:
            all_id_annotated_info_dict_list = i

	##COND1: if the POST request is 'delete annotated Item' from database
        if (deleteitem):
            itemCategorytToDelete = annotation_json.get("itemcategorytodelete")
            delete_status = deleteAnSavedItemCategoryFromannotatorAssignedIdCollection(annotator_username,annotated_insta_username,annotated_image_id,itemCategorytToDelete)

            return Response(json.dumps({"redirect":False,"success": delete_status}),status=200, mimetype= 'application/json')




        ####COND2:if the POST request is  Finalize Annotation
        elif(finalize_annotation_check):
            '''
             this if condition check whether the request is finalize or not.
             The frontend only sending the finalize command.
             Back end will only update the 'annotated' field of the image to True.
             SAMPLE DATA IN DATABASE
             { "_id" : ObjectId("5a62121b25664e0924cc338d"),
             "fashionistausername" : "cellajaneblog",
             "annotatorusername" : "ann7",
             "imageinfo" : { "fashionistausername" : "cellajaneblog",
             "annotateddatajson" : null,
              "annotated" : false ,
              "styles":"chich style" },
             "imageid" : "1682056482685700593" }

             '''
            annotatorAssignedIdCollectionFinalizeFunction(annotator_username,annotated_insta_username,annotated_image_id,styles)
            #print 'FINALIZE {}'.format("https://shatha2.it.kth.se/singleUserFolder/" + annotated_insta_username + "?annotator_username=" + annotator_username)

            return Response(json.dumps({"redirect": True,
                                        "redirect_url": "https://shatha2.it.kth.se/singleUserFolder/" + annotated_insta_username + "?annotator_username=" + annotator_username+"&option="+option,
                                        "success": True}), mimetype='application/json')
	##COND3:if the POST request is  'NonFashion item'
        elif(non_fashion_item):

            non_fashion_image_db =  annotatorAssignedIdCollection.find({"$and":[{"annotatorusername":annotator_username},{"fashionistausername":annotated_insta_username},{"imageid":annotated_image_id}]})
            annotatorAssignedIdCollection.update({"$and":[{"annotatorusername":annotator_username},{"fashionistausername":annotated_insta_username},{"imageid":annotated_image_id}]},{"$set":{"imageinfo.annotated":True,"imageinfo.imageid":annotated_image_id,"imageinfo.fashionistausername":annotated_insta_username,"imageinfo.annotateddatajson":[{"ItemCategory":"Non Fashion  item"}]}})

            for i in non_fashion_image_db:
                print 'NOT FAHSION RELATED IMAGE {} {} '.format(i,"https://shatha2.it.kth.se/singleUserFolder/" + annotated_insta_username + "?annotator_username=" + annotator_username)
            return Response(json.dumps({"redirect": True,"redirect_url": "https://shatha2.it.kth.se/singleUserFolder/" + annotated_insta_username + "?annotator_username=" + annotator_username+"&option="+option,"success": True}), mimetype= 'application/json')

        ## ##COND4:if the POST request is  'Save Item'
        elif(save_item_check):
            #print "--------------Only save item in database do not set annotated field to true"
            saved_data, item_exist_boolean = saveItemDataToannotatorAssignedIdCollection(annotator_username,annotated_insta_username,annotated_image_id,annotated_data)

            #print saved_data
            #print 'Boolean for item existance {} '.format(item_exist_boolean)
            #annotated_data
            #sannotatorAssignedIdCollectionUpdateFunction()

            #print json.dumps({"redirect":False,"success": True, "saveditemindb":saved_data})

            sorted_annotated_json_data = []

            for item in saved_data:
                    print type(item)
                    sorted_annotated_dict ={}
                    annotated_data_dict = item
                    for key,value in item.items():
                        if(key == "ItemCategory"):
                            sorted_annotated_dict["aItemCategory"] = value
                        if(key == "ItemSubCategory"):
                            sorted_annotated_dict["bItemSubCategory"] = value
                        if (key == "FinalizeAnnotatedAttributes"):
                            sorted_annotated_dict["cFinalizeAnnotatedAttributes"] = value
                            print '****** item: {} ****value {}'.format(key ,value )
                    #print sorted(sorted_annotated_dict)
                    sorted_annotated_json_data.append(sorted_annotated_dict)
            #sorted_annotated_json_data = ast.literal_eval(json.dumps(sorted_annotated_json_data))
            sorted_annotated_json_data = json.dumps(sorted_annotated_json_data)
            #final_data = json.dumps(sorted_annotated_json_data)

            redirect_url = url_for('fashionistasImageAnnotation',
                                   annotator_username = annotator_username,
                                   insta_username=annotated_insta_username,
                                   image_url= annotated_image_url,
                                   id = annotated_image_id,
                                   annotated_json_data = sorted_annotated_json_data)
            #print redirect_url
            #print sorted_annotated_json_data
            return Response(json.dumps({"redirect":True,
                                        "redirect_url":redirect_url,
                                        "success": True,
                                        "saveditemindb":saved_data}),
                            status=200, mimetype= 'application/json')
            ##return render_template('fashionistasImageAnnotation.html',annotator_username = annotator_username,insta_username=annotated_insta_username, image_url= annotated_image_url,id = annotated_image_id,all_id_annotated_info_dict_list = all_id_annotated_info_dict_list,annotated_json_data = sorted_annotated_json_data)
    #### GET Request
    if request.method == "GET":
        print 'GET in [fashionistasImageAnnotation]'
        annotator_username= request.args.get('annotator_username')
        insta_username = request.args.get('insta_username')
        image_url = request.args.get('image_url')
        image_id = request.args.get('img_id')
	option = request.args.get('option')
        all_id_annotated_info_dict_list = request.args.get('all_id_annotated_info_dict_list')

        ## request parameter for next image
        next = request.args.get('next')
        ## request parameter for prev image
        prev = request.args.get('prev')

        ## request parameter for saved item
        annotated_json_data  = request.args.get('annotated_json_data')
        #annotated_json_data = ast.literal_eval(annotated_json_data)
        if(annotated_json_data):
            image_id = request.args.get('id')
        all_id_annotated_info_dict_list = annotatorAssignedIdCollectionProcessFunctionForBaseBinarydataAndAnnotatedInfo(
            annotator_username, insta_username)
        #print len(all_id_annotated_info_dict_list)

        for i in all_id_annotated_info_dict_list:
            all_id_annotated_info_dict_list = i

        # check the list is empty or not. this list is required to get the prev and next image if and
        # also provide the annotated information of each image
        if (all_id_annotated_info_dict_list):
            #convert it to remove unicode
            #all_id_annotated_info_dict_list = ast.literal_eval(all_id_annotated_info_dict_list)
            #print annotator_username
            #print insta_username
            #print image_id
            #print image_url
            #print annotated_json_data
            all_assignedimage_ids_for_current_annotator = all_id_annotated_info_dict_list.keys()
            #print (all_assignedimage_ids_for_current_annotator)
            ''' INFO 3 :Get the current image id and url from
             database and display the image in html page'''

            '''BEGIN: required code for INFO:2'''
            # looking for the prev next image id
            current_image_index = all_assignedimage_ids_for_current_annotator.index(image_id)
            length_of_all_assignedimage_ids_list = len(all_assignedimage_ids_for_current_annotator)

            prev_image_id = None
            next_image_id = None

            if(current_image_index == length_of_all_assignedimage_ids_list-1):
                next_image_id = all_assignedimage_ids_for_current_annotator[0]
                prev_image_id = all_assignedimage_ids_for_current_annotator[current_image_index - 1]
                #print 'LAST ELEMENT PREV:{} NEXT{}'.format(prev_image_id,next_image_id)

            elif (current_image_index == 0):
                next_image_id = all_assignedimage_ids_for_current_annotator[current_image_index + 1]
                prev_image_id = all_assignedimage_ids_for_current_annotator[length_of_all_assignedimage_ids_list -1]
                #print 'FIRST ELEMENT PREV:{} NEXT{}'.format(prev_image_id,next_image_id)

            else:
                next_image_id = all_assignedimage_ids_for_current_annotator[current_image_index + 1]
                prev_image_id = all_assignedimage_ids_for_current_annotator[current_image_index - 1]
                #print 'ANY MIDDLE ELEMENT PREV:{} NEXT:{}'.format(prev_image_id,next_image_id)

            if (prev):
                image_id = prev_image_id

            if (next):
                image_id = next_image_id


            print 'CURRENT IMAGE_ID {}'.format(image_id)

            '''END:  required code for INFO:2'''

            ''' INFO 3 :Get the current image id and url from
             database and display the image in html page'''

            current_url = query_db_for_display_url(image_id,None)

            ## check image annotated field to redirect to another page
            current_image_info = all_id_annotated_info_dict_list.get(image_id)
            current_image_annotated_info = current_image_info["annotated"]
            print " -------------------- "
            print  current_image_annotated_info

            ###Here working with the text analysis data
            text_data = retrun_text_data_for_id(image_id)
            ###Here working with the text analysis data
            liketkit = None
            for k, v in text_data.items():
                if (k == 'links'):
                    liketkit = text_data[k]
            print '.................{}'.format(liketkit)
            if(text_data.get('NoData')):
                pass
            else:
                del text_data['links']
	    ####COND1: Annotation Complete
            if(current_image_annotated_info):
                return redirect(url_for("completeImageAnnotated",annotator_username = annotator_username,insta_username=insta_username, image_url= current_url,id = image_id ,option = option))
	    ####COND2: Annotation  Not Complete
            else:
                annotator_assigned_instauser_data = annotatorAssignedIdCollection.find({"$and":[{"annotatorusername":annotator_username},{"fashionistausername":insta_username},{"imageid":image_id}]})
                for each_assigned_data in annotator_assigned_instauser_data:
                    saved_annotated_data = each_assigned_data["imageinfo"]["annotateddatajson"]
                print 'Saved data in database {}'.format(saved_annotated_data)

                sorted_annotated_json_data = []
                if saved_annotated_data:
                    for item in saved_annotated_data:
                            print type(item)
                            sorted_annotated_dict ={}
                            annotated_data_dict = item
                            for key,value in item.items():
                                if(key == 'ItemCategory'):
                                    sorted_annotated_dict['aItemCategory'] = value
                                if(key == 'ItemSubCategory'):
                                    sorted_annotated_dict['bItemSubCategory'] = value
                                if (key == 'FinalizeAnnotatedAttributes'):
                                    sorted_annotated_dict['cFinalizeAnnotatedAttributes'] = value
                                    print '****** item: {} ****value {}'.format(key ,value )
                            #print sorted(sorted_annotated_dict)
                            sorted_annotated_json_data.append(sorted_annotated_dict)

                imagebinarydata = getbinarydataforthisimage(image_id)

                return render_template('fashionistasImageAnnotation.html',annotator_username = annotator_username,insta_username=insta_username, id = image_id,annotated_json_data = sorted_annotated_json_data,text_data=text_data,imagebinarydata = imagebinarydata,liketkit = liketkit,option=option)
#### END[appRoute] applications Image Annotation page

#### BEGIN[appRoute] applications Image Annotation Complete page
@annotation_app.route('/completeImageAnnotated', methods=['GET', 'POST'])
@login_required
def completeImageAnnotated():
    if request.method == 'GET':
        print 'GET in [completeImageAnnotated]'
        annotator_username= request.args.get('annotator_username')
        insta_username = request.args.get('insta_username')
        image_url = request.args.get('image_url')
        image_id = request.args.get('id')
        all_id_annotated_info_dict_list = request.args.get('all_id_annotated_info_dict_list')
        text_data = retrun_text_data_for_id(image_id)
	option = request.args.get('option')

        ## request parameter for next image
        next = request.args.get('next')
        ## request parameter for prev image
        prev = request.args.get('prev')

        all_id_annotated_info_dict_list = annotatorAssignedIdCollectionProcessFunctionForBaseBinarydataAndAnnotatedInfo(
            annotator_username, insta_username)
        print len(all_id_annotated_info_dict_list)

        for i in all_id_annotated_info_dict_list:
            all_id_annotated_info_dict_list = i

        # check the list is empty or not this list is required to get the prev and next image if and
        # also provide the annotated information of each image
        if (all_id_annotated_info_dict_list):
            #convert it to remove unicode
            #all_id_annotated_info_dict_list = ast.literal_eval(all_id_annotated_info_dict_list)
            #print annotator_username
            #print insta_username
            #print image_id
            #sprint image_url
            all_assignedimage_ids_for_current_annotator = all_id_annotated_info_dict_list.keys()
            #print (all_assignedimage_ids_for_current_annotator)
            ''' INFO 3 :Get the current image id and url from
             database and display the image in html page'''

            '''BEGIN: required code for INFO:2'''
            # looking for the prev next image id
            current_image_index = all_assignedimage_ids_for_current_annotator.index(image_id)
            length_of_all_assignedimage_ids_list = len(all_assignedimage_ids_for_current_annotator)

            prev_image_id = None
            next_image_id = None

            if(current_image_index == length_of_all_assignedimage_ids_list-1):
                next_image_id = all_assignedimage_ids_for_current_annotator[0]
                prev_image_id = all_assignedimage_ids_for_current_annotator[current_image_index - 1]
                #print 'LAST ELEMENT PREV:{} NEXT{}'.format(prev_image_id,next_image_id)

            elif (current_image_index == 0):
                next_image_id = all_assignedimage_ids_for_current_annotator[current_image_index + 1]
                prev_image_id = all_assignedimage_ids_for_current_annotator[length_of_all_assignedimage_ids_list -1]
                #print 'FIRST ELEMENT PREV:{} NEXT{}'.format(prev_image_id,next_image_id)

            else:
                next_image_id = all_assignedimage_ids_for_current_annotator[current_image_index + 1]
                prev_image_id = all_assignedimage_ids_for_current_annotator[current_image_index - 1]
                #print 'ANY MIDDLE ELEMENT PREV:{} NEXT:{}'.format(prev_image_id,next_image_id)

            if (prev):
                image_id = prev_image_id

            if (next):
                image_id = next_image_id


            print 'CURRENT IMAGE_ID {}'.format(image_id)

            '''END:  required code for INFO:2'''

            ''' INFO 3 :Get the current image id and url from
             database and display the image in html page'''


            current_url = query_db_for_display_url(image_id,None)

            #retrieve annotated information for an image id,annotator and instagram user
            if annotator_username and insta_username and image_id:
                annotator_assigned_instauser_data = annotatorAssignedIdCollection.find({"$and":[{"annotatorusername":annotator_username},{"fashionistausername":insta_username},{"imageid":image_id}]})
                for i in annotator_assigned_instauser_data:
                    #print 'retrieve data forid {} is {}'.format(image_id,i)
                    annotated_json_data = i["imageinfo"]["annotateddatajson"]
                    annotated_style = i["imageinfo"]["styles"]
                    #print 'DB Annotated DATA {}'.format(annotated_json_data)
                print annotated_json_data
                sorted_annotated_json_data = []

                ###Here working with the text analysis data
                text_data = retrun_text_data_for_id(image_id)
                ###Here working with the text analysis data

                liketkit = None
                for k, v in text_data.items():
                    if (k == 'links'):
                        liketkit = text_data[k]
                print '.................{}'.format(liketkit)
                if (text_data.get('NoData')):
                    pass
                else:
                    del text_data['links']
		## process saved annotated data.
                ## Need to sort to display them in table using jinja2
                for item in annotated_json_data:
                    print type(item)
                    sorted_annotated_dict ={}
                    annotated_data_dict = item
                    for key,value in item.items():
                        if(key == 'ItemCategory'):
                            sorted_annotated_dict['aItemCategory'] = value
                        elif(key == 'ItemSubCategory'):
                            sorted_annotated_dict['bItemSubCategory'] = value
                        elif (key == 'FinalizeAnnotatedAttributes'):
                            sorted_annotated_dict['cFinalizeAnnotatedAttributes'] = value
                        print '****** item: {} ****value {}'.format(key ,value )
                    #print sorted(sorted_annotated_dict)
                    sorted_annotated_json_data.append(sorted_annotated_dict)
                print sorted_annotated_json_data

                imagebinarydata = getbinarydataforthisimage(image_id)

    return render_template('completeImageAnnotated.html',annotator_username = annotator_username,insta_username=insta_username,id = image_id,annotated_json_data = sorted_annotated_json_data,annotated_style=annotated_style,text_data=text_data,imagebinarydata = imagebinarydata,liketkit = liketkit,option = option)
#### END[appRoute] applications Image Annotation Complete page

#####BEGIN Route For Mturk worker#####
@annotation_app.route('/fashionistasImageAnnotationMturkWorker', methods=['GET', 'POST'])
def fashionistasImageAnnotationMturkWorker():
    # POST -handling annotated json data from the  annotator #
    if request.method == "POST":
        print "POST in [fashionistasImageAnnotationMturkWorker]"
        annotation_json = request.json
        annotated_image_id = annotation_json.get("imageid")
        annotated_insta_username = annotation_json.get("instagramuser")
        annotator_username = annotation_json.get("annotator")
        annotated_data = annotation_json.get("annotated_data")
        save_item_check = annotation_json.get("save_item")
        finalize_annotation_check = annotation_json.get("finalizeannotation")
        styles = annotation_json.get("styles")
        itemcount = annotation_json.get("itemcount")
        non_fashion_item = annotation_json.get("nonfashionitem")
        annotated_image_url = annotation_json.get("image_url")
        all_id_annotated_info_dict_list = annotation_json.get("all_id_annotated_info_dict_list")
        deleteitem = annotation_json.get("deleteitem")
	option = '1'

        all_id_annotated_info_dict_list = annotatorAssignedIdCollectionProcessFunctionForBaseBinarydataAndAnnotatedInfo(
            annotator_username, annotated_insta_username)
        print len(all_id_annotated_info_dict_list)

        for i in all_id_annotated_info_dict_list:
            all_id_annotated_info_dict_list = i

        if (deleteitem):
            itemCategorytToDelete = annotation_json.get("itemcategorytodelete")
            delete_status = deleteAnSavedItemCategoryFromannotatorAssignedIdCollection(annotator_username,
                                                                                       annotated_insta_username,
                                                                                       annotated_image_id,
                                                                                       itemCategorytToDelete)

            return Response(json.dumps({"redirect": False, "success": delete_status}), status=200,
                            mimetype='application/json')


        # print 'id : {}--- instaUser: {}--- annottar: {}--- data: {} is save: {}'.format(annotated_image_id, annotated_insta_username,annotator_username,annotated_data,save_item_check)

        ## check if the json_annotated_data is POST for  finalize
        elif (finalize_annotation_check):
            '''
             this if condition check whether the request is finalize or not.
             The frontend only sending the finalize command.
             Back end will only update the 'annotated' field of the image to True.
             SAMPLE DATA IN DATABASE
             { "_id" : ObjectId("5a62121b25664e0924cc338d"),
             "fashionistausername" : "cellajaneblog",
             "annotatorusername" : "ann7",
             "imageinfo" : { "fashionistausername" : "cellajaneblog",
             "annotateddatajson" : null,
              "annotated" : false ,
              "styles":"chich style" },
             "imageid" : "1682056482685700593" }

             '''
            annotatorAssignedIdCollectionFinalizeFunction(annotator_username, annotated_insta_username,
                                                          annotated_image_id, styles)
            #print 'FINALIZE {}'.format(
            #"https://shatha2.it.kth.se/singleUserFolder/" + annotated_insta_username + "?annotator_username=" + annotator_username)

            ## https: // www.mturk.com / mturk / externalSubmit?favoriteColor = blue & favoriteNumber = 7 & ...
            ##Redirect the annotator to mturk link
            #redirect_mturk_url = 'https://workersandbox.mturk.com/mturk/externalSubmit?styles='+styles+'&itemcount='+str(itemcount)
            redirect_mturk_url = 'https://workersandbox.mturk.com/mturk/externalSubmit'

            redirect_complete_url = url_for("completeImageAnnotatedMturkWorker", annotator_username=annotator_username,
                                            insta_username=annotated_insta_username, id=annotated_image_id)
            return Response(json.dumps({"redirect": True,
                                        "redirect_url": redirect_complete_url,
                                        "success": True}), mimetype='application/json')

        elif (non_fashion_item):
            ## NOT FASHION RELATED IMAGE
            non_fashion_image_db = annotatorAssignedIdCollection.find({"$and": [
                {"annotatorusername": annotator_username}, {"fashionistausername": annotated_insta_username},
                {"imageid": annotated_image_id}]})
            annotatorAssignedIdCollection.update({"$and": [{"annotatorusername": annotator_username},
                                                           {"fashionistausername": annotated_insta_username},
                                                           {"imageid": annotated_image_id}]}, {
                                                     "$set": {"imageinfo.annotated": True,
                                                              "imageinfo.imageid": annotated_image_id,
                                                              "imageinfo.fashionistausername": annotated_insta_username,
                                                              "imageinfo.annotateddatajson": [
                                                                  {"ItemCategory": "Non Fashion  item"}]}})

            for i in non_fashion_image_db:
                print 'NOT FAHSION RELATED IMAGE {} {} '.format(i,
                                                                "https://shatha2.it.kth.se/singleUserFolder/" + annotated_insta_username + "?annotator_username=" + annotator_username)
            return Response(json.dumps({"redirect": True,
                                        "redirect_url": "https://shatha2.it.kth.se/singleUserFolder/" + annotated_insta_username + "?annotator_username=" + annotator_username+"&option="+option,
                                        "success": True}), mimetype='application/json')

        ## check if the json_annotated_data is POST for save or finalize
        elif (save_item_check):
            print "--------------Only save item in database do not set annotated field to true"
            saved_data, item_exist_boolean = saveItemDataToannotatorAssignedIdCollection(annotator_username,
                                                                                         annotated_insta_username,
                                                                                         annotated_image_id,
                                                                                         annotated_data)

            print saved_data
            print 'Boolean for item existance {} '.format(item_exist_boolean)
            # annotated_data
            # sannotatorAssignedIdCollectionUpdateFunction()

            print json.dumps({"redirect": False, "success": True, "saveditemindb": saved_data})

            sorted_annotated_json_data = []

            for item in saved_data:
                print type(item)
                sorted_annotated_dict = {}
                annotated_data_dict = item
                for key, value in item.items():
                    if (key == "ItemCategory"):
                        sorted_annotated_dict["aItemCategory"] = value
                    if (key == "ItemSubCategory"):
                        sorted_annotated_dict["bItemSubCategory"] = value
                    if (key == "FinalizeAnnotatedAttributes"):
                        sorted_annotated_dict["cFinalizeAnnotatedAttributes"] = value
                        print '****** item: {} ****value {}'.format(key, value)
                # print sorted(sorted_annotated_dict)
                sorted_annotated_json_data.append(sorted_annotated_dict)
            # sorted_annotated_json_data = ast.literal_eval(json.dumps(sorted_annotated_json_data))
            sorted_annotated_json_data = json.dumps(sorted_annotated_json_data)
            # final_data = json.dumps(sorted_annotated_json_data)

            redirect_url = url_for('fashionistasImageAnnotationMturkWorker',
                                   annotator_username=annotator_username,
                                   insta_username=annotated_insta_username,
                                   image_url=annotated_image_url,
                                   id=annotated_image_id,
                                   annotated_json_data=sorted_annotated_json_data)
            print redirect_url
            print sorted_annotated_json_data
            return Response(json.dumps({"redirect": True,
                                        "redirect_url": redirect_url,
                                        "success": True,
                                        "saveditemindb": saved_data}),
                            status=200, mimetype='application/json')
            ##return render_template('fashionistasImageAnnotation.html',annotator_username = annotator_username,insta_username=annotated_insta_username, image_url= annotated_image_url,id = annotated_image_id,all_id_annotated_info_dict_list = all_id_annotated_info_dict_list,annotated_json_data = sorted_annotated_json_data)

    if request.method == "GET":
        print 'GET in [fashionistasImageAnnotationMturkWorker]'
        annotator_username = request.args.get('annotator_username')
        insta_username = request.args.get('insta_username')
        image_url = request.args.get('image_url')
        image_id = request.args.get('img_id')
	option = request.args.get('option')
        all_id_annotated_info_dict_list = request.args.get('all_id_annotated_info_dict_list')

        ## request parameter for next image
        next = request.args.get('next')
        ## request parameter for prev image
        prev = request.args.get('prev')

        ## request parameter for saved item
        annotated_json_data = request.args.get('annotated_json_data')
        # annotated_json_data = ast.literal_eval(annotated_json_data)
        if (annotated_json_data):
            image_id = request.args.get('id')
        all_id_annotated_info_dict_list = annotatorAssignedIdCollectionProcessFunctionForBaseBinarydataAndAnnotatedInfo(
            annotator_username, insta_username)
        print len(all_id_annotated_info_dict_list)

        for i in all_id_annotated_info_dict_list:
            all_id_annotated_info_dict_list = i

        # check the list is empty or not. this list is required to get the prev and next image if and
        # also provide the annotated information of each image
        if (all_id_annotated_info_dict_list):
            # convert it to remove unicode
            # all_id_annotated_info_dict_list = ast.literal_eval(all_id_annotated_info_dict_list)
            print annotator_username
            print insta_username
            print image_id
            print image_url
            print annotated_json_data
            all_assignedimage_ids_for_current_annotator = all_id_annotated_info_dict_list.keys()
            # print (all_assignedimage_ids_for_current_annotator)
            ''' INFO 3 :Get the current image id and url from
             database and display the image in html page'''

            '''BEGIN: required code for INFO:2'''
            # looking for the prev next image id
            current_image_index = all_assignedimage_ids_for_current_annotator.index(image_id)
            length_of_all_assignedimage_ids_list = len(all_assignedimage_ids_for_current_annotator)

            prev_image_id = None
            next_image_id = None

            if (current_image_index == length_of_all_assignedimage_ids_list - 1):
                next_image_id = all_assignedimage_ids_for_current_annotator[0]
                prev_image_id = all_assignedimage_ids_for_current_annotator[current_image_index - 1]
                # print 'LAST ELEMENT PREV:{} NEXT{}'.format(prev_image_id,next_image_id)

            elif (current_image_index == 0):
                next_image_id = all_assignedimage_ids_for_current_annotator[current_image_index + 1]
                prev_image_id = all_assignedimage_ids_for_current_annotator[length_of_all_assignedimage_ids_list - 1]
                # print 'FIRST ELEMENT PREV:{} NEXT{}'.format(prev_image_id,next_image_id)

            else:
                next_image_id = all_assignedimage_ids_for_current_annotator[current_image_index + 1]
                prev_image_id = all_assignedimage_ids_for_current_annotator[current_image_index - 1]
                # print 'ANY MIDDLE ELEMENT PREV:{} NEXT:{}'.format(prev_image_id,next_image_id)

            if (prev):
                image_id = prev_image_id

            if (next):
                image_id = next_image_id

            print 'CURRENT IMAGE_ID {}'.format(image_id)

            '''END:  required code for INFO:2'''

            ''' INFO 3 :Get the current image id and url from
             database and display the image in html page'''

            current_url = query_db_for_display_url(image_id, None)

            ## check image annotated field to redirect to another page
            current_image_info = all_id_annotated_info_dict_list.get(image_id)
            current_image_annotated_info = current_image_info["annotated"]
            print " -------------------- "
            print  current_image_annotated_info

            ###Here working with the text analysis data
            text_data = retrun_text_data_for_id(image_id)
            ###Here working with the text analysis data
            liketkit = None
            for k, v in text_data.items():
                if (k == 'links'):
                    liketkit = text_data[k]
            print '.................{}'.format(liketkit)
            if (text_data.get('NoData')):
                pass
            else:
                del text_data['links']
            if (current_image_annotated_info):
                return redirect(url_for("completeImageAnnotatedMturkWorker", annotator_username=annotator_username,
                                        insta_username=insta_username, image_url=current_url, id=image_id))

            else:
                annotator_assigned_instauser_data = annotatorAssignedIdCollection.find({"$and": [
                    {"annotatorusername": annotator_username}, {"fashionistausername": insta_username},
                    {"imageid": image_id}]})
                for each_assigned_data in annotator_assigned_instauser_data:
                    saved_annotated_data = each_assigned_data["imageinfo"]["annotateddatajson"]
                print 'Saved data in database {}'.format(saved_annotated_data)

                sorted_annotated_json_data = []
                if saved_annotated_data:
                    for item in saved_annotated_data:
                        print type(item)
                        sorted_annotated_dict = {}
                        annotated_data_dict = item
                        for key, value in item.items():
                            if (key == 'ItemCategory'):
                                sorted_annotated_dict['aItemCategory'] = value
                            if (key == 'ItemSubCategory'):
                                sorted_annotated_dict['bItemSubCategory'] = value
                            if (key == 'FinalizeAnnotatedAttributes'):
                                sorted_annotated_dict['cFinalizeAnnotatedAttributes'] = value
                                print '****** item: {} ****value {}'.format(key, value)
                        # print sorted(sorted_annotated_dict)
                        sorted_annotated_json_data.append(sorted_annotated_dict)

                imagebinarydata = getbinarydataforthisimage(image_id)

                return render_template('fashionistasImageAnnotationMturkWorker.html', annotator_username=annotator_username,
                                       insta_username=insta_username, id=image_id,
                                       annotated_json_data=sorted_annotated_json_data, text_data=text_data,
                                       imagebinarydata=imagebinarydata, liketkit=liketkit ,option = option)


#####END Route For Mturk worker#####
#####BEGIN Route For Mturk worker Completed View #####
@annotation_app.route('/completeImageAnnotatedMturkWorker', methods=['GET', 'POST'])
def completeImageAnnotatedMturkWorker():
    if request.method == 'GET':
        print 'GET in [completeImageAnnotated]'
        annotator_username= request.args.get('annotator_username')
        insta_username = request.args.get('insta_username')
        image_url = request.args.get('image_url')
        image_id = request.args.get('id')
	option = request.args.get('option')
        all_id_annotated_info_dict_list = request.args.get('all_id_annotated_info_dict_list')
        text_data = retrun_text_data_for_id(image_id)

        # retrieve annotated information for an image id,annotator and instagram user
        if annotator_username and insta_username and image_id:
            annotator_assigned_instauser_data = annotatorAssignedIdCollection.find({"$and": [
                {"annotatorusername": annotator_username}, {"fashionistausername": insta_username},
                {"imageid": image_id}]})
            for i in annotator_assigned_instauser_data:
                # print 'retrieve data forid {} is {}'.format(image_id,i)
                annotated_json_data = i["imageinfo"]["annotateddatajson"]
                annotated_style = i["imageinfo"]["styles"]
                # print 'DB Annotated DATA {}'.format(annotated_json_data)
            print annotated_json_data
            sorted_annotated_json_data = []

            ###Here working with the text analysis data
            text_data = retrun_text_data_for_id(image_id)
            ###Here working with the text analysis data

            liketkit = None
            for k, v in text_data.items():
                if (k == 'links'):
                    liketkit = text_data[k]
            print '.................{}'.format(liketkit)
            if (text_data.get('NoData')):
                pass
            else:
                del text_data['links']

            for item in annotated_json_data:
                print type(item)
                sorted_annotated_dict = {}
                annotated_data_dict = item
                for key, value in item.items():
                    if (key == 'ItemCategory'):
                        sorted_annotated_dict['aItemCategory'] = value
                    elif (key == 'ItemSubCategory'):
                        sorted_annotated_dict['bItemSubCategory'] = value
                    elif (key == 'FinalizeAnnotatedAttributes'):
                        sorted_annotated_dict['cFinalizeAnnotatedAttributes'] = value
                    print '****** item: {} ****value {}'.format(key, value)
                # print sorted(sorted_annotated_dict)
                sorted_annotated_json_data.append(sorted_annotated_dict)
            print sorted_annotated_json_data

            imagebinarydata = getbinarydataforthisimage(image_id)

    return render_template('completeImageAnnotatedMturkWorker.html', annotator_username=annotator_username,
                           insta_username=insta_username, id=image_id, annotated_json_data=sorted_annotated_json_data,
                           annotated_style=annotated_style, text_data=text_data, imagebinarydata=imagebinarydata,
                           liketkit=liketkit,option = option)


#####END Route For Mturk worker Completed View #####

def query_db_for_display_url(id,username):
    ''' function to query the display url for an image id.It queries both in liketkitCollection and
    swedishCollection and return url if found.
    :parameter  id: image id to search in database
                username :username to search in database

    :return display_url: an url if id not null
            profile_url: any url if id not null'''

    url = None

    #this if takes an image id and gets the display_url for that image
    if id:
        liketkit = liketkitCollection.find({"id": id})
        if(liketkit.count()>0):
            for i in liketkit:
                #print 'SAMPLE DAT IN DB {}'.format(i)
                url = i['display_url']
        else:
            swedish = swedishCollection.find({"id": id})
            if(swedish.count()>0):
                for i in swedish:
                    url = i['display_url']
        return url

    #this if takes an username and provides any image url to display in the allUser.html view
    elif username:
        profile_index = 4
        liketkit = liketkitCollection.find({"username": username})
        if(liketkit.count()>0):
            if(liketkit[profile_index]['display_url']):
                url = liketkit[profile_index]['display_url']

        else:
            swedish = swedishCollection.find({"username": username})
            if(swedish.count()>0):
                if(liketkit.count()>0):
                    url = swedish[profile_index]['display_url']
        return url
    return None

def annotatorAssignedIdCollectionProcessFunction(annotatorusername,fashionistausername):
    '''function to retrieve data for an image  from  collection "annotateddatadetailwithuser".Data id stored in the structure:
     { "_id" : ObjectId("5a62121b25664e0924cc338d"),
     "fashionistausername" : "cellajaneblog",
     "annotatorusername" : "ann7",
      "imageinfo" : { "fashionistausername" : "cellajaneblog", "annotateddatajson" : null, "annotated" : false },
      "imageid" : "1682056482685700593" }
      :parameter annotatorusername, imageid,fashionistausername
      :return adictionary
    '''
    #this if takes username and annotatedinfo and creates a list of dictionary as :
    # {'id':'12734734','annurl':{'url':'http:/.....','annotated':Ture/false}}
    if annotatorusername and fashionistausername:
        annotator_assigned_instauser_data = annotatorAssignedIdCollection.find({"$and":[{"annotatorusername":annotatorusername},{"fashionistausername":fashionistausername}]})
        annotator_assigned_id_set = set()
        id_annotated_info_dict = {} #this dict conatains thedata As: {'id':'12734734','annurl':{'url':'http:/.....','annotated':Ture/false}}
        id_annotated_info_dict_list = []
        print 'annotated info required'
        for each_data in annotator_assigned_instauser_data:
            imageid = each_data["imageid"]
            annotator_assigned_id_set.add(imageid)
            id_annotated_info_dict[imageid] = {}
            id_annotated_info_dict[imageid]["annotated"] = each_data["imageinfo"]["annotated"]
            url = query_db_for_display_url(imageid, None)
            id_annotated_info_dict[imageid]["url"] = url

        id_annotated_info_dict_list.append(id_annotated_info_dict)
        #print ' id-annotated dict ------ {}'.format(id_annotated_info_dict_list)
        return id_annotated_info_dict_list
    #this if takes an annotatorusername and gives the assigned instagramusers list corresponding to him
    elif annotatorusername:
        annotator_assigned_fashionista_list = set()
        annotator_all_data = annotatorAssignedIdCollection.find({"annotatorusername":annotatorusername})
        for data in annotator_all_data:
            insta_user = data["fashionistausername"]
            annotator_assigned_fashionista_list.add(insta_user)
        return annotator_assigned_fashionista_list

#### BEGIN function to create dictionary list for  Single Users Gallery View
def annotatorAssignedIdCollectionProcessFunctionForBaseBinarydataAndAnnotatedInfo(annotatorusername,fashionistausername):
    '''function to retrieve data for an image  from  collection "annotateddatadetailwithuser".Data id stored in the structure:
     { "_id" : ObjectId("5a62121b25664e0924cc338d"),
     "fashionistausername" : "cellajaneblog",
     "annotatorusername" : "ann7",
      "imageinfo" : { "fashionistausername" : "cellajaneblog", "annotateddatajson" : null, "annotated" : false },
      "imageid" : "1682056482685700593" }
      :parameter annotatorusername, imageid,fashionistausername
      :return adictionary
    '''
    #this if takes username and annotatedinfo and creates a list of dictionary as :
    # {'id':'12734734','annurl':{'url':'http:/.....','annotated':Ture/false}}
    if annotatorusername and fashionistausername:
        print annotatorusername,fashionistausername
        annotator_assigned_instauser_data = annotatorAssignedIdCollection.find({"$and":[{"annotatorusername":annotatorusername},{"fashionistausername":fashionistausername}]})
        annotator_assigned_id_set = set()
        id_annotated_info_dict = {} #this dict conatains thedata As: {'id':'12734734','annurl':{'url':'http:/.....','annotated':Ture/false}}
        id_annotated_info_dict_list = []
        print 'annotated info required ' +str(annotator_assigned_instauser_data.count())
        for each_data in annotator_assigned_instauser_data:
            imageid = each_data["imageid"]
            annotator_assigned_id_set.add(imageid)
            id_annotated_info_dict[imageid] = {}
            id_annotated_info_dict[imageid]["annotated"] = each_data["imageinfo"]["annotated"]
            #url,imagebinary = query_db_for_display_url(imageid, None)
            #id_annotated_info_dict[imageid]["url"] = url
	    imagebinary = getbinarydataforthisimage(imageid)
            #imagebinary = imagebase64binarycollection.find({"_id":imageid})
            #print str(imagebinary.count())+ "--------"+str(imageid)
            #if(imagebinary.count()>0):
                #for item in imagebinary:
                    #imagebinary = item.get("base64binary")
                    #imgdata = base64.b64decode(imagebinary)
                    #im = Image.open(io.BytesIO(imgdata))
                    #width, height = im.size
                    #print width, height
                    #id_annotated_info_dict[imageid]["imagebinary"] = imagebinary
	    id_annotated_info_dict[imageid]["imagebinary"] = imagebinary
	    #Flag check localisation
	    localisationdata = localiseddata.find({"annotator_name": annotatorusername, "insta_username":fashionistausername,"image_id":imageid})
	    if (localisationdata.count() > 0):
		for item in localisationdata:
		    locstatus = item.get("localisedFlag")
		    id_annotated_info_dict[imageid]["localisedFlag"] = locstatus

	    # Flag check segmentation
	    segmentationdata = segmenteddata.find({"annotator_username": annotatorusername, "insta_username": fashionistausername, "ImageID": imageid})
	    if (segmentationdata.count() > 0):
		for item in segmentationdata:
		    segstatus = item.get("segmentedFlag")
                    id_annotated_info_dict[imageid]["segmentedFlag"] = segstatus

        #print len(id_annotated_info_dict)
        id_annotated_info_dict_list.append(id_annotated_info_dict)
        #print ' id-annotated dict ------ {}'.format(id_annotated_info_dict_list)
        return id_annotated_info_dict_list
    #this if takes an annotatorusername and gives the assigned instagramusers list corresponding to him
    elif annotatorusername:
        annotator_assigned_fashionista_list = set()
        annotator_all_data = annotatorAssignedIdCollection.find({"annotatorusername":annotatorusername})
        for data in annotator_all_data:
            insta_user = data["fashionistausername"]
            annotator_assigned_fashionista_list.add(insta_user)
        return annotator_assigned_fashionista_list
#### END function to create dictionary list for  Single Users Gallery View


#### BEGIN function to update finalize complete info for a image  and update style
def annotatorAssignedIdCollectionFinalizeFunction(annotatorusername,fashionistausername,imageid,styles):
    '''
    function to update data for an image  from  collection "annotateddatadetailwithuser".Data id stored in the structure:

     { "_id" : ObjectId("5a62121b25664e0924cc338d"),
     "fashionistausername" : "cellajaneblog",
     "annotatorusername" : "ann7",
     "imageinfo" : { "fashionistausername" : "cellajaneblog",
     "annotateddatajson" : null,
     "annotated" : false,
     "styles":"chich style" },
     "imageid" : "1682056482685700593"}
      :parameter annotatorusername, imageid,fashionistausername
      :return a dictionary
    '''

     ##'''{u'colour': [], u'pattern': [], u'brand': [u'as98', u'aaiko'], u'material': [], u'otherdetails': u'', u'length': [], u'collection': [], u'trouserrise': [], u'itemSubCategory': u'flares', u'lining': [], u'occasion': [], u'collartype': [], u'itemCategory': u'jeans'}'''

    db_id = None
    if annotatorusername and fashionistausername and imageid :
        annotator_assigned_instauser_data = annotatorAssignedIdCollection.find({"$and":[{"annotatorusername":annotatorusername},{"fashionistausername":fashionistausername},{"imageid":imageid}]})
        for each_assigned_data in annotator_assigned_instauser_data:
            db_id = each_assigned_data["_id"]
            print each_assigned_data
            #checking annotated field is True
            if (each_assigned_data["imageinfo"]["annotated"]):
                if(each_assigned_data["imageinfo"]["annotateddatajson"]):
                    print "annotated true and some json data in database" + str(db_id)

                else:
                    print "annotated is true and there is no data in database"
            #checking annotated field is False
            else:# annotated field is false so update database
                saved_items_len = len(each_assigned_data["imageinfo"]["annotateddatajson"])
                #print ">>>>>>>>" + str(saved_items_len)
                if(saved_items_len > 0 and db_id):
                    annotatorAssignedIdCollection.update({"$and":[{"annotatorusername":annotatorusername},{"fashionistausername":fashionistausername},{"imageid":imageid}]},{"$set":{"imageinfo.annotated":True,"imageinfo.imageid":imageid,"imageinfo.fashionistausername":fashionistausername,"imageinfo.styles":styles}})
                    update_assign_db_info = annotatorassignedimagelist.find({"_id": annotatorusername})
                    if (update_assign_db_info.count() > 0):
                        for data in update_assign_db_info:
                            imageList = data.get('imageList')

                            for i, each_item in enumerate(imageList):
                                print i, each_item
                                if (imageid in each_item.values()):
                                    print "FOUND"
                                    imageList[i]["annotated"] = True
                                    annotatorassignedimagelist.update({"_id": annotatorusername},
                                                                      {"$set": {"imageList": imageList}})
                                    print imageList
                                    break

                #else:
                    #annotatorAssignedIdCollection.update({"$and":[{"annotatorusername":annotatorusername},{"fashionistausername":fashionistausername},{"imageid":imageid}]},{"$set":{"imageinfo.annotated":True,"imageinfo.imageid":imageid,"imageinfo.fashionistausername":fashionistausername,"imageinfo.annotateddatajson":json_data_to_update}})

        annotator_assigned_instauser_data = annotatorAssignedIdCollection.find({"$and":[{"annotatorusername":annotatorusername},{"fashionistausername":fashionistausername},{"imageid":imageid}]})
        for each_assigned_data in annotator_assigned_instauser_data:
            print 'After Update{}'.format(each_assigned_data)

        #{"$set":{"imageinfo.annotated":True,"imageinfo.imageid":current_image_id,"imageinfo.fashionistausername":fashionistausername,"imageinfo.annotateddatajson":json_data_to_update}}
    print "update"
#### END function to update finalize complete info for a image  and update style

#### BEGIN function to 'Save' a Annottaion Item for a image
def saveItemDataToannotatorAssignedIdCollection(annotatorusername,fashionistausername,imageid,new_annotated_data):
    #retrieve an existing saved annotated information for an image id,annotator and instagram user
    if annotatorusername and fashionistausername and imageid:
        annotator_saved_instauser_data = annotatorAssignedIdCollection.find({"$and":[{"annotatorusername":annotatorusername},{"fashionistausername":fashionistausername},{"imageid":imageid}]})
        for i in annotator_saved_instauser_data:
           annotated_saved_json_data = i["imageinfo"]["annotateddatajson"]

    #print 'GET DATA FROM DB > {} NEW DATA > {} '.format(annotated_saved_json_data, new_annotated_data)
    '''"annotateddatajson" : [ { "ItemSubCategory" : "cocktail",
                                "ItemCategory" : "dresses",
                                "FinalizeAnnotatedAttributes" : { "Lining" : [ ],
                                "Brand" : [ ], "Material" : [ "cord" ],
                                 "Collection" : [ ], "trouserrise" : [ ],
                                  "Length" : [ "Thigh-Length" ], "Pattern" : [ "colourgradient" ],
                                  "Collartype" : [ "roundneck" ], "Colour" : [ "purple" ], "Occasion" : [ "party" ] } } ]'''
    # If there exist some saved item category in database then retrieve the item category list and and check the existance of new item category
    # if the new item category type already added then do not add the new one
    item_exist_boolean = None
    if(annotated_saved_json_data):
        item_category_list_db = []
        item_set_db = set()
        for item in annotated_saved_json_data:
            image_category_info= item.get("ItemCategory")
            item_category_list_db.append(image_category_info)
            #new_annotated_data.append(item)
        print 'Item Ctaegory Exists {}   '.format(item_category_list_db)
        #Now read the item category for the new saved data
        for the_new_item in new_annotated_data:
            new_annotated_data_item_category = the_new_item["ItemCategory"]
        if new_annotated_data_item_category not in item_category_list_db:
            for item in annotated_saved_json_data:
                new_annotated_data.append(item)
            annotatorAssignedIdCollection.update({"$and":[{"annotatorusername":annotatorusername},{"fashionistausername":fashionistausername},{"imageid":imageid},{"imageinfo.annotated":False}]},{"$set":{"imageinfo.annotateddatajson":new_annotated_data}})
            item_exist_boolean = False
        else:
            notification =" Item category already added"
            print notification
            item_exist_boolean = True
    else:
        #if the annotated data is the first saved item  then update the annotatedjsondata
        annotatorAssignedIdCollection.update({"$and":[{"annotatorusername":annotatorusername},{"fashionistausername":fashionistausername},{"imageid":imageid},{"imageinfo.annotated":False}]},{"$set":{"imageinfo.annotateddatajson":new_annotated_data}})
        item_exist_boolean = False



    ##checking data after update
    annotator_assigned_instauser_data = annotatorAssignedIdCollection.find({"$and":[{"annotatorusername":annotatorusername},{"fashionistausername":fashionistausername},{"imageid":imageid}]})
    for each_assigned_data in annotator_assigned_instauser_data:
        saved_annotated_data = each_assigned_data["imageinfo"]["annotateddatajson"]
        #print 'After Update {}'.format(saved_annotated_data)

    return saved_annotated_data,item_exist_boolean
#### END function to 'Save' a Annottaion Item for a image

#### BEGIN function delete annotated Item from database
def deleteAnSavedItemCategoryFromannotatorAssignedIdCollection(annotatorusername,fashionistausername,imageid,itemCtegoryToDelete):
    db_id = None
    delete_item_status= False
    if annotatorusername and fashionistausername and imageid:
        annotator_saved_instauser_data = annotatorAssignedIdCollection.find({"$and":[{"annotatorusername":annotatorusername},{"fashionistausername":fashionistausername},{"imageid":imageid}]})
        for i in annotator_saved_instauser_data:
            annotated_saved_json_data = i["imageinfo"]["annotateddatajson"]
            db_id = i["_id"]

        #print 'GET DATA FROM DB > {} Will delete >>> {} '.format(annotated_saved_json_data, itemCtegoryToDelete)

        if(annotated_saved_json_data):
            item_category_saved_data_list_db = []
            item_set_db = set()
            for item in annotated_saved_json_data:
                image_category_info= item.get("ItemCategory")
                image_sub_category_info = item.get("ItemSubCategory")
                image_finalize_annotated_data_info = item.get("FinalizeAnnotatedAttributes")
                '''Data structure get from database: "annotateddatajson" : [ { "ItemSubCategory" : "totebags",
                                            "ItemCategory" : "bags",
                                            "FinalizeAnnotatedAttributes" : { "Pattern" : [ ], "Brand" : [ "Abro" ], "Material" : [ "crocheted" ], "otherdetails" : "", "Collection" : [ "spring-summer" ], "Occasion" : [ "evening" ], "Colour" : [ "black" ] } },
                                            { "ItemSubCategory" : "sunglasses",
                                             "ItemCategory" : "accessories",
                                             "FinalizeAnnotatedAttributes" : { "Brand" : [ "abercrombieandfitch" ], "Material" : [ "crocheted" ], "otherdetails" : "", "Collection" : [ "spring-summer" ], "Occasion" : [ "leisure" ], "Colour" : [ "black" ] } },
                                              { "ItemSubCategory" : "cocktail",
                                               "ItemCategory" : "dresses",
                                               "FinalizeAnnotatedAttributes" : { "Pattern" : [ "burnout" ], "Brand" : [ "abercrombieandfitch" ], "Material" : [ "cashmere" ], "otherdetails" : "", "Collection" : [ "autumn-winter" ], "Length" : [ "Calf-Length" ], "Collartype" : [ "backless" ], "Occasion" : [ "evening" ], "Colour" : [ "beige" ] } } ]'''
                #item_category_list_db.append(image_category_info)
                if image_category_info == itemCtegoryToDelete:

                    break
            #print len(annotated_saved_json_data)
            annotated_saved_json_data[:] = [d for d in annotated_saved_json_data if d.get("ItemCategory") != itemCtegoryToDelete]
            for itm in annotated_saved_json_data:
                print 'After deleting {}'.format(itm)
            #print len(annotated_saved_json_data)

            annotatorAssignedIdCollection.update({"_id":db_id},{"$set":{"imageinfo.annotateddatajson":annotated_saved_json_data}})

            annotator_saved_instauser_data = annotatorAssignedIdCollection.find({"_id":db_id})
            for i in annotator_saved_instauser_data:
                annotated_saved_json_data_after_delete = i["imageinfo"]["annotateddatajson"]
                #print len(annotated_saved_json_data_after_delete)
                if(len(annotated_saved_json_data) == len(annotated_saved_json_data_after_delete) ):
                    delete_item_status = True
    return delete_item_status
#### END function delete annotated Item from database


@annotation_app.route('/stylesCategoriesDetail', methods=['GET'])
def stylesCategoriesDetail():
    annotator_username = request.args.get("annotator_username")
    insta_username = request.args.get("insta_username")

    return render_template('stylesCategoriesDetail.html', annotator_username = annotator_username,insta_username = insta_username)

#####################################################################

@annotation_app.route('/crowdsourcingConfigs', methods=['GET', 'POST'])
def crowdsourcingConfigs():
    #annotator_username = request.args.get("annotator_username")

    MTURK_SANDBOX = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'

    mturk = boto3.client('mturk',
                          aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key,
                          region_name='us-east-1',
                          endpoint_url=MTURK_SANDBOX
                          )
    #
    # flash ("I have $" + mturk.get_account_balance()['AvailableBalance'] + " in my Sandbox account")

    external_content = """
          <ExternalQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd">
            <ExternalURL>https://shatha2.it.kth.se/allUserFolder/shatha</ExternalURL>
            <FrameHeight>400</FrameHeight>
          </ExternalQuestion>
          """
    #
    question = open(name='questions.xml', mode='r').read()
    new_hit = mturk.create_hit(
            Title='Annotate the fashionista image with meaningful labels',
            Description='Read the instructions, and according to them annotate the images',
            Keywords='fashion, annotation, images',
            Reward='0.1',
            MaxAssignments=1,
            LifetimeInSeconds=172800,
            AssignmentDurationInSeconds=600,
            AutoApprovalDelayInSeconds=14400,
            Question=external_content
      )
    #
    hit_group_id = new_hit['HIT']['HITGroupId']
    hit_id = new_hit['HIT']['HITId']

    # Let's construct a URL to access the HIT
    sb_path = "https://workersandbox.mturk.com/mturk/preview?groupId={}"
    hit_url = sb_path.format(hit_group_id)





    # hit_id = '3MD8CKRQZZSP9TT4BFL9HTDRRVLRJW'
    # worker_results = mturk.list_assignments_for_hit(HITId=hit_id, AssignmentStatuses=['Submitted'])
    #
    # if worker_results['NumResults'] > 0:
    #     for assignment in worker_results['Assignments']:
    #         xml_doc = xmltodict.parse(assignment['Answer'])
    #
    #         response_text =  "Worker's answer was:"
    #         if type(xml_doc['QuestionFormAnswers']['Answer']) is list:
    #             # Multiple fields in HIT layout
    #             for answer_field in xml_doc['QuestionFormAnswers']['Answer']:
    #                 response_text += "For input field: " + answer_field['QuestionIdentifier']
    #                 response_text += "Submitted answer: " + answer_field['FreeText']
    #         else:
    #             # One field found in HIT layout
    #             response_text += "For input field: " + xml_doc['QuestionFormAnswers']['Answer']['QuestionIdentifier']
    #             response_text += "Submitted answer: " + xml_doc['QuestionFormAnswers']['Answer']['FreeText']
    # else:
    #     print "No results ready yet"

    return render_template('crowdsourcingConfigs.html', annotator_username=hit_url)
    #return render_template('crowdsourcingConfigs.html', annotator_username='shatha')

    #return render_template('crowdsourcingConfigs.html',annotator_username = "A new HIT has been created. You can preview it here:" + "https://workersandbox.mturk.com/mturk/preview?groupId=" + new_hit['HIT']['HITGroupId'] + "HITID = " + new_hit['HIT']['HITId'] + " (Use to Get Results)")
    #return render_template('crowdsourcingConfigs.html', annotator_username = mturk.get_account_balance()['AvailableBalance'])
######################################################################
@lm.user_loader
def load_user(user_id):
    '''This sets the callback for reloading a user from the session.
        The function you set should take a user ID (a unicode) and return a user object,
        or None if the user does not exist.'''

    u = annotation_app.config['ANNOTATION_USERS_COLLECTION'].find({"_id": user_id})
    if not u:
        return None
    else:
        if(u.count() ==1) :
            for item in u:
                userid_db = item["_id"]
                return User(userid_db)
#### BEGIN function to update the annottaed completion information for Fashionista
def check_annotation_completion_for_each_fashionista(name_propic_json,annotator_username,option):
    complete_annotate_boolean = False
    all_user_update_dict_list = []
    for each_user in name_propic_json:
        complete_annotate_boolean = False
        update_annottaed_info_dict ={}
        fashionista_name = each_user.get('username')
        annotated_info_json = each_user.get('annotation_complete')
        update_annottaed_info_dict['username']= each_user.get('username')
        update_annottaed_info_dict['profile_pic_url']= each_user.get('profile_pic_url')
        update_annottaed_info_dict['name']= each_user.get('name')
        update_annottaed_info_dict['binary_profile_pic_base64'] = each_user.get('binary_profile_pic_base64')
	annotator_saved_instauser_data = None
	localisationdata = None
	segmentationdata = None

        if annotator_username and fashionista_name:
	    if(option == '1'):
                annotator_saved_instauser_data = annotatorAssignedIdCollection.find({"$and":[{"annotatorusername":annotator_username},{"fashionistausername":fashionista_name}]})
	    if(option =='2'):
		annotator_saved_instauser_data = annotatorAssignedIdCollection.find({"$and":[{"annotatorusername":annotator_username},{"fashionistausername":fashionista_name}]})
	        localisationdata = localiseddata.find({"$and":[{"annotator_name": annotator_username, "insta_username": fashionista_name}]})
	    if(option =='3'):
		annotator_saved_instauser_data = annotatorAssignedIdCollection.find({"$and":[{"annotatorusername":annotator_username},{"fashionistausername":fashionista_name}]})
		segmentationdata = segmenteddata.find({"$and":[{"annotator_username": annotator_username, "insta_username": fashionista_name}]})

            if(annotator_saved_instauser_data or localisationdata or segmentationdata):
                all_annotated_info_db_list=[]
                if(option == '1'):
		    for each_annotated_data in annotator_saved_instauser_data:
                       annotated_info_db = each_annotated_data['imageinfo']['annotated']
		       all_annotated_info_db_list.append(annotated_info_db)
		    if len(all_annotated_info_db_list)==0:
                        update_annottaed_info_dict['annotation_complete']= False
                    else:
		            #if(None in all_annotated_info_db_list or False in all_annotated_info_db_list):
			    if(False in all_annotated_info_db_list):
		                update_annottaed_info_dict['annotation_complete']= False
		            if(all(item for item in all_annotated_info_db_list)):
		                update_annottaed_info_dict['annotation_complete']= True
		if(option =='2'):

		    for each_annotated_data in localisationdata:
			annotated_info_db = each_annotated_data['localisedFlag']
			all_annotated_info_db_list.append(annotated_info_db)


		    if not all_annotated_info_db_list:
                        update_annottaed_info_dict['annotation_complete']= False
		    else:
			if (annotator_saved_instauser_data.count() == len(all_annotated_info_db_list)):
			    if(all(item for item in all_annotated_info_db_list)):
		                    update_annottaed_info_dict['annotation_complete']= True



		if(option =='3'):
		   for each_annotated_data in segmentationdata:
			annotated_info_db = each_annotated_data['segmentedFlag']
			all_annotated_info_db_list.append(annotated_info_db)

		   if not all_annotated_info_db_list:
                        update_annottaed_info_dict['annotation_complete']= False
		   else:
			if (annotator_saved_instauser_data.count() == len(all_annotated_info_db_list)):
			    if(all(item for item in all_annotated_info_db_list)):
		                    update_annottaed_info_dict['annotation_complete']= True

            all_user_update_dict_list.append(update_annottaed_info_dict)

    return all_user_update_dict_list
#### END function to update the annottaed completion information for Fashionista

#### BEGIN function to get text-data given a image id from database
def retrun_text_data_for_id(imageid):
    text_analysis_csr = textAnalysisDataCollection.find({"_id": imageid})
    text_data = {}
    if (text_analysis_csr.count() > 0):
        for item in text_analysis_csr:
            print item
            for k, v in item.items():
                if (k != '_id'):
                    text_data[k] = v
        print 'Retrieve text data {}'.format(text_data)

    else:
        print 'NO TEXT_ANALYSIS DATA '
        text_data['NoData'] = 'None'
    return text_data
#### END function to get text-data from database given a image id

#### BEGIN function to get imagebinaryfrom database given a image id
def getbinarydataforthisimage(imageid):
    imagebinary = imagebase64binarycollection.find({"_id": imageid})
    imagebinaryData = None
    if (imagebinary.count() > 0):
        for item in imagebinary:
            imagebinaryData = item.get("base64binary")
    else:
	liketkit = liketkitCollection.find({"id": imageid})
        if (liketkit.count() > 0):
            for i in liketkit:
		path = i['imagepath']
	with open(path, "rb") as image_file:
            encoded_string_pic = base64.b64encode(image_file.read())
	imagebase64binarycollection.insert({"_id": imageid, "base64binary": encoded_string_pic})
      	imagebinaryData = encoded_string_pic

    return imagebinaryData
#### END function to get imagebinaryfrom database given a image id

####function to retrun json data given a file name
def return_json_data(filename):
    json_data = []
    if os.path.isfile(filename) :
        json_file = open(filename)
        json_data = json.load(json_file)
    return json_data


####BEGIN Route for Main page containing options- Annotation ,Localisation and Segmentation ####
@annotation_app.route("/mainpage", methods=['GET', 'POST'])
@login_required
def mainpage():
    if request.method == 'POST':
        print 'POST in [mainpage]'

        checklink = request.form['val']
        print checklink
        return Response(json.dumps({"success": True, "checklink":checklink}))
        #return redirect(url_for("allUserFolder", checklink=checklink))
        #nonfashioncheck = request.form['nonfashion']

    if request.method == "GET":
        annotator_username = request.args.get('annotator_username')
        #print "Hi there"


        return render_template('mainpage.html', annotator_username=annotator_username)
####END Route for Main page containing options- Annotation ,Localisation and Segmentation ####

###BEGIN Function to retrieve Localised images
def getLocBinary(imageid,annotator_username,insta_username):
    imagebinary = imagelocdata.find({"id":imageid,"annotator_username":annotator_username,"insta_username":insta_username})
    imagebinaryData = None
    if (imagebinary.count() > 0):
        for item in imagebinary:
            imagebinaryData = item.get("base64binary")
    return imagebinaryData
###END Function to retrieve Localised images

####BEGIN Route to perform localisation ####
@annotation_app.route("/localisation", methods=['GET', 'POST'])
@login_required
def localisation():
    ''' This function creates the localisation page loading the images.'''
    #imgadr = "../static/Fashionista.jpg" #Not needed now
    if request.method == "POST":
        print "POST in [localisation]"

        nonfashioncheck = request.form['nonfashion']
        print nonfashioncheck

        bin_image = request.form['binimage']
        #print bin_image

        imagedata = request.form['im']
        print imagedata
	option = '2'

        # read as object and format
        # imagedataformatted = json.loads(imagedata)
        # print imagedataformatted

        annotator_username = request.form['annotator_username']

        insta_username = request.form['insta_username']
	localisedflag = True

        # Localisation now works perfect with non fashion and fashion Item
        if nonfashioncheck =="true" :
            print "non fashion"
            localiseddata.insert(
                {"image_id": imagedata, "annotator_name": annotator_username, "insta_username": insta_username,
                 "nonfashion": nonfashioncheck,"localisedFlag": localisedflag})
            print "data inserted for non fashion"
            print json.dumps({'status': 'OK', 'imagedata': imagedata})


        elif nonfashioncheck== "false" :
            print "fashion"
            localisedformdata = request.form['annotation']
            print localisedformdata

            # formats it after reading
            loadedtestformdataformatted = json.loads(localisedformdata)
            print "itsme"
            print loadedtestformdataformatted

            localiseddata.insert(
            {"localisation_data":loadedtestformdataformatted,"image_id": imagedata, "annotator_name": annotator_username, "insta_username": insta_username,
             "nonfashion": nonfashioncheck,"localisedFlag": localisedflag})

            if bin_image != " ":
                print "inserting image binary for localisation"
                imagelocdata.insert({"base64binary": bin_image, "id": imagedata, "annotator_username": annotator_username,
                                 "insta_username": insta_username})
                print "image binary inserted"

            print "data inserted for fashion"
            print json.dumps({'status': 'OK', 'locdata': localisedformdata})

        #redirect_url = "http://127.0.0.1:5000/singleUserFolder/jessi_afshin?annotator_username=l"
        #print redirect_url


        #Check if localisedformdata exist for this item then mark the icon as circle.
        #todo: fix this later while merging and segmentation


        #"https://shatha2.it.kth.se/singleUserFolder/" + annotated_insta_username + "?annotator_username=" + annotator_username,

        return Response(json.dumps({"redirect": True, 'redirect_url': "https://shatha2.it.kth.se/singleUserFolder/"+ insta_username + "?annotator_username=" + annotator_username+"&option="+option,
                                    "success": True}),mimetype='application/json')


        #return json.dumps({'status': 'OK'});


    if request.method == "GET":
        print 'GET in [localisation]'
        annotator_username = request.args.get('annotator_username')
        insta_username = request.args.get('insta_username')
        image_url = request.args.get('image_url')
        image_id = request.args.get('img_id')
	option = request.args.get('option')

        #Prev, Next Functionality
        next = request.args.get('next')

        ## request parameter for prev image
        prev = request.args.get('prev')

        all_id_annotated_info_dict_list = annotatorAssignedIdCollectionProcessFunctionForBaseBinarydataAndAnnotatedInfo(
            annotator_username, insta_username)

        for i in all_id_annotated_info_dict_list:
            all_id_annotated_info_dict_list = i

        if (all_id_annotated_info_dict_list):
            print annotator_username
            print insta_username
            print image_id
            print image_url
            all_assignedimage_ids_for_current_annotator = all_id_annotated_info_dict_list.keys()
            ''' INFO 3 :Get the current image id and url from
             database and display the image in html page'''

            '''BEGIN: required code for INFO:2'''

            # looking for the prev next image id
            current_image_index = all_assignedimage_ids_for_current_annotator.index(image_id)
            length_of_all_assignedimage_ids_list = len(all_assignedimage_ids_for_current_annotator)


            if (current_image_index == length_of_all_assignedimage_ids_list - 1):
                next_image_id = all_assignedimage_ids_for_current_annotator[0]
                prev_image_id = all_assignedimage_ids_for_current_annotator[current_image_index - 1]
                # print 'LAST ELEMENT PREV:{} NEXT{}'.format(prev_image_id,next_image_id)

            elif (current_image_index == 0):
                next_image_id = all_assignedimage_ids_for_current_annotator[current_image_index + 1]
                prev_image_id = all_assignedimage_ids_for_current_annotator[length_of_all_assignedimage_ids_list - 1]
                # print 'FIRST ELEMENT PREV:{} NEXT{}'.format(prev_image_id,next_image_id)

            else:
                next_image_id = all_assignedimage_ids_for_current_annotator[current_image_index + 1]
                prev_image_id = all_assignedimage_ids_for_current_annotator[current_image_index - 1]
                # print 'ANY MIDDLE ELEMENT PREV:{} NEXT:{}'.format(prev_image_id,next_image_id)

            if (prev):
                image_id = prev_image_id

            if (next):
                image_id = next_image_id

            print 'CURRENT IMAGE_ID {}'.format(image_id)

            '''END:  required code for INFO:2'''

            ''' INFO 3 :Get the current image id and url from
             database and display the image in html page'''


        current_url = query_db_for_display_url(image_id, None)
        #Text data stuff starts here
        text_data = retrun_text_data_for_id(image_id)
        liketkit = None
        for k, v in text_data.items():
            if (k == 'links'):
                liketkit = text_data[k]
        print '.................{}'.format(liketkit)




        #resizing functionality
        # first try
        #Note: This is static but useable but the problem is  it gives me Numpy array not jpg
        # URL used: https://www.pyimagesearch.com/2015/03/02/convert-url-to-image-with-python-and-opencv/ and mix
        # https://stackoverflow.com/questions/48121916/numpy-resize-rescale-image
        #img = cv2.imread('current_url')
        #res = cv2.resize(img, dsize=(1000, 600), interpolation=cv2.INTER_CUBIC)
        #image = url_to_image(current_url)
        #print "ouput image url to image"
        #print image
        #img = cv2.imread('image')
        #print "img" #none
        #print img
        #res = cv2.resize(image, dsize=(1000, 600), interpolation=cv2.INTER_CUBIC)
        #print "res"
        #print res


        #resized = Image.fromarray(image)
        #saved = resized.save("op.jpg")

        # second try
        # This works fine statically but when fed URL it resturns a format not url or jpg something PIL.image.JPEGImageFile
        #URL: http://code.activestate.com/recipes/577591-conversion-of-pil-image-and-numpy-array/
        #file = cStringIO.StringIO(urllib.urlopen(current_url).read())
        #image = Image.open(file)

        #response = requests.get(current_url)
        #image = Image.open(BytesIO(response.content))
        #print "Hi I am image"
        #print image

        #basewidth = 600
        #img = Image.open(image)
        #wpercent = (basewidth/float(img.size[0]))
        #hsize = 1000
        #img = image.resize((basewidth,hsize), Image.ANTIALIAS)
        #img.save('/home/m/Downloads/LocalisationForm/LocApp/static/sompic.jpg')
        #print "I am resized one"
        #print img
        #flask.send_file(img, mimetype=JpegImageFile)

        #Note: left hand side variable in render goes to jinja always
        #imagebinarydata = getbinarydataforthisimage(image_id) later if needed

        #do third try here
        #URl:https://mikeboers.github.io/Flask-Images/
        width = 600
        height = 1000
        #Note: This works through jinja, doubt for width and height,also what for images like 640*640

        #resize code
        uri = None

        if (image_id):

            liketkit = liketkitCollection.find({"id": image_id})
            if (liketkit.count() > 0):
                for i in liketkit:
                    uri = i['imagepath']
                    idofthis = i['id']

        #resize
        basewidth = 600
        img = Image.open(uri)
        hsize = 1000
        img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
        for i in image_id:

            img.save('/var/www/annotation_webapp/static/resized/resized_image'+'_'+image_id+'.jpg')




        #image binary of localised image
        imagebinarydata = getbinarydataforthisimage(image_id)
        imagebinarydatas = getLocBinary(image_id, annotator_username, insta_username)

        return render_template('localisation.html',annotator_username=annotator_username,image_url= current_url, uri = uri, width= width,height= height,insta_username=insta_username,id=image_id,text_data=text_data,liketkit = liketkit,imagebinarydata = imagebinarydata,imagebinarydatas=imagebinarydatas,option = option)
####END Route to perform localisation ####

####BEGIN Route for rendering the segmentation platform where segmentation is performed ####
@annotation_app.route("/segmentation", methods=['GET', 'POST'])
@login_required
def segmentation():
    ''' This function creates the localisation page loading the images.'''
    #imgadr = "../static/Fashionista.jpg" #Not needed now
    if request.method == "POST":
        print "POST in [segmentation]"

        #Fetch all json POST OF PIXELS HAPPEN HERE
	print request.data

        pixeldata = json.loads(request.data)
        print pixeldata
        finald = json.dumps(pixeldata) #removes unicode
        print finald

        annotator_username = pixeldata['Annotatorname']
        print annotator_username

        insta_username = pixeldata['Instaname']
        print insta_username

        image_id = pixeldata['ImageID']

        labels = pixeldata['Labels']

        rgbcodes = pixeldata['RGB']

        totallabelcount = pixeldata['Total']

        segmentedpix = pixeldata['segmenteddata']

        image_bin = pixeldata['image']
        #print image_bin
	option = '3'
	segmentedFlag = True

        if image_bin != " ":
            print "inserting image binary"
            imagesegdata.insert({"base64binary":image_bin,"id":image_id,"annotator_username":annotator_username,"insta_username":insta_username})
            print "image binary inserted"

        #todo: fix non fashion item
        if finald != "":
            segmenteddata.insert(
           {"annotator_username":annotator_username,"insta_username":insta_username,"SegmentedData":segmentedpix, "ImageID":image_id,
               "LabelCode":labels, "RGB":rgbcodes,"LabelCount":totallabelcount,"nonfashion":False, "segmentedFlag":segmentedFlag})
            print "data inserted for segmentation"
        #print json.dumps({'status': 'OK', 'label': pixeldata})
        return Response(json.dumps({"redirect": True,
                                    'redirect_url': "https://shatha2.it.kth.se/singleUserFolder/" + insta_username + "?annotator_username=" + annotator_username+"&option="+option,
                                    "success": True}), mimetype='application/json')
        #return json.dumps({'status': 'OK', 'd':pixeldata})

    if request.method == "GET":
        print 'GET in [segmentation]'
        image_id = request.args.get('img_id')
	option = request.args.get('option')

        print image_id
        insta_username = request.args.get('insta_username')
        print insta_username
        annotator_username = request.args.get('annotator_username')
        print annotator_username


        return render_template('segmentation.html',id=image_id,annotator_username=annotator_username,insta_username=insta_username,option =  option)
####END Route for rendering the segmentation platform where segmentation is performed ####

###Function  to retrieve segmented image from Database
def getsegbinary(imageid,annotator_username,insta_username):
    imagebinary = imagesegdata.find({"id":imageid,"annotator_username":annotator_username,"insta_username":insta_username})
    imagebinaryData = None
    if (imagebinary.count() > 0):
        for item in imagebinary:
            imagebinaryData = item.get("base64binary")
    return imagebinaryData

####BEGIN Route for rendering initial segmentation webpage ####
@annotation_app.route("/seg", methods=['GET', 'POST'])
@login_required
def seg():
    ''' This function creates the localisation page loading the images.'''
    #imgadr = "../static/Fashionista.jpg" #Not needed now
    if request.method == "POST":
        print "POST in [seg]"
        #todo: implement POST OF NON FASHION ITEMS happen here
        nonfashioncheck = request.form['nonfashion']
        imagedata = request.form['imageid']
        annotator_username = request.form['annotator_username']
        insta_username = request.form['insta_username']
	option = '3'
	segmentedFlag = True

        segmenteddata.insert(
            {"ImageID": imagedata, "annotator_name": annotator_username, "insta_username": insta_username,
             "nonfashion": nonfashioncheck, "segmentedFlag":segmentedFlag})
        print "data inserted for non fashion"
        print json.dumps({'status': 'OK'})
        return Response(json.dumps({"redirect": True,
                                    'redirect_url': "https://shatha2.it.kth.se/singleUserFolder/" + insta_username + "?annotator_username=" + annotator_username+"&option="+option,
                                    "success": True}), mimetype='application/json')


    if request.method == "GET":
        print 'GET in [seg]'
        annotator_username = request.args.get('annotator_username')
        insta_username = request.args.get('insta_username')
        image_url = request.args.get('image_url')
        image_id = request.args.get('img_id')
	option = request.args.get('option')
        all_id_annotated_info_dict_list = request.args.get('all_id_annotated_info_dict_list')
        print all_id_annotated_info_dict_list
        #Prev, Next Functionality
        next = request.args.get('next')

        ## request parameter for prev image
        prev = request.args.get('prev')

        all_id_annotated_info_dict_list = annotatorAssignedIdCollectionProcessFunctionForBaseBinarydataAndAnnotatedInfo(
            annotator_username, insta_username)

        for i in all_id_annotated_info_dict_list:
            all_id_annotated_info_dict_list = i

        if (all_id_annotated_info_dict_list):
            # convert it to remove unicode
            #all_id_annotated_info_dict_list = ast.literal_eval(all_id_annotated_info_dict_list)
            print annotator_username
            print insta_username
            print image_id
            print image_url
            all_assignedimage_ids_for_current_annotator = all_id_annotated_info_dict_list.keys()
            ''' INFO 3 :Get the current image id and url from
             database and display the image in html page'''

            '''BEGIN: required code for INFO:2'''

            # looking for the prev next image id
            current_image_index = all_assignedimage_ids_for_current_annotator.index(image_id)
            length_of_all_assignedimage_ids_list = len(all_assignedimage_ids_for_current_annotator)


            if (current_image_index == length_of_all_assignedimage_ids_list - 1):
                next_image_id = all_assignedimage_ids_for_current_annotator[0]
                prev_image_id = all_assignedimage_ids_for_current_annotator[current_image_index - 1]
                # print 'LAST ELEMENT PREV:{} NEXT{}'.format(prev_image_id,next_image_id)

            elif (current_image_index == 0):
                next_image_id = all_assignedimage_ids_for_current_annotator[current_image_index + 1]
                prev_image_id = all_assignedimage_ids_for_current_annotator[length_of_all_assignedimage_ids_list - 1]
                # print 'FIRST ELEMENT PREV:{} NEXT{}'.format(prev_image_id,next_image_id)

            else:
                next_image_id = all_assignedimage_ids_for_current_annotator[current_image_index + 1]
                prev_image_id = all_assignedimage_ids_for_current_annotator[current_image_index - 1]
                # print 'ANY MIDDLE ELEMENT PREV:{} NEXT:{}'.format(prev_image_id,next_image_id)

            if (prev):
                image_id = prev_image_id

            if (next):
                image_id = next_image_id

            print 'CURRENT IMAGE_ID {}'.format(image_id)

            '''END:  required code for INFO:2'''

            ''' INFO 3 :Get the current image id and url from
             database and display the image in html page'''
            print "HeloTesting"

        current_url = query_db_for_display_url(image_id, None)

        #Text data stuff starts here
        text_data = retrun_text_data_for_id(image_id)
        liketkit = None
        for k, v in text_data.items():
            if (k == 'links'):
                liketkit = text_data[k]
        print '.................{}'.format(liketkit)

        uri = None

        if (image_id):

            liketkit = liketkitCollection.find({"id": image_id})
            if (liketkit.count() > 0):
                for i in liketkit:
                    uri = i['imagepath']
                    idofthis = i['id']

        #resize
        basewidth = 600
        img = Image.open(uri)
        hsize = 1000
        img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
        for i in image_id:
            img.save(
                '/var/www/annotation_webapp/static/data/images/resized_image' + '_' + image_id + '.jpg')

        #image binary
        imagebinarydata = getbinarydataforthisimage(image_id)
        imagebinarydatas = getsegbinary(image_id, annotator_username, insta_username)

        return render_template('seg.html',annotator_username=annotator_username,image_url= current_url, uri = uri,insta_username=insta_username,id=image_id,text_data=text_data,liketkit = liketkit,imagebinarydata = imagebinarydata, imagebinarydatas=imagebinarydatas,option = option)
####END Route for rendering initial segmentation webpage ####


####BEGIN Route for Localisation page instructions ####
@annotation_app.route('/localisationinstructions', methods=['GET'])
def localisationinstructions():
    annotator_username = request.args.get("annotator_username")
    insta_username = request.args.get("insta_username")

    return render_template('localisationinstructions.html', annotator_username = annotator_username,insta_username = insta_username)
####END Route for Localisation page instructions ####

####BEGIN Route for Segmentation page instructions ####
@annotation_app.route('/segmentationinstructions', methods=['GET'])
def segmentationinstructions():
    annotator_username = request.args.get("annotator_username")
    insta_username = request.args.get("insta_username")

    return render_template('segmentationinstructions.html', annotator_username = annotator_username,insta_username = insta_username)
####END Route for Segmentation page instructions ####

#### Function to  convert image to URL (Not used at the moment, useful for future)
def url_to_image(url):
	# download the image, convert it to a NumPy array, and then read
	# it into OpenCV format
	resp = urllib.urlopen(url)
	image = np.asarray(bytearray(resp.read()), dtype="uint8")
	image = cv2.imdecode(image, cv2.IMREAD_COLOR)

	return image

#### BEGIN Route logout ####
@annotation_app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
#### END Route logout ####

if __name__ == "__main__":

    #run_simple('localhost', 4000, annotation_app,
     #ssl_context=('/home/ummul/FashionRec_DataCollection/AnnotationWebApp/image-annotation-webapp/annotation_webapp/static/appdata/key.crt', '/home/ummul/FashionRec_DataCollection/AnnotationWebApp/image-annotation-webapp/annotation_webapp/static/appdata/key.key'))
    annotation_app.run()
