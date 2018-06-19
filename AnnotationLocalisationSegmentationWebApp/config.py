from pymongo import MongoClient

WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'a random CSRF secret string'
SECRET_KEY = 'thequickbrownfox jumpoverthe lazydog'
#databases
DB_NAME_ANNOTATION_APP = 'annotatorwebapp'
DB_NAME_INSTAGRAM_USER = 'instagramscraper'
DB_NAME_LOCALISATION_APP = 'localisation'
DB_NAME_SEGMENTATION_APP = 'segmentation'

#database connection to annotation-webapp
DATABASE = MongoClient()[DB_NAME_ANNOTATION_APP]

# collection holds annotators list
ANNOTATION_USERS_COLLECTION = DATABASE.users

#collection holds the image id for corresponding user
#ANNOTATION_USER_IAMGEID_COLLECTION = DATABASE.annotationuser  

#this collection holds the images annotated data
ANNOTATE_DETAIL_IAMGEID_USER_COLLECTION = DATABASE.annotateddatadetailwithuser 

#collection holds imagelist for each annottaor {"_id":annotator,"imageidlist":[...,...,..]}
ANNOTATOR_IMAGEID_ASSIGNED_COLLECTION = DATABASE.annotatorimageidlist     
 
#collection holds image binary data {"_id":imageid,"base64binary":base64binary}
IMAGEID_AND_BASE64_BINARY_DATA_COLLECTION = DATABASE.imageidbasebinarydata
#collection holds text analysis data {"_id":<>,"items":[],}
IMAGEID_TEXT_ANALYSIS_DATA_COLLECTION = DATABASE.imageidtextanalysisdata  

#database connection to instagram-scraper
DATABASE_INSTAGRAM_USER = MongoClient()[DB_NAME_INSTAGRAM_USER]
INSTAGRAM_LIKETKIT_USER_COLLECTION = DATABASE_INSTAGRAM_USER.liketoknowituser
INSTAGRAM_SWEDISH_USER_COLLECTION = DATABASE_INSTAGRAM_USER.swedishuser
INSTAGRAM_ALL_USER_ID_COLLECTION = DATABASE_INSTAGRAM_USER.usernameidtable


# Database information for Localization and Segmentation
DATABASE_LOCALISATION = MongoClient()[DB_NAME_LOCALISATION_APP]
LOCALISATION_DATA = DATABASE_LOCALISATION.localiseddata #collection to hold localised data
IMG_BIN_LOC = DATABASE_LOCALISATION.imagelocdata #collection to store localised image binary

DATABASE_SEGMENTATION = MongoClient()[DB_NAME_SEGMENTATION_APP]
SEGMENTATION_DATA = DATABASE_SEGMENTATION.segmenteddata #collection to hold segmented data
IMG_BIN_SEG = DATABASE_SEGMENTATION.imagesegdata #collection to store segmented images based on annotation



COMMON_COUNT = 5

SETTINGS_COLLECTION = DATABASE.settings

DEBUG = True
ALL_FASHIONISTA_LIST = ['cocorocha', 'blaireadiebee', 'hellofashionblog','hapatime', 'lolariostyle', 'cmcoving', 'kaitlynn_carter', 'emmahill', 'kathleen_barnes', 'doina', 'champagneandchanel', 'shortstoriesandskirts', 'lyndiinthecity', 'cellajaneblog', 'jessi_afshin', 'hauteofftherack', 'apinchoflovely', 'holliewdwrd', 'stephsterjovski', 'laurenkaysims', 'samanthabelbel', 'littleblondebook', 'thehouseofsequins', 'oliviarink','themilleraffect','joellefriend','jordanunderwood','kenzasmg','katiesbliss','jaimeshrayber','daphnemodeandthecity','ruerodier','thestylebungalow','babiolesdezoe','sorayabakhtiar','jessannkirby','n_g_le','chicflavours','hellovalentine','the_beauty_issue','themoptop','karazwaanstra','jdfashionfreak','interiordesignerella', 'thedoubletakegirls','jessicawhitaker','polishedavenue','modern.mrs']

