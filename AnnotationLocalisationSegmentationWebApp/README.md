Annotation-Localisation-Segmentattion Web Application
==========================

This is a flask-based web application that is used to annotate a fashion relate image  with all possible attributes according to its fashion items and store data in MongoDB database.Moreover, it facilitates the localisation and pixel-by-pixel segmentation. Its backend is written in python and frontend is written in html, javascript,jquery AJAX and Jinja2. 

Modules 
-----
1. *./node_modules* - contains 3 npm modules - ./base64-arraybuffer, ./css-line-break and ./html2canvas. They are used for localisation and segmentation to capture annotated images and encoding/decoding to base64 binary. 

2. *./static* - contains all the staic data files like- appdata, css, bootstrap, css etc.
3. *./templates* - contains all the front-end view in html.
 

Requirements 
-----
1. Create virtual environment
```bash
$ virtualenv venv-web-solution
```

2. Activate virtual environment 
```bash
$ source venv/bin/activate
```
3. Install required libraries using pip from requirements.txt

```bash
$ pip install requirements.txt
```
4. Start MongoDB(version 2.6.12) using 'mongod' command
```bash
mongod
```
5. The Image Annotation websolution is depend on the instagram fashionistas data in mongo database 'instagramscraper'.To fulfill this requirement one needs to run InstagramScraper app and store instagram data in the corresponding database.After that the solution need to preprocess some data(annottaor create, image conversion to base64 and text_analysis data insert in databse) using the populateDB.py script and assign images to different annotators using assignImageToAnnotator_dynamic_v3.py script.

```bash
python populateDB.py
```
Select - Option 1 to create atleast five annotators. Then again run the script and select Option- '5' to convert all images to base64 binary data. Again run script wit hoption - '7' to process liketkit link and at last option- '8' to insert text analysis data in database.

6. After preprocessing one needs to assign a specific fashionistas image to a annotator .This is done by the script 'assignImageToAnnotator_dynamic_v3.py'. This script has  option-  Assign a batch of images of a specific Fashionista to a specific annotator. After providing the correct annotator and fashionista name, a batch of images will be assigned and inserted into MongoDB.

```bash
python assignImageToAnnotator_dynamic_v3.py
```
7. The next step after image assignment is to start the web solution by runnig the 'views.py' file.

```bash
python views.py

```
However, this websolution is deployed in the Apache server by creating a configuration file and accessible via the link 'https://shatha2.it.kth.se'.

To be able to run it in the Flask development server one needs to add the IP address in the code snippet 'annotation_app.run('IP','PORT')'. Also, need to replace all URL 'https://shatha2.it.kth.se/' to corresponding address with IP and port.

Description
-----

After succesful login you will be redirected to a page that contain three options- 1)Detail Annottaion, 2) Localisation and 3) Segmentation. Selecting any of the three option will direct to a gallery view of different fashionistas. Upon clicking one of the gallery thumbnail you will be redirected to a page where all the assigned images will be visible as thumbnail. Each of the thumbnail contains a checkbox either filled or unfilled.  By clicking a image with unfilled checkbox will be redirected to a page where you can annotate the image. In the annotation page there is provided a dropdown list of fashion item category, subcategory and their attributes. You can annotate one fashion item  and save them. Before adding another fashion item annottaion it is recommended to click clear and add new item button. After completing the annotation for all items click the 'Finalize Annotation' button. After completing the final annotation you will be redirected to the fashionistas gallery folder. 

Usage
-----
Execute following commnad to start web-application:
```bash

python views.py

```
**To Query Database:**

**DB command for Segmentation:**

1. use segmentation   (Always execute it first to use the database)
2. Search based on specific image id of fashionista:
```bash
     db.segmenteddata.find({"ImageID" : "1129741704208628631"}).pretty()
```
3. To see all records
```bash
    db.segmenteddata.find().pretty()
```
4. Search based on specific fashionista name
```bash
    db.segmenteddata.find({"insta_username" : "jessi_afshin"}).pretty()
```
5. Search based on specific annotator name
```bash
    db.segmenteddata.find({"annotator_username" : "mallu"}).pretty()
```




**DB command for Localisation:**
1. use localisation   (Always execute it first to use the database)
2. Search based on specific image id of fashionista
```bash
     db.localiseddata.find({"image_id" : "1129741704208628631"}).pretty()
```
3. To see all records
```bash
    db.localiseddata.find().pretty()
```
4. Search based on specific fashionista name
```bash
    db.localiseddata.find({"insta_username" : "jessi_afshin"}).pretty()
```
5. Search based on specific annotator name
```bash
    db.localiseddata.find({"annotator_name" : "mallu"}).pretty()
```
**DB command for Annotation:**
1. use annotatorwebapp   (Always execute it first to use the database)
2. Search based on specific image id of fashionista and annotator:
```bash
     db.annotateddatadetailwithuser.find({"imageid" : "1662569323480290687","annotatorusername" : "umu","fashionistausername" : "apincholovely"}).pretty()
```
3. To see all records that is annotated:
```bash
    db.annotateddatadetailwithuser.find().pretty()
```
4. Search based on specific fashionista name (which may also contain different annotator images)
```bash
    db.annotateddatadetailwithuser.find({"insta_username" : "jessi_afshin"}).pretty()
```
5. Search based on specific annotator name:
```bash
    db.annotateddatadetailwithuser.find({"annotatorusername" : "umu"}).pretty()
```

License
-------
All rights reserved to Fashion Recommendation Team , KTH.