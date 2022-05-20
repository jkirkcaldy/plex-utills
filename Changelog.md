# Changelog
## Version 21.12

#### Changes
* plex-Utills now no longer needs write access to your media. 
    * The scripts now only need access to your media for the media info scan. If you disable this in the config then no access is required at all. 
* you can search through all the data plex-utills has stored for your films and TV shows. Clicking on the poster will restore that poster. Useful if a banner has applied incorrectly or you want to try a new banner. this should force the film to be processed again next time the script is run. 

### Posters 4K:
#### Changes:
* poster backups are now stored in a backup folder next to your config files.
    * Posters are assigned a random string as a filename and this is stored in the database. 
    * restores are now super quick as files are all uploaded locally. 
    * TMDB fall back is still there if requred. 
* information to speed up subsiquent scans is now stored in the database, this means that media doesn't need to be scanned again unless a change in the file is detected. 
* media info scans are only required for audio banners and HDR10+ banners. HDR and Dolby Vision banners can be done with metadata provided by plex.

### TV posters finally got some love
* Now the tv poster script works for adding banners to your episodes. 
* As people will likely have far more TV episodes the scan will only run on 4K and HDR files. But audio posters will still be applied on these files if enabled.


