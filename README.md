# plex-utills

## MASSIVE UPDATE!
The whole app now runs in a webui. This should make things easier for those who are not as comfortable in the commandline or just prefer a ui. 

I have also removed a couple of the config elements, namely, the PLEXPATH and MOUNTEDPATH options. These are now handled directly by the application and Docker. When you pass through you plex media directory, the app will automatically map this and find your plex path to make the config easier. Now as long as the container has write access to the media directory, it should make enabling the backup posters much easier. 

There is an option to automatically migrate your old config files into the new ui for easier migration. 

New HDR banners along with a script to migrate from the old banners to the new ones should you wish to use them. You can stick with the old banners if you would like. 

The new scripts us TheMoviedb for finidng posters and metadata, so for maximum compatability and fewer issues, these work best when using TheMoviedb as your metadata agent. Trhoughout my testing, it is only sequals that were giving me issues, as the Plex scanner will name your films like: 

Boss Baby 2: Family Business

Whereas on TheMoviedb it is named:

Boss Baby: Family Business 

This means that the search for the film can fail in the script. 

### New Features:
GUI for managing the application in a browser

Add 4k mini banners to your 4K TV episodes. 

New HDR banner design
Dolby Vision HDR Banner
HDR10 Banner


## Description
### Automatically add 4k/HDR Banner



This will go through your library and automatically add a 4k banner at the top of your posters. It will also add a HDR logo so you can easily see which of your files are HDR at a glance. This can be disabled in the config file.

The script will download the poster that you have set for your media and add the banners meaning you can still have curated posters. It will also make a backup of your posters next to the media files so the posters can be restored easily.


 
#### Optional
Now there is the option to use a minified 4k logo if you don't want to have the full width banner on your posters. Set mini-4k to true in the config file. 

<table><tr><td><img src='https://github.com/jkirkcaldy/plex-utills/blob/master/img/4k-example.png?raw=true'></td><td><img src='https://github.com/jkirkcaldy/plex-utills/blob/master/img/mini-4k-example.png?raw=true'></td></tr></table>


### Hide-4k Files
The plex streaming brain has come on a long way and I believe it's no longer necessary to separate your 4k files into a separate library. 

There is still the risk, when keeping all your media in a single library, of having a film where the only copy is 4k. In this case running the hide-4k script will add an 'Untranscodable' tag to these items.

If you add a lower resolution to your library it will remove the tag. 

You will need to set the restrictions in your users profile to exclude the 'Untranscodable' label.

Run this script on a regular basis to keep on top of your library. 

#### Optional
Set transcode to True in the config. This will send your 4k only files to be optimised through plex. The setting for this is 1080p 10mbps. This is not reccomended on low powered hardware. 


### Disney/Pixar collection
This is a script to find all films in your library with a studio having Disney in the studio's title, e.g. Walt Disney Pictures or Disney animation. It then adds all of these films into a collection named Disney. 

It then does the same for Pixar

# Docker install
I have created a docker container for ease of use, epecially for people who aren't comfortable with Python. 

To run the container enter the following:

`docker run -d --name=Plex-utills -v </your/plex/media/folder>:/films -v /<your config directory>:/config jkirkcaldy/plex-utills`

Or you can use docker-compose. An example file is located in the repository.

All configuration is done in the config file. 

# Manual Install
### Requirements
Python3
python3-pip

`sudo apt install python3 python3-pip`

### Instructions
Clone to your machine
`sudo git clone https://github.com/jkirkcaldy/plex-utills.git`

Cd into the folder
`cd plex-utills`

install the requirements 
`sudo pip3 install -r requirements.txt`

Edit the config.ini file, change the plex url and the plex token and select your film library. 

Run the script. 
`python3 4klibrary.py`

#### Optional
Set cron job to run the script daily to automatically run the script and organise your library
