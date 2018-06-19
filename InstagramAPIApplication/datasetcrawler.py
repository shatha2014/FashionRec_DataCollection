#from app import app
import os
from flask import Flask,render_template,request, url_for, redirect,session
from constant import *
from storeDataToDB import InstagramDataStore
import json,ast
import requests
import urllib
import urllib2
global accessToken_gl

app = Flask(__name__)
 
@app.route('/',methods=['GET', 'POST'])
#@app.route('/index',methods=['GET', 'POST'])
def index():
    
    if request.method == 'GET':
	code = request.args.get('code')
	username = request.args.get('username')
        media_show = request.args.get('show_media')
	if code:
	    print  code
	
            url = 'https://api.instagram.com/oauth/access_token'
            values = {
            'client_id':'329baa060a044ea58e966a10e30f5473',
            'client_secret':'30c24436db944af89e953549bb8de647',
            'redirect_uri':REDIRECT_URI,
            'code':code,
            'grant_type':'authorization_code'
            }
            data_access_token = urllib.urlencode(values)
	    print data_access_token
            req = urllib2.Request(url, data_access_token)
            response = urllib2.urlopen(req)
            response_string = response.read()
	    response.close() 
	    
	    print str(response_string)
	    instagram_data = json.loads(response_string)
	    #accessToken_gl.append(json.loads(response_string))
	    if 'access_token' in instagram_data:
	        print ' ACCESSTOKEN::'+instagram_data['access_token'] + " of USER:: "+instagram_data['user']['username']
		login_user = instagram_data['user']['username']
		
		return redirect(url_for('login',current_user = login_user))

            else:
		print 'authentication failure'
      
        if username:
	    
	    print 'MAIN PAGE USER SEARCH' + str(username) 
	    user_dict = {'5467508547':'umu2017','4841977337':'wara.kab'}
	    for uid,name in user_dict.items():
		if username in name:
		    print uid
		    print name
		    break 
		else:
		    name = 'NoUser'  
	    return render_template("templates_view.html",username = name)
 
        if username and media_show: 
	    print "//////"+ username + "///"+ media_show
	    
	    database = InstagramDataStore()
            all_user = InstagramDataStore.retrieve_from_db_alldata(database)
            #alldata = all_user
            print 'datasetCrawler retriever data from database'
            data =[]
    	    for user in all_user:
		#deleting _id as json cannot dump it
		
		current_user_data_show = user[u'name']
		if username in current_user_data_show:
		    print current_user_data_show
	            del user[u'_id']	        
		    alldata = ast.literal_eval(json.dumps(user)) 
       		#print type(alldata)
        	    for key,value  in alldata.items():
	    	        print key,  'corresponds to',value
	    	        data.append(value)
	

    	    total_user = all_user.count()
    	    #print data
            #print len(data)
            return render_template("templates_view.html", content=data, row=total_user,current_user = username)
    
    if request.method == 'POST':
	print 'post method'
        
    
    return render_template("templates_view.html")

@app.route('/login',methods=['GET', 'POST'])
def login():
    
    if request.method == 'GET':
	username = request.args.get('current_user')
	media_list_show = request.args.get('show_media')
	if username:
	    print 'LOGGED IN USER:: '+request.args.get('current_user')
	## here the media list is shown
	if media_list_show:
            print 'SHOW MEDIA:'
	    database = InstagramDataStore()
            all_user = InstagramDataStore.retrieve_from_db_alldata(database)
            #alldata = all_user
            print 'datasetCrawler retriever data from database'
            data =[]
    	    for user in all_user:
		#deleting _id as json cannot dump it
		
		current_user_data_show = user[u'name']
		if username in current_user_data_show:
		    print current_user_data_show
	            del user[u'_id']	        
		    alldata = ast.literal_eval(json.dumps(user)) 
       		#print type(alldata)
        	    for key,value  in alldata.items():
	    	        print key,  'corresponds to',value
	    	        data.append(value)
	

    	    total_user = all_user.count()
    	   
            return render_template("login.html", content=data, row=total_user,current_user = username)

           
    return render_template("login.html",current_user = username)

@app.route('/showdataset',methods=['GET', 'POST'])
def showdataset():

    if request.method == 'GET':
	username = request.args.get('username')
        media_show = request.args.get('show_media')
    database = InstagramDataStore()
    all_user = InstagramDataStore.retrieve_from_db_alldata(database)
    #alldata = all_user
    print 'datasetCrawler retriever data from database'
    data =[]
    for user in all_user:
	#deleting _id as json cannot dump it
	current_user_data_show = user[u'name']
	if username in current_user_data_show:
	    del user[u'_id']
	    alldata = ast.literal_eval(json.dumps(user)) 
            #print type(alldata)
            for key,value  in alldata.items():
	    #print key,  'corresponds to',value
	        data.append(value)
	

    total_user = all_user.count()
    
    return render_template("templates_view.html", content=data, row=total_user,current_user = username)

@app.route('/logininstagram',methods=['GET', 'POST'])
def logininstagram():
    if request.method == 'POST':
        return redirect(url_for('index'))

    if request.method == 'GET':
        instagram_client_id = '329baa060a044ea58e966a10e30f5473'
        instagram_client_secret = '30c24436db944af89e953549bb8de647'
        instagram_redirect_url = REDIRECT_URI
        login_url = 'https://api.instagram.com/oauth/authorize/?client_id=' + instagram_client_id + '&redirect_uri=' +instagram_redirect_url + '&response_type=code&scope=basic'
	print 'redirecting to ->   '+login_url
	
	
    return redirect(login_url )



@app.route("/logout",methods=['GET', 'POST'])
def logout():
	"""Logout Form"""
#	#session['logged_in'] = False
	url = 'http://instagram.com/accounts/logout/'
	return redirect(url)


@app.route('/policy',methods=['GET', 'POST'])

def policy():
    if request.method == 'POST':
        return redirect(url_for('index'))

    # show the form, it wasn't submitted
    return render_template('policy.html')

@app.route('/description',methods=['GET', 'POST'])

def description():
    if request.method == 'POST':
        
        return redirect(url_for('index'))

    # show the form, it wasn't submitted
    return render_template('description.html')


if __name__== "__main__":
	app.secret_key = "123"
	app.run(host = '130.237.20.58')

