import const
import subprocess
from subprocess import call

class SourceViewer(object):

    os_type = None
    srcPath = None

    def __init__(self):
        const.os_type_linux = 1
        const.os_type_osx = 2
        const.os_type_windows = 3

        uname_str = (subprocess.check_output(['uname'])).decode("utf-8")
        
        if "Linux" in uname_str:
            self.os_type = const.os_type_linux
        elif "Darwin" in uname_str:
            self.os_type = const.os_type_osx

    def createIndex(self, pathSrc):
        if None == pathSrc:
            return

        self.srcPath = pathSrc
        if const.os_type_linux == self.os_type:
            call(['ctags','-R',self.srcPath])
            #call(['find','self.srcPath','-name','*.java','|','ctags'])

    def openViewer(self, module, message):
        module_str = module.split(".")
        file_path, search_str = self.findOneMsgInTags(module_str[-1], message.split("(")[0])
        cmd_str = ['mvim',file_path,'-c',"/" + search_str]
        print(cmd_str)
        call(cmd_str)

    def findOneMsgInTags(self, module, message):

        file_path = None
        search_str = None
        byte_stuffing_search_str = None
        file_in = open("tags","r",encoding='utf-8',errors='ignore')
        for line in file_in:
            if message == (line.split())[0]:
                file_path = line.split()[1]
                search_str = line.split("/^")[1].split("$/;")[0]
                #if "class:" + module + "\n" in line or "interface:" + module + "\n" in line:
                #    file_path = line.split()[1]
                #    search_str = line.split("/^")[1].split("$/;")[0]

                byte_stuffing_search_str = search_str.replace('*','\\*')

        return file_path, byte_stuffing_search_str
            
