from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from lib.ModuleConfig import ConfAnalysis
import os
import mySqlUtil
import json
import uuid
import socket
import random
import time
import common
from lib.DateEncoder import DateEncoder
import traceback
from lib.FinalLogger import getLogger
# 初始化logger
loggerFIle = 'log/wxInfoViews.log'
logger = getLogger(loggerFIle)
# 初始化config
configFile = 'conf/moduleConfig.conf'
confAllItems = ConfAnalysis(logger, configFile)

devid=confAllItems.getOneOptions('devInfo','dev')


def queryWxInfo(request):
    if request.method == 'GET':
        wxCheckId=request.GET.get('wxCheckId')
        phCheckId = request.GET.get('phCheckId')
        regCheckId = request.GET.get('regCheckId')
        pageShowNum = int(request.GET.get('pageShowNum'))
        ifStartId= request.GET.get('ifStartId')
        if regCheckId == "注册人员":
            regCheckId = ""
        pageIndex = request.GET.get('pageIndex')
        pageNum = int(pageIndex)
        # 获取用户id
        oper_id = request.session['oper_id']
        oper_name = request.session['oper_name']

    pageStart = (pageNum - 1) * pageShowNum
    pageNum = pageShowNum

    sqlConditions = """ where 1=1 """
    if wxCheckId != "":
        sqlConditions += " and wx_id like '%%%s%%'" % wxCheckId
    if phCheckId != "":
        sqlConditions += " and phone_no like '%%%s%%' " % phCheckId
    if regCheckId != "":
        sqlConditions += " and registrar like '%%%s%%' " % regCheckId
    if ifStartId != "":
        sqlConditions += " and if_start = '%s' " % ifStartId
    if_admin_sql="select level from wx_system_operator where oper_id ="+str(oper_id)
    rs=mySqlUtil.getData(if_admin_sql)
    if_admin=rs[0][0]
    if not if_admin or str(if_admin)=='2':
        if_admin='2'
        wxInfoCheckSql = """SELECT A.wx_id,A.wx_name,A.phone_no,A.pword,A.sex,A.zone,A.signature,A.register_time,
                            ifnull(A.head_picture,'\\\\static\\\\img\\\\header_none.png'), A.client_id,A.devId,A.registrar,A.if_start,A.wx_login_id
                                FROM `wx_account_info` A
                                %s 
                                and ( A.wx_id IN (SELECT C.object_id from wx_oper_wx C where C.oper_id = %s and type = 0)
                                or A.wx_login_id IN  (SELECT C.object_id from wx_oper_wx C where C.oper_id = %s and type = 0))
                             and A.wx_status = 1
                             order by A.register_time desc
                                limit %s,%s ;""" % (sqlConditions, oper_id, oper_id, pageStart, pageNum)
    elif str(if_admin)=='1':
        if_admin='1'
        wxInfoCheckSql = """SELECT A.wx_id,A.wx_name,A.phone_no,A.pword,A.sex,A.zone,A.signature,A.register_time,
                            ifnull(A.head_picture,'\\\\static\\\\img\\\\header_none.png'), A.client_id,A.devId,A.registrar,A.if_start,A.wx_login_id,
                            (select ws.name from wx_system_operator ws where ws.oper_id in 
                            (select wx.oper_id from wx_oper_wx wx where wx.object_id=A.wx_id or wx.object_id=A.wx_login_id) and ws.level=2 limit 1) operator
                            FROM `wx_account_info` A
                            %s 
                            and ( A.wx_id IN (SELECT C.object_id from wx_oper_wx C where C.oper_id = %s and type = 0)
                            or A.wx_login_id IN  (SELECT C.object_id from wx_oper_wx C where C.oper_id = %s and type = 0))
                         and A.wx_status = 1
                         order by A.register_time desc
                            limit %s,%s ;""" %(sqlConditions,oper_id,oper_id,pageStart,pageNum)
    # logger.info(wxInfoCheckSql)
    countSql = """select count(1) from `wx_account_info` A
                    %s
                    and A.wx_status = 1
                    and (A.wx_id IN (SELECT C.object_id from wx_oper_wx C where C.oper_id = %s and type = 0)
                    or A.wx_login_id IN  (SELECT C.object_id from wx_oper_wx C where C.oper_id = %s and type = 0))
                    """ %(sqlConditions,oper_id,oper_id)
    accountInfoList = mySqlUtil.getData(wxInfoCheckSql)
    countNum = mySqlUtil.getData(countSql)
    retList = {}
    index=0
    for info in accountInfoList:
        retList[index]={'wx_id': info[0],
             'wx_name': info[1],
             'phone_no': info[2],
             'password': info[3],
             'sex': info[4],
             'zone': info[5],
             'signature': info[6],
             'register_time': str(info[7]),
             'head_picture': info[8],
             'client_id': info[9],
             'devId': info[10],
             'registrar': info[11],
             'if_start': info[12],
             'wxLoginId':info[13],
             'if_admin':if_admin}
        if if_admin=='1':
            retList[index]["operator"]=info[14]

        index = index+1
    pageCount = int((int(countNum[0][0]) / pageShowNum)) + 1
    retList['countNum'] = int(countNum[0][0])
    retList['pageCount'] = pageCount

    return HttpResponse(json.dumps(retList))

