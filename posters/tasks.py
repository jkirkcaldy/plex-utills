from .models import Plex, film, episode, season
from .utils import banners, item, process

import re

cutoff = 10

def posters4k(webhooktitle, posterVar):
    errors = []
    size = (2000,3000)
    mediaType = 'film'
    plex = item.getPlex()
    libraries = item.libraries(mediaType)
    config = item.getConfig()
    db = film
    for library in libraries:
        key = [film.key for film in library.search(title=webhooktitle, sort='titleSort:desc', limit=1)]
        n = len(key)
        for x in range(n):
            for f in plex.fetchItems(key[x]):
                print(f.title)
                process.dbUpdate(f, db)
                filepath = item.sanitiseFilepath(f)
                if config.skip_media_info == False:
                    hdr, audio = item.scanFile(f, filepath, db)
                else:
                    hdr = item.getHdr(f, db)
                    audio = item.getAudio(f, db)
                tmpPoster, t = item.tmpPoster(f, mediaType)
                poster = item.poster(f, tmpPoster, size)
                newPoster = item.newPoster(f, poster, mediaType, t, db)
                checked = process.checked(f, db)
                if newPoster == True or checked == False:
                    posterBannerHash = banners.posterBannerHash(poster, size)

                    if ('dovi' in hdr or 'hdr' in hdr):
                        dolbyVisionBanner, hdr10Banner, hdrBanner = banners.hdrBannerCheck(posterBannerHash)
                        print(dolbyVisionBanner)
                        if hdr == 'dovi' and dolbyVisionBanner == False:
                            process.addBanner(f, t, 'dv', poster, size, mediaType, db)
                        if hdr == 'hdr' and hdrBanner == False:
                            process.addBanner(f, t, 'hdr', poster, size, mediaType, db)  
                        if hdr == 'hdr10' and hdr10Banner == False:
                            process.addBanner(f, t, 'hdr10', poster, size, mediaType, db)

                    if ('atmos' in audio or 'dtsx' in audio):
                        atmosBanner, dtsxBanner = banners.audioBannerCheck(posterBannerHash)
                        if audio == 'atmos' and atmosBanner == False:
                            process.addBanner(f, t, 'atmos', poster, size, mediaType, db)
                        if audio == 'dtsx' and dtsxBanner == False:
                            process.addBanner(f, t, 'dtsx', poster, size, mediaType, db)

                    if f.media[0].videoResolution == '4k':
                        wideBanner, mini4kBanner  = banners.resolutionBannerCheck(posterBannerHash)
                        if config.mini4k == True and mini4kBanner == False:
                            process.addBanner(f, t, 'mini_4k', poster, size, mediaType, db)
                        elif config.mini4k == False and wideBanner == False:
                            process.addBanner(f, t, 'banner_4k', poster, size, mediaType, db)
