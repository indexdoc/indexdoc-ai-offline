import sys
import os

import subprocess

class JSApi:
    def __init__(self, window):
        self.window = window

###--------------session begin--------------------------------
    def getDeviceInfo(self): #获取client机器的设备信息
        from util.DeviceInfoUtil import get_device_info
        return get_device_info()
###--------------session end--------------------------------

###--------------local_kb begin--------------------------------
    def openLocalFile(self, filepath):
        if sys.platform.startswith('darwin'):  # macOS
            subprocess.call(['open', filepath])
        elif os.name == 'nt':  # Windows
            os.startfile(filepath)
        elif os.name == 'posix':  # Linux、其它类 Unix
            subprocess.call(['xdg-open', filepath])
        else:
            raise OSError(f'Unsupported platform: {sys.platform}')

    def addHistory(self, history_id, chat_id, current_id, role_name, message):
        # add_history(history_id, chat_id, current_id, role_name, message)
        return 1

    def loadHistory(self, chat_id):
        # return select_history(chat_id)
        pass

    def chatList(self, id):
        return []

    def hasFinish(self, kb_id):
        return {
            "total": 0,
            "finish": 0,
            "finished": 0 == 0,
        }

##--------------local_kb end--------------------------------

