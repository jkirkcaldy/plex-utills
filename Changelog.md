# Changelog
## Version 21.12

### Collections:
#### Added:
* Autocollection for Marvel Cinematic Universe
* Popular, Top Rated and Recommended collections
    * Requires TheMovieDB api key for this to work.
    * Popular is based on popular movies on TheMovieDb
    * Top Rated is based on the top rated on TheMovieDb
    * Recommended requires Tautulli to work
        * Takes the most popular movie as seen on the Tautulli home page and finds the recommended movies from TheMovieDB
* Config options added to enable/disable each collection

#### Changes:
* Changed the logic behind the colleciton creation. Collections are now Smart collections so the script doesn't need to be re-run for Films to be added. 
    * Smart collection creation is almost instant
    * Existing Disney/Pixar collections will be converted into Smart collections.
    * If you have a Collection called 'Marvel Cinematic Universe' this will be converted into a smart collection
    * Option to use a default poster for Disney, Pixar and Marvel Cinematic Universe. 
    * Exisiting artwork for these collections will be transfered to new smart collections unless default collection artwork is enabled in the config. 
* Collections are handled as a single script. Individual scripts can be enabled/disabled in the config page. 

### Posters 4K:
#### Added:
* Dolby Atmos and DTS:X banners for your films.

#### Changes:
* The script now saves the temp posters to RAM rather than to disk. This should help with corrupted posters.
* Posters are uploaded once rather than after addiong each individual banner. (4k/HDR banners are handled separately from Audio banners as audio banners are applied to all your films, not just 4k or HDR versions.)
* Dolby vision detection has been re-worked for updates to Media Info so should work porperly now. 
* Truncated images are logged
* Temp posters are created with the film title to avoid uploading the incorrect posters to other films. 


### Misc Changes:
#### Front end
* Moved Help page so it is on the side menu
* Config page is now split into server config and options. New options added. 
* Javascript for viewing the logs pages changed, as well with slight tweaks to CSS. 

#### Backend
* Reworked how the web pages are rendered
* New config options will be added to the database
    * All new options default to empty or false.
* Dev page for debugging HDR detection and audio codec detection. 
* TZ variable removed from Unraid template. Should be configured automatically.

#### Misc
* Some typos fixed.
