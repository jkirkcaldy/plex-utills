# plex-utills
## Description
### Automatically add 4k/HDR Banner
![4k Poster Art](https://github.com/jkirkcaldy/plex-utills/blob/master/img/library_update_sm.gif?raw=true)
![4k Poster Art-cmdline](https://github.com/jkirkcaldy/plex-utills/blob/master/img/library_update_console.gif?raw=true)

This will go through your library and automatically add a 4k banner at the top of your posters. It will also add a HDR logo so you can easily see which of your files are HDR at a glance. 

The script will download the poster that you have set for your media and add the banners meaning you can still have curated posters. It will also make a backup of your posters next to the media files so the posters can be restored easily (coming soon)

In order to use this script you will need your plex media volumes mounted. If you are not running this on the same computer as your plex server or you are using docker you will likely need to change the root path of your media. 

Find the file path that Plex uses to find the media, if you use docker this is likely 
`/media/<your directory layout>`
You can use the setup_helper.py script to show you the base path that Plex is using. 

Change this in the config.ini file and add the location of the local directory where your plex media is located. You will need read/write access to this directory. 

If your paths are the same or you are running the script on the same machine as your plex server make sure that both entries in the config file match otherwise you will get an error. 
 

### Hide-4k Files
The plex streaming brain has come on a long way and I believe it's no longer necessary to separate your 4k files into a separate library. 

There is still the risk, when keeping all your media in a single library, of having a film where the only copy is 4k. In this case running the hide-4k script will add an 'Untranscodable' tag to these items.

If you add a lower resolution to your library it will remove the tag. 

You will need to set the restrictions in your users profile to exclude the 'Untranscodable' label.

Run this script on a regular basis to keep on top of your library. 


#### 4klibrary
I don't like the idea of having two separate libraries for 4k and 1080p films, the whole process seems like a lot of extra work when it comes to watching movies. I have to rember if I have a 4k version or not. I prefer to have a single library to scroll though, when I want to watch a film I want to just select a film and watch, I don't want to have to remember whether or not I have a 4k version and if someone else selects I want them to select the best quality by default.

Running this script assumes you have a single library with all your films, collections enabled and set to hide items that are in a collection. 

When you run the script it will scan your library, it will find all of the films with both a 4k and non 4k version. (For this to work best, it is better to leave your library to its default behaviour of combining the resolutions into a single item in the library.)

Once it has found films with both 4k and non 4k versions it will split the file into two separate library items, add both items to a collection with the same name. It then tags all of your films with sharing labels. For all the highest resolution version of your film it gives it the tag 'Best' This includes 1080p and 4k versions. For all of your non4k files it also adds the tag 'Transcodable'. With these tags you can restrict your users to only be able to see the trascodable films, so they will never see the 4k versions but will see the rest of your library. Where as the server admin can see everything, all in one single library. 

#### Disney/Pixar collection
This is a script to find all films in your library with a studio having Disney in the studio's title, e.g. Walt Disney Pictures or Disney animation. It then adds all of these films into a collection named Disney. 

It then does the same for Pixar

# Install
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

Profit.

