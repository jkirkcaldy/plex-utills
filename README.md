# plex-utills
## You will likely need to re-create or update your config file after updating as there are breaking changes. 
### Changes
Setting whether scripts should run or selecting options has now moved to a different config block. 

New 3D poster creation. This is done by library only at the moment. So all films in your selected 3D library will have banners added. 

4K_hdr_poster script allows for changning poster art, it will recreate the backup as long as it doesn't detect a 4k banner. 

restore poster script will restore all posters from backup not just 4k HDR posters. 

## Description
### Automatically add 4k/HDR Banner

![4k Poster Art](https://github.com/jkirkcaldy/plex-utills/blob/master/img/library_update_sm.gif?raw=true)

This will go through your library and automatically add a 4k banner at the top of your posters. It will also add a HDR logo so you can easily see which of your files are HDR at a glance. This can be disabled in the config file.

The script will download the poster that you have set for your media and add the banners meaning you can still have curated posters. It will also make a backup of your posters next to the media files so the posters can be restored easily.

In order to use this script you will need your plex media volumes mounted. 

Change this in the config.ini file and add the location of the local directory where your plex media is located. You will need read/write access to this directory. 

If your paths are the same or you are running the script on the same machine as your plex server make sure that both entries in the config file match otherwise you will get an error. 
 
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
Set transcode to True in the config file. This will send your 4k only files to be optimised through plex. The setting for this is 1080p 10mbps. This is not reccomended on low powered hardware. 


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

