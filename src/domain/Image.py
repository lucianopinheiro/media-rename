from .MediaInterface import Media
import re
import datetime


class Image(Media):

    def __init__(self, filename):
        super().__init__(filename)
        self.type = 'image'

    def __str__(self) -> str:
        return "image: " + self.original_name

    def find_datetime(self) -> str:
        techniques = [self.find_datetime_from_filename]
        for method in techniques:
            date = method(self.original_name)
            if date:
                self.date = date[0]
                self.extension = date[1]
                self.found = True
                break

    def find_datetime_from_filename(self, filename) -> datetime.datetime:
        """New name based on pattern yyyymmdd_hhMMss.jpg
            - 20211228_100341.jpg

        Returns:
            str: new name
        """

        expression = '(\d{8})_(\d{6})\.(jp[e]?g)$'
        r = re.compile(expression)
        if r.match(filename) is not None:
            found = re.search(expression, filename)
            y = int(found.group(1)[0:4])
            m = int(found.group(1)[4:6])
            d = int(found.group(1)[6:8])
            h = int(found.group(2)[0:2])
            min = int(found.group(2)[2:4])
            s = int(found.group(2)[4:6])
            extension = found.group(3)
            return [datetime.datetime(y, m, d, h, min, s), extension]
