import json
import os
import random
import time

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import common
import mySqlUtil
from lib.DateEncoder import DateEncoder
from lib.FinalLogger import getLogger
from lib.ModuleConfig import ConfAnalysis

# 初始化logger
loggerFIle = 'log/loginWxViews.log'
logger = getLogger(loggerFIle)
# 初始化config
configFile = 'conf/moduleConfig.conf'
confAllItems = ConfAnalysis(logger, configFile)

imgsavepath = confAllItems.getOneOptions('img', 'imgsavepath')
checkImgPath = '\\static\\tmpFile\\img\\'

def loginWx(request):
    return render(request, "loginWx.html")


@csrf_exempt
def loginData(request):
    ret = {}
    try:
        if request.method == 'GET':
            type = request.GET.get('type')
        else:
            type = request.POST.get('type')
        if (type == 'writeCoord'):
            ret = writeCoord(request)
        if (type == 'loginTask'):
            ret = loginTask(request)
        if (type == 'getLoginInfo'):
            ret = getLoginInfo(request)
        if (type == 'logoutTask'):
            ret = logoutTask(request)
            # if (type == 'getWxFrinedsByItChat'):
            #     ret = getWxFrinedsByItChat(request)
    except(Exception) as e:
        logger.error(e)
    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))


def loginTask(request):
    ret = {}
    try:
        oper_name = request.session['oper_name']
        wxLoginId = request.POST.get('wxLoginId')
        sql = "select if_start from wx_account_info where wx_login_id='%s'" % wxLoginId
        ifStart = mySqlUtil.getData(sql)[0][0]
        sql = """select a.taskSeq from wx_task_manage a left join wx_login_task b on a.taskSeq=b.taskSeq
where uuid=(select uuid from wx_account_info where wx_login_id='%s') and a.actionType='19' and (a.status='1' or a.status='2') 
and b.type='1' and TIMESTAMPDIFF(MINUTE,a.startTime,CURRENT_TIMESTAMP)<=6""" % wxLoginId
        taskSeqResult = mySqlUtil.getData(sql)
        taskSeq = ""
        if taskSeqResult and taskSeqResult[0][0]:
            taskSeq = taskSeqResult[0][0]
        if ifStart == 1: 
            ret['ifStart'] = 1
        elif taskSeq:
            ret['ifTask'] = 1
            ret['taskSeq'] = taskSeq
        else:
            taskSeq = round(time.time() * 1000 + random.randint(100, 999))
            sql = "insert into wx_task_manage(taskSeq,uuid,actionType,createTime,priority,status,operViewName)values('%s',(select uuid from wx_account_info where wx_login_id='%s'),%d,now(),0,1,'%s')" % (
                taskSeq, wxLoginId, 19,oper_name)
            logger.info(sql)
            mySqlUtil.excSql(sql)
            sql = "insert into wx_login_task(taskSeq,wx_id,type)VALUES (%d,'%s','1') " % (taskSeq, wxLoginId)
            mySqlUtil.excSql(sql)
            ret['taskSeq'] = taskSeq
        ret['result'] = 1
    except(Exception) as e:
        logger.exception(e)
        ret['result'] = 0
    return ret


def getLoginInfo(request):
    ret = {}
    try:
        taskSeq = request.POST.get('taskSeq')
        sql = "select a.wx_id,a.x_value,a.state,a.picture,a.picture_name,b.status,a.type,a.remark,c.is_first_time,c.wx_id from wx_login_task  a " \
              " left join wx_task_manage b on a.taskSeq=b.taskSeq left join wx_account_info c on a.wx_id=c.wx_login_id  " \
              " where a.taskSeq='%s'" % taskSeq
        loginInfo = mySqlUtil.getData(sql)
        for imgitem in loginInfo:
            img = imgitem[3]
            imgname = imgitem[4]
            ret["picture"] = imgname
            ret['xValueDB'] = imgitem[1]
            ret['state'] = imgitem[2]  # 登录状态
            ret['taskStatus'] = imgitem[5]  # 任务状态
            ret['type'] = imgitem[6]  # 任务类型
            ret['remark'] = imgitem[7]  # 任务备注
            ret['isFirstTime']=imgitem[8]
            ret['wx_id']=imgitem[9]
        if str(ret['state'])=='10':
            logger.info("添加session")
            request.session['oper_main_wx'].append(ret['wx_id'])
        ret['result'] = 1
    except(Exception) as e:
        logger.error(e)
        ret['result'] = 0
    return ret


def writeCoord(request):
    wxId = 'chenchen9662'  # request.POST.get('wxId')
    xValue = request.POST.get('xValue')
    taskSeq = request.POST.get('taskSeq')
    ret = {}
    try:
        # 更新好友信息
        sql = "update wx_login_task set x_value='%s',state='%s'where taskSeq='%s'" % (xValue, '0', taskSeq)
        mySqlUtil.excSql(sql);
        ret['result'] = 1

    except(Exception) as e:
        logger.error(e)
        ret['result'] = 0
    return ret


