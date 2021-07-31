#!/usr/local/bin/python

from configparser import ConfigParser
from pathlib import Path
from plexapi.server import PlexServer


DEFAULT_INI: Path = Path(__file__).parent.joinpath('config.ini')


class config (object):
    def __init__(self, fname: str = DEFAULT_INI):
        self.fname = fname
        conf = ConfigParser()
        conf.read(fname)

        self.POSTER_BU = conf.getboolean("PLEXSERVER", "POSTER_BU")
        self.HDR_BANNER = conf.getboolean("PLEXSERVER", "HDR_BANNER")
        self.do_4k_hdr_posters = conf.getboolean(
            "PLEXSERVER", "4k_hdr_posters")
        self.do_Disney = conf.getboolean("PLEXSERVER", "Disney")
        self.do_Pixar = conf.getboolean("PLEXSERVER", "Pixar")
        self.hide_4k = conf.getboolean("PLEXSERVER", "hide_4k")
        self.mini_4k = conf.getboolean("PLEXSERVER", "mini_4k")
        self.transcode = conf.getboolean("PLEXSERVER", "transcode")

        plexpath = Path(conf.get("PLEXSERVER", "PLEXPATH"))
        mountedpath = conf.get("PLEXSERVER", "MOUNTEDPATH")
        self.LIBRARY_PATH = plexpath.joinpath(
            mountedpath[1:] if mountedpath[0] in ["/", "\\"] else mountedpath)

        self.createFoldersIfMissing = conf.getboolean(
            "APP", "CREATE_FOLDERS_IF_MISSING", fallback=True)

        if self.createFoldersIfMissing:
            self.LIBRARY_PATH.mkdir(parents=True, exist_ok=True)
        elif not plexpath.is_dir():
            raise NotADirectoryError(str(plexpath))
        elif not self.LIBRARY_PATH.is_dir():
            raise NotADirectoryError(str(self.LIBRARY_PATH))

        self.plex = PlexServer(
            conf.get("PLEXSERVER", "PLEX_URL"), conf.get("PLEXSERVER", "TOKEN"))
        self.films = self.plex.library.section(
            conf.get("PLEXSERVER", "FILMSLIBRARY"))

        self.schedule_poster = conf.get("SCHEDULE", "poster_schedule")
        self.schedule_disney = conf.get("SCHEDULE", "disney_schedule")
        self.schedule_pixar = conf.get("SCHEDULE", "pixar_schedule")
        self.schedule_hide_poster = conf.get(
            "SCHEDULE", "hide_poster_schedule")

    def __repr__(self):
        return f"config(\'{self.fname}\')"

    def __str__(self):
        return str(self.__dict__)
