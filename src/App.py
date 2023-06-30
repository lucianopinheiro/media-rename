from domain.DirectoryHandler import DirectoryHandler
from domain.Image import Image
import os

# CONFIG
srcDirectory = '../temp/src'
dstDirectory = srcDirectory+'/dst'

# APP


class App(object):

    def __init__(self, src, dst):
        script_directory = os.path.dirname(os.path.abspath(__file__))
        self.src = os.path.join(script_directory, src)
        self.dst = os.path.join(script_directory, dst)
        self.files = []

    def rename(self) -> bool:
        files = self.directoryHandler.media_files(self.src)
        for file in files:
            print(file, ' ---> ', file.new_name())

            # find date name
            # if found, move to new name
            # new_path = shutil.move(source, destination)

    def setDirectoryProvider(self, provider):
        self.directoryHandler = provider


app = App(srcDirectory, dstDirectory)
directoryProvider = DirectoryHandler()
app.setDirectoryProvider(directoryProvider)
app.rename()
