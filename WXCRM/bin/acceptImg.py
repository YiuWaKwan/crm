#coding:utf-8
from flask import request, Flask
import time
import os

from lib.Logger import FinalLogger
from lib.ModuleConfig import ConfAnalysis

app = Flask(__name__)
# 初始化logger
loggerFIle = '../../log/acceptImg.log'
logger = FinalLogger().getConfLogger(loggerFIle)
configFile =  '../../conf/moduleConfig.conf'
confAllItems = ConfAnalysis(logger, configFile)
imgsavepath = confAllItems.getOneOptions('devInfo','dev')
@app.route("/", methods=['POST'])
def get_frame():
    start_time = time.time()
    upload_file = request.files['file']
    old_file_name = upload_file.filename
    if upload_file:
        file_path = os.path.join('D:/project/pythonProj/WXCRM/WXCRM/static/img/Screenshot/', old_file_name)
        upload_file.save(file_path)
        print ("success")
        print('file saved to %s' % file_path)
        duration = time.time() - start_time
        print('duration:[%.0fms]' % (duration*1000))
        return 'success'
    else:
        return 'failed'


if __name__ == "__main__":
    app.run(str(imgsavepath), port=5000)