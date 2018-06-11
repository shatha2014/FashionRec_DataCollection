
from pymongo import MongoClient
from pymongo import ASCENDING
import logging.config
import warnings

warnings.filterwarnings('ignore')

class InstagramDataStore(object):
    """InstagramDataStore for storing scraped items in the database"""
    def __init__(self):
        """
        Create a client connection to the MongoDb instance running on the local machine
        """
        try:
	    global client 
	    client = MongoClient('localhost:27017')
	    global db 
	    db = client.instagramapidata
	    

	except Exception, e:
            print str(e)
        

        # Set up a file logger.
        #self.logger = InstagramDataStore.get_logger(level=logging.DEBUG)
    def insert_into_db_alldata(self,media_id,userid,username,media_location,caption_text,likes_count,liked_users,comments_count,comment_users,images_standard_resolution):
	"""
        Insert the user metadata in database:instagramapidata and collection:allData
        """
	try:
            s = {"mediaid":media_id,"userid":userid, "name" : username,"location":media_location,"caption":caption_text,"totallike":likes_count,"likedusers":liked_users,"totalcomments":comments_count,"commentedusers":comment_users,"url":images_standard_resolution }
	    #dbinsert = client.instagramapidata.create_index([('name', pymongo.ASCENDING)], unique=True)
	    #db_insert = db.testData.create_index("id",unique = True)
	    
	    ##db.allData.drop()
	    db.allData.create_index([("mediaid", ASCENDING)], unique=True)
	    db.allData.insert(s)

	    #print '\n insert data successfully with id'+ str(id_insert)+' \n'
	    print s 
	    print  '\n insert data successfully \n'


	except Exception,e:
	    print 'EXP>'+ str(e)

	

    def insert_into_db(self,id,name):
	"""
        Insert the user metadata in database:instagramapidata and collection:testData
        """
	try:
            s = {"id":id, "Name" : name }
	    #dbinsert = client.instagramapidata.create_index([('name', pymongo.ASCENDING)], unique=True)
	    #db_insert = db.testData.create_index("id",unique = True)
	    #not working when use create_index id_insert = db_insert.insert_one(s).inserted_id;
	    db.testData.create_index([("id", ASCENDING)], unique=True)
	    db.testData.insert(s)

	    #print '\n insert data successfully with id'+ str(id_insert)+' \n'
	    print '\n insert data successfully \n'


	except Exception,e:
	    print 'EXP>'+ str(e)

    def retrieve_from_db(self):
	try:
	    all_user = db.testData.find()
	    print '\n All data from db Database\n'
	    for user in all_user:
		print user
	    
	except Exception,e:
	    print str(e)
    def retrieve_from_db_alldata(self):
	try:
	    all_user = db.allData.find()
	    print '\n All data from db Database\n'
	    
	    return all_user
	    
	except Exception,e:
	    print str(e)


    @staticmethod
    def get_logger(level=logging.WARNING, log_file='instagram-InstagramDataStore.log'):
        '''Returns a file logger.'''
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.NOTSET)

        handler = logging.FileHandler(log_file, 'w')
        handler.setLevel(level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        return logger

