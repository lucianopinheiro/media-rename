import datetime
import os


class Media:

    def __init__(self, filename) -> None:
        self.type = ''  # video,image
        self.date = None
        self.extension = ''
        self.found = False
        self.path = os.path.dirname(filename)
        self.original_name = os.path.basename(filename)

    def find_datetime():
        """Abstract method"""
        pass

    def new_name(self) -> str:
        if not self.found:
            self.find_datetime()

        if self.found:
            return datetime.datetime.strftime(self.date, "%Y-%m-%d_%H.%M.%S."+self.extension)
