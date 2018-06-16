
Instagram API Application
=================

Instagram API application is a flask based web-solution written in python. The main purpose of this application is to get permission for Instagram API access. Because, Instagram data is required for a cross-domain recommendation system to recognize fashion style using deep learning and recommend fashion cloths. To fulfill the Instagram API review requests condition- privacy policy for data usage and sharing and also the Instagram 'login' experience using a Instagram username and its password is added.
The 'login' option using the Instagram  username and its password ensures that the developed application asks the users permission for basic information data access via API.

Requirements
-----
1. Python version 2.7

Usage
-----
1. Open the terminal and browse to the folder containing 'run.sh' file and execute below command.
```bash
$ bash run.sh
```
2. After executing the command, the url of the application server will appear below. Open the url in any browser and login with any valid Instagram username and password. After successful login, the user will be prompt a option to allow the access of the application 'Fashion Dataset Retriever' for basic informations. Then allow access for the given user.

3.  Follow the instructions inside the module './InstagramScraperAPIVersion' to crawl the basic data and media for the given user.

------








License
-------
All rights reserved to Fashion Recommendation Team , KTH.