def createWxInfo(request):
    try:
        wx_login_id = common.getValue(request,'wx_Modal_input')
        phone_no = common.getValue(request,'phone_no_Modal_input')
        if not phone_no:
            phone_no=""
        password = common.getValue(request,'password_Modal_input')
        oper_id = str(request.session['oper_id'])
        sql = "select wx_login_id,wx_status from wx_account_info where wx_login_id='%s'" %wx_login_id
        wxIdInfo = mySqlUtil.getData(sql)
        retList = {}
        retList['retStatus'] = 1
        authorization_flag=True #是否需要改权限
        if len(wxIdInfo)>0 and wxIdInfo[0][0]:
            wx_status=str(wxIdInfo[0][1])
            if wx_status=='1':
                retList['retStatus'] = 0
                retList['msg'] = '该微信号已经存在'
                authorization_flag=False
            else:#改微信号存在但已经失效
                update_phone_str=",phone_no='%s'" % phone_no
                if not phone_no:
                    update_phone_str=''
                sql="update wx_account_info set pword='%s',wx_status=1%s,last_logout_time=now(),delete_time=null,if_start=0,registrar='%s' where wx_login_id='%s'" %(password,update_phone_str,request.session['oper_id'],wx_login_id)
                logger.info(sql)
                mySqlUtil.excSql(sql)
                retList['retStatus'] = 1
        else:
            uu_id = uuid.uuid1()
            machineId, client_id, dev_id = getEmptyDev()  # 获取空闲模拟器中最多的机器中的一个模拟器id
            if machineId == None or client_id == None or dev_id == None:
                retList['retStatus'] = 0
                retList['msg'] = '系统资源不足，请联系管理员增加资源'
                logger.info(retList['msg'])
                return HttpResponse(json.dumps(retList))
            updateDevUUID(machineId, uu_id)
            createSql = """INSERT INTO `wx_account_info` (uuid, wx_id, phone_no, pword, register_time,
                      registrar,wx_login_id,client_id,devid,last_logout_time) VALUES ('%s','%s','%s','%s',now(),'%s','%s','%s','%s',now()) """ % (
                      uu_id, wx_login_id, phone_no, password,request.session['oper_id'],wx_login_id,client_id,dev_id)
            logger.info(createSql)
            mySqlUtil.excSql(createSql)
        if authorization_flag:
            sql="select level,top_level_id from wx_system_operator where oper_id='"+oper_id+"'"
            rs=mySqlUtil.getData(sql)
            if len(rs)>0:
                level=rs[0][0]
                top_level_id=rs[0][1]
                if level:
                    sql="insert into wx_oper_wx (oper_id,type,object_id,add_time,oper_account_id) " \
                        "values('"+oper_id+"',0,'"+wx_login_id+"',DATE_FORMAT(CURDATE(),'%Y-%m-%d'),'"+oper_id+"')"
                    logger.info(sql)
                    mySqlUtil.excSql(sql)
                    if str(level)=='2' and str(top_level_id)!=str(oper_id):#2代表非管理员且有上级管理员
                        sql = "insert into wx_oper_wx (oper_id,type,object_id,add_time,oper_account_id) " \
                              "values('" +str(top_level_id)+ "',0,'"+wx_login_id+"',DATE_FORMAT(CURDATE(),'%Y-%m-%d'),'" + oper_id + "')"
                        logger.info(sql)
                        mySqlUtil.excSql(sql)
    except (Exception) as e:
        logger.info(traceback.format_exc())
        logger.warn(e)
        retList['retStatus'] = 0
        retList['msg'] = '创建失败'

    return HttpResponse(json.dumps(retList))

