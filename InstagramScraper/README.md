
Instagram Scraper
=================

instagram-scraper is a command-line application written in Python that scrapes and downloads an instagram user's photos and videos. Use responsibly.

Requirements 
-----
1. Create virtual environment
```bash
$ virtualenv venv-instascraper
```

2. Activate virtual environment 
```bash
$ source venv/bin/activate
```

3. Execute pip install command
```bash
pip install -r requirements.txt
```

4. Execute setup.py
```bash
python setup.py develop
```

Usage
-----

Example Command(Mostly use this command):
------
If the --maximum option is omitted then it will download all posts of a user/users. But it is usefull to limit the scraping item using --maximum if the script downloading items for long time. Adding another option --latest will download new media since the last download.

```bash
instagram-scraper comma-separated-username --media-types image --comments --maximum 5
```

*By default, downloaded media will be placed in `<current working directory>/<username>`.*


To scrape a hashtag for media:
```bash
$ python -m instagram-scraper.app <hashtag without #> --tag          
```
*It may be useful to specify the `--maximum <#>` argument to limit the total number of items to scrape when scraping by hashtag.*


To scrape a private user's media when you are an approved follower:
```bash
$ python -m instagram-scraper.app <username> -u <your username> -p <your password>
```

To specify multiple users, pass a delimited list of users:
```bash
$ python -m instagram-scraper.app username1,username2,username3           
```

You can also supply a file containing a list of usernames:
```bash
$ python -m instagram-scraper.app -f ig_users.txt           
```

```
# ig_users.txt

username1
username2
username3

# and so on...
```
*The usernames may be separated by newlines, commas, semicolons, or whitespace.*



OPTIONS
-------

```
--help -h           Show help message and exit.

--login-user  -u    Instagram login user.

--login-pass  -p    Instagram login password.

--filename    -f    Path to a file containing a list of users to scrape.

--destination -d    Specify the download destination. By default, media will 
                    be downloaded to <current working directory>/<username>.

--retain-username -n  Creates a username subdirectory when the destination flag is
                      set.

--media-types -t    Specify media types to scrape. Enter as space separated values. 
                    Valid values are image, video, story, or none. Stories require
                    a --login-user and --login-pass to be defined.

--latest            Scrape only new media since the last scrape. Uses the last modified
                    time of the latest media item in the destination directory to compare.

--quiet       -q    Be quiet while scraping.

--maximum     -m    Maximum number of items to scrape.

--media-metadata    Saves the media metadata associated with the user's posts to 
                    <destination>/<username>.json. Can be combined with --media-types none
                    to only fetch the metadata without downloading the media.

--include-location  Includes location metadata when saving media metadata. 
                    Implicitly includes --media-metadata.

--comments          Saves the comment metadata associated with the posts to 
                    <destination>/<username>.json. Implicitly includes --media-metadata.

--tag               Scrapes the specified hashtag for media.

--filter            Scrapes the specified hashtag within a user's media.

--location          Scrapes the specified instagram location-id for media.

--search-location   Search for a location by name. Useful for determining the location-id of 
                    a specific place.

```


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
