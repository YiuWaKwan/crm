import common, MysqlDbPool, traceback
import time, random, json
from django.http import HttpResponse
from lib.FinalLogger import getLogger
from lib.ModuleConfig import ConfAnalysis

# 初始化logger
loggerFIle = 'log/AppHeartState.log'
logger = getLogger(loggerFIle)
# 初始化config
configFile = 'conf/moduleConfig.conf'
confAllItems = ConfAnalysis(logger, configFile)
imgsavepath = confAllItems.getOneOptions('img','imgsavepath')

try:
    mySqlUtil=MysqlDbPool.MysqlDbPool()
except Exception as e:
    logger.info(traceback.format_exc())

def appHeartBeat(request):
    """copyfile app的心跳包，一分钟发一次"""
    wx_main_id = common.getValue(request, "wx_main_id")
    version_code = common.getValue(request, "version_code")
    version_name = common.getValue(request, "version_name")
    if version_code is None or version_code == "":
        version_code = "0"
    if version_name is None or version_name == "":
        version_name = "0"
    if wx_main_id is None or wx_main_id == "":
        return HttpResponse(json.dumps({"msg": "没有wx_main_id"}))

    sql = "select count(1) from wx_status_check where wx_main_id='%s' and program_name='copyfile'" % wx_main_id
    info = mySqlUtil.getData(sql)

    if len(info) > 0 and info[0][0] >=1 :
        sql = "update wx_status_check set last_heartbeat_time=now(), state='1', version_code='%s', version_name='%s' " \
              "where wx_main_id='%s' and program_name='copyfile'" % (version_code, version_name, wx_main_id)
        mySqlUtil.excSql(sql)
    else:
        sql = "insert into wx_status_check(wx_main_id, program_name, last_heartbeat_time, state,program_type, version_code,version_name)" \
              "VALUES('%s','copyfile',now(),'1','1')" % (wx_main_id, version_code, version_name)
        mySqlUtil.excSql(sql)

    return HttpResponse(json.dumps({"msg": "ok"}))