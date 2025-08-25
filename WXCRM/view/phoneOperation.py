import uuid
import traceback
from django.http import HttpResponse
from lib.ModuleConfig import ConfAnalysis
from django_redis import get_redis_connection
import MysqlDbPool,common,json, time, random
from lib.DateEncoder import DateEncoder
from lib.FinalLogger import getLogger
# 初始化logger
loggerFIle = 'log/phoneOperation.log'
logger = getLogger(loggerFIle)
# 初始化config
configFile = 'conf/moduleConfig.conf'
confAllItems = ConfAnalysis(confDir=configFile)
alarm_server = confAllItems.getOneOptions('alarm', 'alarm_server')
redis_con = get_redis_connection("default")

try:
    mySqlUtil=MysqlDbPool.MysqlDbPool()
except Exception as e:
    logger.info(traceback.format_exc())

def flush_friend(oper_name, wx_id):
    # 判断是否有多余的任务
    # 判断app心跳是否正常
    sql = "select uuid from wx_account_info w where wx_id='%s' and if_start='1' and is_first_time='0'" \
          " and not EXISTS (select 1 from wx_task_manage t where t.status in (1,2) and t.actionType=9 " \
          " and t.uuid=w.uuid and (t.startTime is null or t.startTime < date_sub(now(),interval 1 minute)))" \
          " and EXISTS (select 1 from wx_status_check s where s.program_type='1' and s.wx_main_id=w.wx_id and " \
          " s.last_heartbeat_time >= date_sub(now(),interval 3 minute)) " % wx_id
    wxInfoUUID = mySqlUtil.getData(sql)  # 当前用户所能操作的微信主号
    if wxInfoUUID and len(wxInfoUUID) > 0:
        # redis广播任务
        try:
            task_uuid = wxInfoUUID[0][0]
            redis_con.publish("flush_friend", "%s:~:0#=#0" % wx_id)
            # 添加刷新任务
            taskSeq = round(time.time() * 1000 + random.randint(100, 999))
            sql = "INSERT INTO wx_task_manage(taskSeq,uuid,actionType,createTime,status,priority, startTime)" \
                  "VALUES(%d,'%s',9,now(),2,5, now())" % (taskSeq, task_uuid)
            mySqlUtil.excSql(sql)
        except (Exception) as e:
            logger.exception(e)
            #发送告警
            common.alarm(logger, "redis连接不上，刷新好友不成功, 登录账号[%s]" % oper_name, alarm_server)

def phone_oper(request):
    try:
        if(common.getValue(request,'oper') == 'check_oper_name'): #校验用户是否存在
            ret=check_oper_name(request)
            return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))
        elif(common.getValue(request,'oper') == 'banding_wx'): #绑定微信
            ret=banding_wx(request)
            return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))
        elif (common.getValue(request, 'oper') == 'un_banding_wx'):  #解绑微信
            ret = un_banding_wx(request)
            return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))
        elif (common.getValue(request, 'oper') == 'get_version'):  #解绑微信
            ret = get_version(request)
            return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))
    except(Exception) as e:
        logger.error(traceback.format_exc())

def check_oper_name(request):
    ret = {}
    ret["result"] = "0"
    oper_name = common.getValue(request, "oper_name")
    try:
        if "'" in oper_name or ";" in oper_name or len(oper_name) > 32:
            None
        else:
            sql = """select oper_id from wx_system_operator where name='%s'""" % oper_name
            operInfo = mySqlUtil.getData(sql)
            if operInfo and len(operInfo) > 0:
                ret["result"] = "1"
            else:
                ret["result"] = "-2"
    except Exception as e:
        ret["result"] = "-1"
        logger.warn(traceback.format_exc())
    return ret

