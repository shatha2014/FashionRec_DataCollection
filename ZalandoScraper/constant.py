
BASE_URL = 'https://www.zalando.co.uk'
BLOUSEAND_TUNIC = 'https://www.zalando.co.uk/womens-clothing-blouses-tunics/'
BLOUSES ='https://www.zalando.co.uk/womens-clothing-blouses/'
SHIRTS='https://www.zalando.co.uk/womens-clothing-shirts/'
TUNIC ='https://www.zalando.co.uk/womens-clothing-tunics/'
DRESSES ='https://www.zalando.co.uk/womens-clothing-dresses/'
COATS = 'https://www.zalando.co.uk/womens-clothing-coats/'
JEANS = 'https://www.zalando.co.uk/womens-clothing-jeans/'
JACKETS = 'https://www.zalando.co.uk/womens-clothing-jackets/'
JUMPER_AND_CARDIGAN = 'https://www.zalando.co.uk/womens-clothing-jumpers-cardigans/'
SKIRTS = 'https://www.zalando.co.uk/womens-clothing-skirts/'
TOPS_AND_TSHIRTS = 'https://www.zalando.co.uk/womens-clothing-tops/'
TIGHT_AND_SOCKS = 'https://www.zalando.co.uk/womens-clothing-tights-socks/'
TROUSER_AND_SHORTS = 'https://www.zalando.co.uk/womens-clothing-trousers/'
SHOES='https://www.zalando.co.uk/womens-shoes/'
BAGS='https://www.zalando.co.uk/bags-accessories-womens-bags/'

ITEM_CATEGORY = ['Blouse & Tunic','Dresses','Coats','Jeans','Jackets','Jumpers and Cardigans','Skirts','Tops and T-shirts','Tight and Socks','Trousers and Shorts','Shoes','Bags']
SUBCAT_LIST_BLOUSES = ['Blouses', 'Shirts', 'Tunic']
SUBCAT_LIST_DRESSES = ['Work Dresses', 'Denim Dresses', 'Casual Dresses','Shirt Dresses', 'Cocktail Dresses', 'Knitted Dresses', 'Maxi Dresses', 'Jersey Dresses']
SUBCAT_LIST_COATS = ['Down Coats', 'Winter Coats',  'Wool Coats', 'Short Coats','Trench Coats', 'Parkas']
SUBCAT_LIST_JEANS = ['Denim Shorts', 'Slim Fit',  'Skinny Fit', 'Flares','Straight Leg', 'Loose Fit', 'Bootcut']
SUBCAT_LIST_JACKETS = ['Winter Jackets', 'Athletic Jackets',  'Fleece Jackets', 'Leather Jackets','Denim Jackets', 'Outdoor Jackets', 'Gilets & Waistcoats', 'Lightweight Jackets','Blazers','Down Jackets', 'Capes']
SUBCAT_LIST_JUMPER = ['Athletic Jackets', 'Hoodies', 'Sweatshirts', 'Fleece Jumpers', 'Cardigans','Jumpers']
SUBCAT_LIST_SKIRT = ['Maxi Skirts', 'Pleated Skirts', 'A-Line Skirts', 'Pencil Skirts','Mini Skirts','Denim Skirts','Leather Skirts']
SUBCAT_LIST_TOP = ['Long Sleeve Tops', 'Vest Tops','Polo Shirts', 'T-Shirts']
SUBCAT_LIST_SHOES = ['Sports Shoes', 'Flip Flops & Beach Shoes', 'Ballet Pumps','Flats & Lace-Ups', 'Boots','Trainers', 'Outdoor Shoes','Heels', 'Sandals','Ankle Boots', 'Slippers','Mules & Clogs']
SUBCAT_LIST_BAG =['Phone Cases', 'Wash bags', 'Tote Bags', 'Sport- & Travel Bags', 'Laptop Bags', 'Shoulder Bags','Rucksacks', 'Clutch Bags']
SUBCAT_LIST_TROUSER = ['Joggers & Sweats','Shorts','Chinos','Playsuits & Jumpsuits','Leggings','Trousers']
SUBCAT_LIST_TIGHT = ['Knee High Socks','Leggings','Socks','Thigh High Socks','Tights','Tight & Socks']


##TODO:check print / printStripe/floralprint
PATTERN = ['animal print','camouflage','checked','colour gradient','colourful', 'floral', 'herringbone','marl', 'paisley','photo print', 'printstriped','plain','polka dot','print','striped']
COLLAR = ['backless','boat neck','button down','cache-coeur','contrast collar', 'cowl neck', 'cup-shaped', 'envelop', 'henley', 'high', 'hood', 'lapel', 'low round neck', 'low v-neck', 'mandarin', 'mao' , 'off-the-shoulder', 'peter pan' , 'polo neck', 'polo shirt', 'round neck', 'shawl' , 'shirt' , 'square neck', 'turn-down' ]
BRAND = ['betsey johnson', 'burberry', 'chanel', 'chole','christian dior','dolce & Gabbana','donna karan','fashion nova','givency','gucci','hermes','hugo boss','karl legerfeld','lacoste','luis vuitton','marc jacobs','micheal kors','moschino','nicole miller','prada','ralph lauren','supreme','stella mccartney','valentino','vera wang','versace','vivienne westwood','yves saint laurent','zara','zac posen','nike','addidas','h&m']
COLOR = ['black', 'brown','beige','grey','white','blue','petrol','turquoise','green','olive','yellow','orange','red','pink', 'lilac','gold','silver','multi-coloured']
MATERIAL = ['braided','cashmere','cord','cotton','crocheted','denim','imitation leather', 'jersey', 'lace','leather','felt','fleece','hardshell','linen','mesh','mohair','modal','platinum','patent','polyester','ribbed','silver','silk','satin','synthetic','softshell','sweat','titanium','textile','viscose','wool']



from pymongo import MongoClient


DB_NAME_ZALANDO_DATA_SET = 'zalandodataset'


DATABASE = MongoClient()[DB_NAME_ZALANDO_DATA_SET]
ZALANDO_DATA_SET_ALL = DATABASE.zalandoproductdetails
ZALANDO_DATA_SEARCH_KEY_PATTERN = DATABASE.zalandodatabypattern
ZALANDO_DATA_SEARCH_KEY_COLLAR = DATABASE.zalandodatabycollar
ZALANDO_DATA_SEARCH_KEY_BRAND = DATABASE.zalandodatabybrand
ZALANDO_DATA_SEARCH_KEY_MATERIAL = DATABASE.zalandodatabymaterial

DB_NAME_INSTAGRAM_USER = 'instagramscraper'
DATABASE_INSTAGRAM_USER = MongoClient()[DB_NAME_INSTAGRAM_USER]
INSTAGRAM_LIKETKIT_USER_COLLECTION = DATABASE_INSTAGRAM_USER.liketoknowituser
INSTAGRAM_DATE_MODIFY = DATABASE_INSTAGRAM_USER.instagrampoststimestamp #id,time




DB_NAME_ANNOTATION_APP = 'annotatorwebapp'
DATABASE3 = MongoClient()[DB_NAME_ANNOTATION_APP]
IMAGEID_TEXT_ANALYSIS_DATA_COLLECTION2 = DATABASE3.imageidtextanalysisdata2