def editWxInfo(request):
    wx_Modal_edit = common.getValue(request,'wx_Modal_edit')
    phone_no_Modal_edit = common.getValue(request,'phone_no_Modal_edit')
    password_Modal_edit = common.getValue(request,'password_Modal_edit')
    editSql=""
    if password_Modal_edit:
        if phone_no_Modal_edit:
            editSql = """update wx_account_info A set  A.phone_no = '%s', A.pword = '%s' WHERE A.wx_login_id = '%s'""" %(
                phone_no_Modal_edit,password_Modal_edit,wx_Modal_edit)
        else:
            editSql = """update wx_account_info A set  A.pword = '%s' WHERE A.wx_login_id = '%s'""" % (
                password_Modal_edit, wx_Modal_edit)
    else:
        if phone_no_Modal_edit:
            editSql = """update wx_account_info A set  A.phone_no = '%s' WHERE A.wx_login_id = '%s'""" % (
                phone_no_Modal_edit, wx_Modal_edit)
    if editSql:
        try:
            mySqlUtil.excSql(editSql)
            retStatus = 1
        except (Exception) as e:
            logger.warn(e)
            retStatus = -1
    else:
        retStatus = -1
    retList = {'retStatus':retStatus}
    return HttpResponse(json.dumps(retList))

def delWxInfo(request):
    retList = {}
    oper_name = request.session['oper_name']
    wxLoginId = common.getValue(request,'wxLoginId')
    try:
        uuid_sql = "select uuid,wx_id,wx_name from wx_account_info where wx_status=1 and wx_login_id='" + str(wxLoginId) + "'"
        uuid_rs = mySqlUtil.getData(uuid_sql)
        if len(uuid_rs) > 0:
            uuid_str = uuid_rs[0][0]
            wx_id = str(uuid_rs[0][1])
            wx_name = uuid_rs[0][2]

            if wx_name is not None: #保证登录成功，微信名称刷出来后才保存关系
                taskSeq = round(time.time() * 1000 + random.randint(100, 999))
                sql = "INSERT INTO wx_task_manage(taskSeq,uuid,actionType,createTime,status,priority,operViewName)" \
                      "VALUES(%d,'%s', 28, now(), 1, 5, '%s')" % (taskSeq, uuid_str, oper_name)
                mySqlUtil.excSql(sql)
                run_times=0
                while run_times<15:
                    run_times+=1
                    sql="select status from wx_task_manage where taskSeq=%d" % taskSeq
                    rs=mySqlUtil.getData(sql)
                    if len(rs)>0:
                        status=int(rs[0][0])
                        if status==4:
                            break
                        logger.info("正在关闭（%s）模拟器。。。。" % wx_name)
                    else:
                        break
                    time.sleep(1)
                sql = "update wx_account_info set wx_status=0,delete_time=now() where wx_login_id='" + str(wxLoginId) + "'"
                mySqlUtil.excSql(sql)
            else:#没用过的模拟器释放掉
                sql="update wx_machine_info set uuid=null , status=0 where uuid='%s' " % uuid_str
                logger.info(sql)
                mySqlUtil.excSql(sql)
                sql = "delete from wx_account_info where wx_login_id='" + str(wxLoginId) + "'"
                mySqlUtil.excSql(sql)

            delTaskSql = "delete from wx_task_manage where uuid = '%s' " % uuid_str
            logger.info(delTaskSql)
            mySqlUtil.excSql(delTaskSql)
            # 删除微信号后更新session
            sql="delete from wx_oper_wx where object_id in ('"+wx_id+"','"+wxLoginId+"')"
            mySqlUtil.excSql(sql)
            retStatus = 1
            if wx_id in request.session['oper_main_wx']:
                request.session['oper_main_wx'].remove(wx_id)
            if wxLoginId in request.session['oper_main_wx']:
                request.session['oper_main_wx'].remove(wxLoginId)
        else:
            retStatus=1
    except Exception as e:
        retStatus = -1
        logger.warn(e)
    retList['retStatus'] = retStatus

    return HttpResponse(json.dumps(retList))