def logoutTask(request):
    ret = {}
    try:
        oper_name = request.session['oper_name']
        wxLoginId = request.POST.get('wxLoginId')
        sql = "select if_start from wx_account_info where wx_login_id='%s'" % wxLoginId
        logger.info(sql)
        ifStart = mySqlUtil.getData(sql)[0][0]
        if ifStart == 0:
            ret['ifStart'] = 0
        else:
            taskSeq = round(time.time() * 1000 + random.randint(100, 999))
            sql = " insert into wx_task_manage(taskSeq,uuid,actionType,createTime,priority,status,operViewName)values('%s',(select uuid from wx_account_info where wx_login_id='%s'),%d,now(),0,1,'%s')" % (
                taskSeq, wxLoginId, 20, oper_name)
            logger.info(sql)
            mySqlUtil.excSql(sql)
            sql = "insert into wx_login_task(taskSeq,wx_id,type)VALUES (%d,'%s','0') " % (taskSeq, wxLoginId)
            logger.info(sql)
            mySqlUtil.excSql(sql)
            # updateStatusSql = "update  wx_account_info set if_start=0 where wx_login_id='%s'" % wxLoginId
            # logger.info(updateStatusSql)
            # mySqlUtil.excSql(updateStatusSql)
            ret['taskSeq'] = taskSeq
        ret['result'] = 1
    except(Exception) as e:
        logger.exception(e)
        ret['result'] = 0
    return ret

@csrf_exempt
def accept_img(request):
    start_time = time.time()
    myFile = request.FILES.get("file", None)
    file_path = request.POST.get("file_path")
    if not myFile:
        return HttpResponse("no files for upload!")
    BASEDIR = os.getcwd()
    file_path_final = BASEDIR + '/WXCRM/static/img/' + file_path + '/'
    if not os.path.exists(file_path_final):
        os.makedirs(file_path_final)
    destination = open(os.path.join(file_path_final, myFile.name), 'wb+')  # 打开特定的文件进行二进制的写操作
    for chunk in myFile.chunks():  # 分块写入文件
        destination.write(chunk)
    destination.close()
    return HttpResponse("upload success!")


def Register(request):
    sql = """select name,value from wx_dictionary where type = 'organization'"""
    organizationInfo = mySqlUtil.getData(sql)
    organizationList = []
    if organizationInfo and len(organizationInfo) > 0:
        for item in organizationInfo:
            organization = {}
            organization['name'] = item[0]
            organization['value'] = item[1]
            organizationList.append(organization)
    return render(request, "register.html", {"organizationList": organizationList})


@csrf_exempt
def reg_submit(request):
    oper = common.getValue(request, "oper")
    ret = {}
    if oper == "regist":
        ret = submit(request)
    elif oper == "checkusername":
        ret = checkUserName(request)
    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))


def checkUserName(request):
    ret = {}
    username = common.getValue(request, "username")
    try:
        sql = "select count(1) from wx_system_operator where name= '%s' " % username
        usernameList = mySqlUtil.getData(sql)
        usernameCount = 0;
        if usernameList and usernameList[0]:
            usernameCount = usernameList[0][0]
        if usernameCount == 0:
            ret['result'] = "<img src='/static/img/icon_correct_nor.png'>"
        else:
            ret['result'] = "用户名已存在"
    except(Exception) as e:
        logger.error(e)
        ret['result'] = "校验失败"
    return ret


def submit(request):
    username = common.getValue(request, 'username')
    sex = common.getValue(request, 'sex')
    password = common.getValue(request, 'password')
    email = common.getValue(request, 'email')
    phone = common.getValue(request, 'phone')
    viewname = common.getValue(request, 'viewname')

    ret = {}
    try:
        # 更新好友信息
        sql = "insert into wx_system_operator (name,create_time,pwd,sex,email,state,level,organization,phone,viewName) value ('%s',CURDATE(),'%s','%s','%s','0','1','','%s','%s')" \
              % (username, password, sex, email, phone,viewname)
        mySqlUtil.excSql(sql)
        operIdGetSql = """SELECT oper_id from wx_system_operator where name = '%s'""" %(username)
        operId = mySqlUtil.getData(operIdGetSql)[0][0]
        menuList = [1,3,4,5,6,7,10,17,19,20,21,22,23,25,26]
        insertCon = ""
        for muneId in menuList:
            insertCon += "('%s','%s',curdate(),'999'),"%(operId,muneId)
        menuInsertSql = """INSERT INTO `wx_oper_menu` (
                        `oper_id`,
                        `menu_id`,
                        `add_time`,
                        `oper_account_id`
                    )
                    VALUES %s"""%(insertCon[:-1])
        mySqlUtil.excSql(menuInsertSql)
        ret['result'] = 1
    except(Exception) as e:
        logger.error(e)
        ret['result'] = 0
    return ret


