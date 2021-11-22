# plex-utills

## MASSIVE UPDATE!
---
The whole app now runs in a webui. This should make things easier for those who are not as comfortable in the commandline or just prefer a ui. 

I have also removed a couple of the config elements, namely, the PLEXPATH and MOUNTEDPATH options. These are now handled directly by the application and Docker. When you pass through you plex media directory, the app will automatically map this and find your plex path to make the config easier. Now as long as the container has write access to the media directory, it should make enabling the backup posters much easier. 

There is an option to automatically migrate your old config files into the new ui for easier migration. 

New HDR banners along with a script to migrate from the old banners to the new ones should you wish to use them. You can stick with the old banners if you would like. 

The new scripts us TheMoviedb for finding posters and metadata, so for maximum compatibility and fewer issues, these work best when using TheMoviedb as your metadata agent. Throughout my testing, it is only sequels that were giving me issues, as the Plex scanner will name your films like: 

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

Migration scripts for moving from the old config files to the new database and for moving from the old HDR banner to the new designs. 


## Features

### 4K/HDR Posters



This script will go through your library and add a 4k banner to your posters. Configurable options include:

-   Selecting full width banners or mini corner banners
-   enabling HDR banners
-   Backup your original posters alongside your media

This can be run on both your films library and your TV shows Library. If enabled on your TV shows, a mini 4K banner will be added to each of your 4K episodes, not the season posters. This is due to the possibility of having Shows/Seasons with mixed resolutions. TV shows will be done at the same time as film posters.


### 3D Posters


Much like the 4K poster script, this will go through your films and add a 3D banner to your films. Currently as Plex has no support for labelling content as 3D this will only work for 3D films kept in a separate library. You can configure the script to have full width banners or the mini corner banners as well as backing up your posters.

Available Banners
-----------------

* * * * *

#### The 4K/3D banners will be combined with the HDR posters if they are enabled.

 
<table class="tg">
  <tr>
    <th class="tg-0pky"><img src="https://raw.githubusercontent.com/jkirkcaldy/plex-utills/f0d354387c1010d55066ae971c8f44874ca11906/app/img/Examples/4k_banner.png" alt="Image" width="200" height="300"></th>
    <th class="tg-0lax"><img src="https://raw.githubusercontent.com/jkirkcaldy/plex-utills/f0d354387c1010d55066ae971c8f44874ca11906/app/img/Examples/mini4k.png" width="200" height="300"></th>
    <th class="tg-0lax"><img src="https://raw.githubusercontent.com/jkirkcaldy/plex-utills/f0d354387c1010d55066ae971c8f44874ca11906/app/img/Examples/3D_banner.png" width="200" height="300"></th>
    <th class="tg-0lax"><img src="https://raw.githubusercontent.com/jkirkcaldy/plex-utills/f0d354387c1010d55066ae971c8f44874ca11906/app/img/Examples/mini3d.png" width="200" height="300"></th>
  </tr>
  <tr>
    <td class="tg-0lax"><img src="https://raw.githubusercontent.com/jkirkcaldy/plex-utills/f0d354387c1010d55066ae971c8f44874ca11906/app/img/Examples/old_hdr.png" width="200" height="300"></td>
    <td class="tg-0lax"><img src="https://raw.githubusercontent.com/jkirkcaldy/plex-utills/f0d354387c1010d55066ae971c8f44874ca11906/app/img/Examples/new_hdr.png" width="200" height="300"></td>
    <td class="tg-0lax"><img src="https://raw.githubusercontent.com/jkirkcaldy/plex-utills/f0d354387c1010d55066ae971c8f44874ca11906/app/img/Examples/new_dolby_vision.png" width="200" height="300"></td>
    <td class="tg-0lax"><img src="https://raw.githubusercontent.com/jkirkcaldy/plex-utills/f0d354387c1010d55066ae971c8f44874ca11906/app/img/Examples/new_hdr10.png" width="200" height="300"></td>
  </tr>
</table>



### Hide 4K

For those of you who don't separate your 4K and non-4K content into separate libraries. This script will go through your films library and add an "Untranscodable" tag to any of your films that only have a single 4K copy of the film available. By adding this tag to your users restrictions, they simply won't see these 4K films giving your hardware a break.

If your hardware is powerful enough, there is the option to create an optimized version so that your users can play this version. This will send your film to be optimized with the Plex optimize feature baked directly into Plex. This means all the hard work is done by your plex server, (useful if you're hosting these scripts on a lower powered device.) Once the transcode has finished, the untranscodable tag will be removed the next time the script runs and your users will be able to see the film.

### Disney Collection



Where this whole project started. A simple script, that will go through your films library and add any film from the Disney Studio into a Disney collection.

### Pixar Collection

As above only with Pixar Films

****

# How to Install

This update has been designed to run in docker only. 

[Click here for installation instructions](https://github.com/jkirkcaldy/plex-utills/wiki)
