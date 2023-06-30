import datetime
import os


class Media:

    def __init__(self, filename) -> None:
        self.type = ''  # video,image
        self.found = False
        self.path = os.path.dirname(filename)
        self.originalName = os.path.basename(filename)
        self.date = datetime.datetime.now()

    def destinName() -> str:
        pass