@csrf_exempt
def login_log(request):
    try:
        if request.method == 'GET':
            return render(request, 'loginLog.html')
        else:
            if request.POST.get("pageSize") == None:
                pageSize = 10
            else:
                pageSize = request.POST.get("pageSize")
            pageNumber = request.POST.get("pageIndex")
            pageStart = (int(pageNumber) - 1) * int(pageSize)
            clause_sql = "where 1=1"
            oper_id = request.session['oper_id']
            sql = "select oper_id,top_level_id from wx_system_operator where oper_id = '" + str(oper_id) + "' "
            oper_list = mySqlUtil.getData(sql)
            if oper_list[0][0] == oper_list[0][1]:
                sql = "select ta.ip,ta.oper_id,tb.name,ta.login_time,ta.logout_time from wx_oper_logtime ta," \
                      "wx_system_operator tb " + clause_sql + " and ta.oper_id = tb.oper_id order by login_time desc " \
                                                              "limit " + str(pageSize) + " offset " + str(
                    pageStart) + " "
            else:
                sql = "select ta.ip,ta.oper_id,tb.name,ta.login_time,ta.logout_time from wx_oper_logtime ta," \
                      "wx_system_operator tb " + clause_sql + " and ta.oper_id = tb.oper_id and ta.oper_id = '" + str(
                    oper_id) \
                      + "'order by login_time desc limit " + str(pageSize) + " offset " + str(pageStart) + " "
            log_list = mySqlUtil.getData(sql)
            index = 0
            result_list = {}
            wx_id_list = ""
            wx_name_list = ""
            for log_info in log_list:
                oper_id = log_info[1]
                sql = "select wx_id,wx_name from wx_account_info where if_start = 1 and groupId in (select object_id " \
                      "from wx_oper_wx where oper_id = '" + str(oper_id) + "') order by groupID"
                weixin_list = mySqlUtil.getData(sql)
                weixin_len = len(weixin_list)
                for weixin_item in weixin_list:
                    wx_id = weixin_item[0]
                    wx_name = weixin_item[1]
                    wx_id_list += wx_id + " | "
                    wx_name_list += wx_name + " | "
                result_list[index] = {'IP': log_info[0],
                                      'oper_name': log_info[2],
                                      'login_time': str(log_info[3]),
                                      'logout_time': str(log_info[4]),
                                      'weixin': wx_name_list,
                                      'weixin_count': weixin_len
                                      }
                index = index + 1
                wx_id_list = ""
                wx_name_list = ""
            sql_count = "select count(*) from wx_oper_logtime  " + clause_sql + ""
            client_count = mySqlUtil.query_data(sql_count)
            result_list["pageCount"] = client_count[0]["count(*)"]
            return HttpResponse(json.dumps(result_list))
    except(Exception) as e:
        logger.warn(e)
    finally:
        pass


def accountCreate(request):
    ret = {}
    ret['result'] = 1
    try:
        operId = request.session['oper_id']
        username = request.GET.get("username")
        sex = request.GET.get("sex")
        password = request.GET.get("password")
        email = request.GET.get("email")
        phone = request.GET.get("phone")
        viewname = request.GET.get("viewname")
        insertSql = """INSERT INTO `wx_system_operator` (
                    `viewName`,
                    `name`,
                    `pwd`,
                    `create_time`,
                    `sex`,
                    `phone`,
                    `email`,
                    `state`,
                    `organization`,
                    `level`,
                    `top_level_id`
                )
                VALUES
                    (
                        \'%s\',
                        \'%s\',
                        \'%s\',
                        curdate(),
                        \'%s\',
                        \'%s\',
                        \'%s\',
                        '1',
                        NULL,
                        '2',
                        \'%s\'
                    )"""%(viewname, username, password, sex, phone, email, operId)
        print(insertSql)
        mySqlUtil.excSql(insertSql)
        ret['result'] = 1
    except(Exception) as e:
        logger.error(e)
    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))
@csrf_exempt
def logoutTaskCheck(request):
    ret = {'taskList':[]}
    try:
        wx_id = request.POST.get('wxLoginId')
        sql = "select distinct name from wx_dictionary where type='task_type' and value in " \
              "(select actionType from wx_task_manage where uuid in " \
              "(select uuid from wx_account_info where wx_login_id='%s') and actionType in (22,23,24,30,32) and ((TIMESTAMPDIFF(SECOND, now(),cronTime)>0 and status=1) or status=2))" % wx_id
        logger.info(sql)
        rs = mySqlUtil.getData(sql)
        if len(rs)>0:
            for result in rs:
                ret['taskList'].append(result[0])
            ret['flag'] = 1
        else:
            ret['flag'] = 0
    except(Exception) as e:
        logger.error(e)
        ret['result'] = -1
    return HttpResponse(json.dumps(ret, ensure_ascii=False))
@csrf_exempt
def stopTaskBySeq(request):
    ret = {}
    try:
        task_seq = request.POST.get('taskSeq')
        sql = "update wx_task_manage set ifKill=1 where taskSeq="+str(task_seq)
        logger.info(sql)
        mySqlUtil.excSql(sql)
        ret['result'] = 1
    except(Exception) as e:
        logger.error(e)
        ret['result'] = -1
    return HttpResponse(json.dumps(ret, ensure_ascii=False))