def refreshWxInfo(request):
    retList = {}
    oper_name = request.session['oper_name']
    valueInfo = common.getValue(request,'valueInfo')
    valueInfoList = valueInfo.split(',')

    try:
        for wx_login_id in valueInfoList:
            sql="select uuid,wx_id from wx_account_info where wx_login_id='%s'" % wx_login_id
            wxInfo = mySqlUtil.getData(sql)
            if len(wxInfo) > 0:
                taskSeq = round(time.time() * 1000 + random.randint(100, 999))
                sql = "INSERT INTO wx_task_manage(taskSeq,uuid,actionType,createTime,status,priority,operViewName)" \
                      "VALUES(%d,'%s',9,now(),1,5,'%s')" % (taskSeq, wxInfo[0][0], oper_name)
                mySqlUtil.excSql(sql)

                sql = "INSERT INTO wx_friend_refresh(taskSeq,wx_main_id)" \
                      "VALUES(%d,'%s')" % (taskSeq, wxInfo[0][1])
                mySqlUtil.excSql(sql)

        retStatus = 1
    except Exception as e:
        retStatus = -1
        logger.warn(e)
    retList['retStatus'] = retStatus

    return HttpResponse(json.dumps(retList))

def createGetIp(request):
    retList = {}
    loaclIp = socket.gethostbyname(socket.getfqdn(socket.gethostname(  )))
    retList['loaclIp'] = loaclIp

    return HttpResponse(json.dumps(retList))

def getEmptyDev():
    #优先使用本地节点
    sql = "select id,clientId,devId from wx_machine_info where (uuid is null or uuid = '') and if_ready=1 and status=0 and  clientId='"+str(devid)+"' ORDER BY id limit 1 "
    logger.info(sql)
    result = mySqlUtil.getData(sql)
    if len(result) == 0:
        sql = "select id,clientId,devId from wx_machine_info where (uuid is null or uuid = '') and status=0 and if_ready=1 and  clientId=(select clientId from " \
            "(select count(1) as emptyNum,clientId from wx_machine_info where (uuid is null or uuid = '') " \
            " and status=0 and if_ready=1  GROUP BY clientId order by emptyNum desc limit 1) b) ORDER BY id limit 1 "
        result=mySqlUtil.getData(sql)

    if len(result) > 0:
        machineId = result[0][0]
        clientId = result[0][1]
        devId = result[0][2]
    else:
        return (None, None, None)

    return (machineId, clientId, devId)

def updateDevUUID(machineId,uuid):
    sql="update wx_machine_info set uuid='%s' , status=1 where id='%s'" %(uuid, machineId)
    logger.info(sql)
    mySqlUtil.excSql(sql)