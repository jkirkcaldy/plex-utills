class MetaDataError(Exception):
    def __init__(self, item, message="Metadata is not correct. Plex is using local metadata rather than from your agents"):
        self.item = item
        self.message = message
        super().__init__(item.title+' - '+self.message)