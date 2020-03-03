# plex-utills
## Description
#### 4klibrary
I don't like the idea of having two separate libraries for 4k and 1080p films, the whole process seems like a lot of extra work when it comes to watching movies. I have to rember if I have a 4k version or not. I prefer to have a single library to scroll though, when I want to watch a film I want to just select a film and watch, I don't want to have to remember whether or not I have a 4k version and if someone else selects I want them to select the best quality by default.

Running this script assumes you have a single library with all your films, collections enabled and set to hide items that are in a collection. 

When you run the script it will scan your library, it will find all of the films with both a 4k and non 4k version. (For this to work best, it is better to leave your library to its default behaviour of combining the resolutions into a single item in the library.)

Once it has found films with both 4k and non 4k versions it will split the file into two separate library items, add both items to a collection with the same name. It then tags all of your films with sharing labels. For all the highest resolution version of your film it gives it the tag 'Best' This includes 1080p and 4k versions. For all of your non4k files it also adds the tag 'Transcodable'. With these tags you can restrict your users to only be able to see the trascodable films, so they will never see the 4k versions but will see the rest of your library. Where as the server admin can see everything, all in one single library. 

#### Disney collection
This is a script to find all films in your library with a studio with Disney in the studio's title, e.g. Walt Disney Pictures or Disney animation. It then adds all of these films into a collection named Disney. 

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
`sudo pip install -r requirements.txt`

Edit the config.ini file, change the plex url and the plex token and select your film library. 

Run the script. 
`python3 4klibrary.py`

#### Optional
Set cron job to run the script daily to automatically run the script and organise your library

Profit.

Modified from this script by [u/spazatk](https://www.reddit.com/r/PleX/comments/afs8m9/my_scripted_solution_to_having_a_single_movies/?utm_source=share&utm_medium=web2x)
