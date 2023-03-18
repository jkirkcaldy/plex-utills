# Changelog
## Version 23.01.31

#### Changes
* plex-Utills now no longer needs write access to your media, docker compose example adds read only tag to /films directory. 
    * The scripts now only need access to your media for the media info scan. If you disable this in the config then no access is required at all. _If you disable media scanning, audio banners will be disabled_ 
* Plex Utills now keeps a database of all your processed films and TV shows. Backups are kept separately to your media files.
* You can now search through your plex libraries inside Plex-utills. If you set your TMDB api key you are able to upload new posters from TMDB which will be processed and bannered immediately before upload. As well as creating a backup for the unbannered version. This works for Films, Shows, Seasons and episodes. Though bannered posters are not supported on Shows. 
* Docker Compose file options for Windows systems are in the example compose file. 
* On the first run after updating, it ask you to migrate, this will seed the database of your bannered films. 
### Posters 4K:
#### Changes:
* Poster backups as well as a bannered poster backup are now stored in a backup folder next to your config files.
    * Posters are saved with the guid of your plex media. 
    * restores are now much quicker as files are restored from your local backups. 
    * TMDB fall back is still there if requred. 
* information to speed up subsiquent scans is now stored in the database, this means that media doesn't need to be scanned again unless a change in the file is detected. 
* media info scans are only required for audio banners and HDR10+ banners. HDR and Dolby Vision banners can be done with metadata provided by plex.

### TV posters finally got some love
* Now the tv poster script works for adding banners to your episodes and seasons. 
* TV posters search is filtered to only include files that are 4K or HDR. Audio banners can still be applied to these files but they will not be applied for files <1080p that are not HDR.
* media info scans are only required for audio banners and HDR10+ banners. HDR and Dolby Vision banners can be done with metadata provided by plex.


