from .MediaInterface import Media
import re


class Video(Media):

    def __init__(self, filename):
        super().__init__(filename)
        self.type = 'video'

    def __str__(self) -> str:
        return "video: " + self.originalName

    def new_name(self) -> str:
        new_name = self.new_name_datetime()
        if new_name:
            return new_name

    def new_name_datetime(self) -> str:
        """New name based on pattern yyyymmdd_hhMMss.jpg
            - 20211228_100341.mp4

        Returns:
            str: new name
        """

        filename = self.originalName

        r = re.compile('\d{8}_\d{6}\.(mp[e]?g|mp4|3gp)')
        if r.match(filename) is not None:
            extension = re.search('\.(mp[e]?g|mp4|3gp)$', filename).group(0)
            return filename[0:4]+'-'+filename[4:6]+'-'+filename[6:8]+'_'+filename[9:11]+'.'+filename[11:13]+'.'+filename[13:15]+extension