def banding_wx(request):
    ret = {}
    ret["result"] = "0"
    oper_name = common.getValue(request, "oper_name")
    wx_id = common.getValue(request, "wx_id")
    phone_no = common.getValue(request, "phone_no")
    if oper_name is None or wx_id is None:
        return ret["result"];
    try:
        sql = """select oper_id from wx_system_operator where name='%s'""" % oper_name
        operInfo = mySqlUtil.getData(sql)
        if operInfo and len(operInfo) > 0:
            None
        else:
            ret["result"] = "-2"
            return ret

        # 2.先查询记录是否存在，如果存在一样的记录则更新手机号码，根据wx_id判断
        sql = """select uuid from wx_account_info where wx_id='%s' and wx_status='1'""" % wx_id
        countInfo = mySqlUtil.getData(sql)
        if countInfo and len(countInfo) > 0:
            uuid_str = countInfo[0][0]
            sql = """update wx_account_info set if_start=1, is_first_time='0' where wx_id='%s' and wx_status='1' """ % wx_id
            if phone_no and len(phone_no) == 11:
                sql = """update wx_account_info set phone_no='%s' , if_start=1, is_first_time='0' where wx_id='%s' and wx_status='1' """ % (phone_no, wx_id)
            mySqlUtil.execSql(sql)
            sql = """update wx_machine_info set is_phone=1 where uuid='%s'""" % uuid_str
            mySqlUtil.execSql(sql)
        #3.如果不存在，则新增微信账户和机器信息
        else:
            uuid_str = uuid.uuid1()
            taskSeq = round(time.time() * 1000 + random.randint(100, 999))
            sql = """ insert into wx_account_info(uuid,wx_id,wx_login_id, phone_no,
                      register_time, if_start, wx_status, is_first_time,client_id, devId)
                      values('%s', '%s', '%s', '%s',now(), 1,'1','0','%s','真实手机') """ \
                  % (uuid_str, wx_id, wx_id, wx_id, str(taskSeq))
            mySqlUtil.execSql(sql)
            sql = """ insert into wx_machine_info(uuid,clientId,devport,create_time,status,devname,clientid,devId, is_phone)
                      values('%s', '0.0.0.0', '0000',now(), '1', '真实手机','%s','真实手机', 1) """ % (uuid_str, str(taskSeq))
            mySqlUtil.execSql(sql)
        #权限控制 1.操作员账号是否能找到，2.是否已经有这个微信的权限有就更新，没有就写入
        authorization(mySqlUtil, oper_name, wx_id)
        #刷新好友
        flush_friend(oper_name, wx_id)
        ret["result"] = "1"
    except Exception as e:
        ret["result"] = "-1"
        logger.warn(traceback.format_exc())
    return ret

def authorization(mySqlUtil, oper_name, wx_id):
    """#权限控制 1.操作员账号是否能找到，2.是否已经有这个微信的权限,如果没有就写入"""
    sql = "select oper_id from wx_system_operator where name='%s'" % oper_name
    oper_info = mySqlUtil.getData(sql)
    if oper_info and len(oper_info) > 0:
        oper_id = oper_info[0][0]
        sql = "select object_id from wx_oper_wx where oper_id='%s' and object_id='%s' and type='0'" % (oper_id, wx_id)
        oper_wx_info = mySqlUtil.getData(sql)
        if oper_wx_info and len(oper_wx_info) > 0:
            None#已经有权限
        else:
            sql = "INSERT INTO wx_oper_wx(oper_id,type,object_id,add_time)VALUES('"+str(oper_id)+"','0','"+wx_id+"',date_format(now(),'%Y-%c-%d'))"
            mySqlUtil.execSql(sql)


def un_banding_wx(request):
    ret = {}
    ret["result"] = "1"
    oper_name = common.getValue(request, "oper_name")
    wx_id = common.getValue(request, "wx_id")
    try:
        #微信下线
        sql = """update wx_account_info set if_start=0 where wx_id='%s' and wx_status='1' """ % wx_id
        mySqlUtil.execSql(sql)
        #删除权限
        sql = """delete from wx_oper_wx where object_id='%s' and oper_id=(select oper_id from wx_system_operator where name='%s')""" % (wx_id, oper_name)
        mySqlUtil.execSql(sql)
        ret["result"] = "1"
    except Exception as e:
        ret["result"] = "-1"
        logger.warn(traceback.format_exc())
    return ret

def get_version(request):
    ret = {"versionCode": 0, "versionName": "", "downloadUrl": "", "appName": ""}
    try:
        #微信下线
        sql = """select version_code,version_name,download_url,app_name from wx_app_version where state='1' """
        versionInfo = mySqlUtil.getData(sql)
        if versionInfo and len(versionInfo) > 0:
            ret["versionCode"] = versionInfo[0][0]
            ret["versionName"] = versionInfo[0][1]
            ret["downloadUrl"] = versionInfo[0][2]
            ret["appName"] = versionInfo[0][3]
    except Exception as e:
        logger.warn(traceback.format_exc())
    return ret