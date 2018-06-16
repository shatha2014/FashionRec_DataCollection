
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

3.  Follow the instruction inside the module './InstagramScraperAPIVersion' to crawl the basic data and media for the given user. 

------








License
-------
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
