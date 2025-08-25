import common
import datetime
import json
import random
import time
import traceback

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import mySqlUtil
from lib.DateEncoder import DateEncoder
from lib.FinalLogger import getLogger
from lib.ModuleConfig import ConfAnalysis

# 初始化logger
loggerFIle = 'log/groupViews.log'
logger = getLogger(loggerFIle)
# 初始化config
configFile = 'conf/moduleConfig.conf'
confAllItems = ConfAnalysis(logger, configFile)


def group(request):
    return render(request, "group.html")

@csrf_exempt
def groupInfo(request):
    ret = {}
    try:
        group_name = request.POST.get("group_name")
        wx_id = request.POST.get("wx_id")
        pageSize = request.POST.get("pageSize")
        pageIndex = request.POST.get("pageIndex")
        mainWxStr = "','".join(request.session['oper_main_wx'])

        sql = """ SELECT i.group_id, i.group_name, g.wx_id, (select wx_name from wx_account_info where wx_id=g.wx_id AND wx_status=1), i.group_wx_name, i.description, i.notice,
			(SELECT count(1) FROM wx_group_member m WHERE m.group_id = i.group_id ),'1' status,
			(SELECT count(1) from wx_schedule_task A, wx_system_operator B where A.creatorId = B.oper_id and A.groupId = i.group_Id and A.wxId=g.wx_id),
			i.wx_id qunzhu, (select max(view_name) from wx_group_member m where m.wx_id=i.wx_id and m.group_id=i.group_id) qunzhuname
          FROM wx_group_info i, (select group_id, wx_id, view_name from wx_group_member  where wx_id in ('%s')) g
          WHERE g.group_id = i.group_id and i.STATUS != 0 AND i.group_name != ''
          and exists(select 1 from wx_friend_rela where wx_id=i.group_id and state='1' and wx_main_id in ('%s')) """ % (mainWxStr, mainWxStr)

        if group_name != "" and group_name is not None:
            sql = sql + " and i.group_name like '%" + group_name + "%'"
        if wx_id != "" and wx_id is not None:
            sql = sql + " and g.wx_id = '" + wx_id + "'"
        sql = sql + " order by i.create_date desc "
        #logger.info(sql)
        ret = mySqlUtil.getDataByPage(sql, pageIndex, pageSize)
    except(Exception) as e:
        logger.error(e)
    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))


@csrf_exempt
def getWxId(request):
    mainWxStr = "','".join(request.session['oper_main_wx'])
    sql = "select wx_id,wx_name,head_picture,wx_login_id from wx_account_info a  where a.wx_id in ('%s') or a.wx_login_id in ('%s')" % (mainWxStr, mainWxStr)
    wx_info_list = mySqlUtil.getData(sql)
    wx_list = []
    for wx_info in wx_info_list:
        wx_list.append( {"wx_id": wx_info[0], "wx_name": wx_info[1], "head_picture": wx_info[2], "wx_login_id": wx_info[3]})
    return HttpResponse(json.dumps({"data": wx_list}))


@csrf_exempt
def getWxFriend(request):
    wx_id = request.GET.get("wx_id")
    wx_name = request.GET.get("wx_name")
    sql = "select a.wx_id,r.remark,a.head_picture from wx_friend_list a, wx_friend_rela r " \
          " where r.wx_id=a.wx_id and r.wx_main_id='%s'" % wx_id
    if wx_name != "" and wx_name is not None:
        sql = sql + " and a.wx_name like '%" + wx_name + "%'"
    wx_info_list = mySqlUtil.getData(sql)
    wx_list = []
    for wx_info in wx_info_list:
        wx_list.append({"wx_id": wx_info[0], "wx_name": wx_info[1], "head_picture": wx_info[2]})

    return HttpResponse(json.dumps({"data": wx_list}))


def getMember(request):
    group_id = request.GET.get("group_id")
    wx_main_id = common.getValue(request, 'wx_main_id')
    sql = """select m.wx_id,m.view_name,ifnull((select l.head_picture from wx_friend_list l where l.wx_id=m.wx_id),
          (select a.head_picture from wx_account_info a where a.wx_id=m.wx_id)) head_picture,
          (select remark from wx_group_member_remark where wx_id=m.wx_id and wx_main_id='%s')
          from wx_group_member m where group_id='%s' """ % (wx_main_id, group_id)
    wx_info_list = mySqlUtil.getData(sql)
    wx_list = []
    for wx_info in wx_info_list:
        #wx_list.append({"wx_id": wx_info[0], "wx_name": wx_info[1], "head_picture": wx_info[2]})
        if wx_info[3] is not None:
            wx_list.append({"wx_id": wx_info[0], "wx_name": wx_info[3], "head_picture": wx_info[2]})
        else:
            wx_list.append({"wx_id":wx_info[0],"wx_name":wx_info[1],"head_picture":wx_info[2]})
    return HttpResponse(json.dumps({"data": wx_list}))


@csrf_exempt
def saveGroupInfo(request):
    flag = request.POST.get("flag")
    group_name = request.POST.get("group_name")
    wx_id = request.POST.get("wx_id")
    groupUsage = request.POST.get("groupUsage")
    groupNotice = request.POST.get("groupNotice")
    friend_list = request.POST.get("friend_list")
    group_wx_name = request.POST.get("group_wx_name")
    group_id = request.POST.get("group_id")
    friend_wx_id = request.POST.get("friend_wx_id")
    oper_name = request.session['oper_name']

    sql = "select a.uuid from wx_account_info a where wx_id='%s'" % wx_id
    group_info = mySqlUtil.getData(sql)
    uuid = group_info[0][0]

    if "insert" == flag:  # 不写记录
        sql = "select group_name from wx_group_info where group_name='%s' and status!=0 and wx_id='%s' " % (
        group_name, wx_id)
        group_info = mySqlUtil.getData(sql)
        if len(group_info) > 0:
            return HttpResponse(json.dumps({"status": "-1", "msg": "群名称重复，请更改群名称！"}))

        friend_list_tmp = ""
        for wx_info in friend_list.split("#"):
            wx_infos = wx_info.split(r",")
            if friend_list_tmp == "":
                friend_list_tmp = wx_infos[1] + "|" + wx_infos[2].strip()
            else:
                friend_list_tmp = friend_list_tmp + "#" + wx_infos[1] + "|" + wx_infos[2]

        # 写任务
        group_id = ""
        createTask(group_id, wx_id, group_wx_name, group_name, groupUsage, groupNotice, friend_list_tmp, 12, uuid,oper_name)
    elif "add_member" == flag:
        friend_list_add = ""
        for wx_info in friend_list.split("#"):
            wx_infos = wx_info.split(r",")

            if friend_list_add == "":
                friend_list_add = wx_infos[1] + "|" + wx_infos[2].strip()
            else:
                friend_list_add = friend_list_add + "#" + wx_infos[1] + "|" + wx_infos[2].strip()

            # sql = "insert into wx_group_member(group_id,wx_id,add_date,add_type,view_name,head_picture) select '%s' group_id, wx_id, now(), '1' add_type, '%s' view_name, head_picture from wx_friend_list where wx_id='%s'" % (
            # group_id, wx_infos[2].strip(), wx_infos[1])
            # mySqlUtil.excSql(sql)

        # 写任务
        if friend_list_add != "":
            createTask(group_id, wx_id, group_wx_name, group_name, groupUsage, groupNotice, friend_list_add, 13, uuid,oper_name)

    elif "del_member" == flag:
        friend_list_del = ""
        for wx_info in friend_list.split("#"):
            wx_infos = wx_info.split(r",")

            if friend_list_del == "":
                friend_list_del = wx_infos[1] + "|" + wx_infos[2].strip()
            else:
                friend_list_del = friend_list_del + "#" + wx_infos[1] + "|" + wx_infos[2].strip()

            # sql = "delete from wx_group_member where group_id='%s' and wx_id='%s' " % (group_id, wx_infos[1])
            # mySqlUtil.excSql(sql)
        # 写任务
        if friend_list_del != "":
            createTask(group_id, wx_id, group_wx_name, group_name, groupUsage, groupNotice, friend_list_del, 14, uuid,oper_name)
    elif "notice" == flag:
        createTask(group_id, wx_id, group_wx_name, group_name, groupUsage, groupNotice, "", 16, uuid,oper_name)
    elif "modify_name" == flag:
        createTask(group_id, wx_id, group_wx_name, group_name, groupUsage, groupNotice, "", 18, uuid,oper_name)
    elif "update_wx_id" == flag:
        createTask(group_id, wx_id, group_wx_name, group_name, groupUsage, groupNotice, friend_wx_id, 17, uuid,oper_name)
    elif "delete" == flag:  # 马上删除
        createTask(group_id, wx_id, group_wx_name, group_name, groupUsage, groupNotice, "", 15, uuid,oper_name)
        sql = "update wx_group_info set wx_id=null,group_wx_name=null where group_id='%s'" % group_id
        mySqlUtil.excSql(sql)
        sql = "delete from wx_friend_rela where wx_main_id='%s' and wx_id='%s' " % (wx_id, group_id)
        mySqlUtil.excSql(sql)
        sql = "delete from wx_group_member where wx_id='%s' and group_id='%s' " % (wx_id, group_id)
        mySqlUtil.excSql(sql)

    return HttpResponse(json.dumps({"status": "200"}))


def createTask(group_id, wx_id, group_wx_name, group_name, groupUsage, groupNotice, friend_list, task_type, uuid,oper_name):
    taskSeq = round(time.time() * 1000 + random.randint(100, 999))
    sql = "insert into wx_task_manage(taskSeq,uuid,actionType,createTime,priority,status,operViewName)values('%s','%s',%d,now(),3,1,'%s')" % (
        taskSeq, uuid, task_type,oper_name)
    mySqlUtil.excSql(sql)
    sql = "INSERT INTO wx_group_task(taskSeq,wxId,mainWxName,groupName,friendList,groupUsage,groupNotice)VALUES" \
          "(%d,'%s','%s','%s','%s','%s','%s') " % (
          taskSeq, wx_id, group_wx_name, group_name, friend_list, groupUsage, groupNotice)
    mySqlUtil.excSql(sql)
    if group_id:
        sql = "update wx_group_info set status=2 where group_id='%s'" % group_id
        mySqlUtil.excSql(sql)


@csrf_exempt
def getGroupTaskInfo(request):
    ret = {}
    task_date = common.getValue(request, 'task_date')
    try:
        sql = u"select g.groupName,g.mainWxName,m.startTime, (m.endTime - m.startTime),m.status,m.remarks, " \
              u"(select name from wx_dictionary where type='task_type' and value=m.actionType) " \
              u"from wx_task_manage m, wx_account_info a, wx_group_task g " \
              u"where m.uuid=a.uuid and g.taskSeq=m.taskSeq and m.actionType in (12,13,14,15,16,17,18) and (a.wx_login_id in (select w.object_id from wx_oper_wx w where type=0 and oper_id='" + str(
            request.session['oper_id']) + "') or" \
                                          u" a.wx_id in (select w.object_id from wx_oper_wx w where type=0 and oper_id='" + str(
            request.session['oper_id']) + "'))" \
                                          u"and DATE_FORMAT(m.createTime,'%Y-%m-%d') = '" + task_date + "' order by m.createTime desc "

        task_info_list = mySqlUtil.getData(sql)
        task_list = []
        for task_info in task_info_list:
            task_list.append({"groupName": task_info[0], "mainWxName": task_info[1], "startTime": task_info[2],
                              "seconds": task_info[3], "status": task_info[4], "remark": task_info[5],
                              "actionType": task_info[6]})
        ret["task_list"] = task_list
    except(Exception) as e:
        logger.error(e)

    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))


@csrf_exempt
def authCheck(request):
    ret = {}
    try:
        group_id = request.GET.get("groupId")
        main_wx_str = "','".join(request.session['oper_main_wx'])
        sql = """select count(1) from wx_group_info i where group_id = '%s' and wx_id in ('%s') """ % (group_id,
                                                                                                            main_wx_str)
        # print(sql)
        checkret = mySqlUtil.getData(sql)
        if checkret and len(checkret) > 0:
            if checkret[0][0] > 0:
                ret['authCheckStatus'] = 1
            else:
                ret['authCheckStatus'] = 0
    except Exception as e:
        logger.info(traceback.format_exc())
    return HttpResponse(json.dumps(ret))


def groupSchedule(request):
    ret = {}
    ret["retStatus"] = -1
    try:
        operId = request.session['oper_id']
        oper_name = request.session['oper_name']
        groupId = request.GET.get("groupId")
        planName = request.GET.get("planName")
        scheduleTime = request.GET.get("scheduleTime")
        scheduleType = request.GET.get("scheduleType")
        wxIdFind = request.GET.get("wx_id")
        scheduleText = request.GET.get("scheduleText")
        schedulePicName = request.GET.get("schedulePicName")
        if scheduleType == "2":
            # 每天
            maxActionNum = 0
            taskType = 24
        elif scheduleType == "1":
            # 一次
            maxActionNum = 1
            taskType = 23
        else:
            maxActionNum = scheduleType  # TODO

        taskSeqMain = round(time.time() * 1000 + random.randint(100, 999))
        if scheduleText:
            taskSeq = round(time.time() * 1000 + random.randint(100, 999))
            sql = """INSERT INTO wx_schedule_task (taskSeq, taskMain, planName, groupId, wxId, taskType, createTime, actionTime, actionTimeFlag, actionNum, creatorId,actionMaxNum)
                                VALUES ('%s', '%s', '%s','%s', '%s', %s, now(), '%s', '%s',0, %s, %s)
                                """ % ( taskSeq, taskSeqMain, planName, groupId, wxIdFind, scheduleType, scheduleTime, scheduleTime, operId, maxActionNum)
            mySqlUtil.excSql(sql)
            sql = """INSERT INTO wx_chat_task (taskSeq, wx_main_id, wx_id, type, content, createTime, noticeName, msgId)
                                VALUES ('%s', '%s', '%s', '1', '%s', now(), NULL, '%s')
                                """ % (taskSeq, wxIdFind, groupId, scheduleText, str(taskSeq))
            mySqlUtil.excSql(sql)
            sql = """SELECT uuid from wx_account_info where wx_id = '%s'""" % (wxIdFind)
            uuidFind = mySqlUtil.getData(sql)[0][0]
            sql = """INSERT INTO wx_task_manage (taskSeq, uuid, actionType, createTime, startTime, endTime, priority, remarks, status, alarm, cronTime, operViewName)
                                VALUES ('%s', '%s', '%s', now(),NULL, NULL, '1', "", '1', '0', '%s','%s');
                                """ % (taskSeq, uuidFind, taskType, scheduleTime,oper_name)
            mySqlUtil.excSql(sql)
            # if scheduleType == "1":
            #     sql = "insert into wx_chat_info(wx_main_id, wx_id, send_time, type, content, send_type, status, msgId)" \
            #           "values('%s', '%s', now(), '1', '%s', '1', '0', '%s') " % (wxIdFind, groupId, scheduleText, str(taskSeq))
            #     # mySqlUtil.excSql(sql)
            #     print(sql)

        if schedulePicName:
            for picName in schedulePicName[:-1].split(';'):
                taskSeq = round(time.time() * 1000 + random.randint(100, 999))
                sql = """INSERT INTO wx_schedule_task (taskSeq, taskMain, planName, groupId, wxId, taskType, createTime, actionTime, actionTimeFlag, actionNum, creatorId,actionMaxNum)
                                                    VALUES ('%s', '%s', '%s','%s', '%s', %s, now(), '%s', '%s',0, %s,%s)
                                                    """ % ( taskSeq, taskSeqMain, planName, groupId, wxIdFind, scheduleType, scheduleTime, scheduleTime, operId, maxActionNum)
                mySqlUtil.excSql(sql)
                sql = """INSERT INTO wx_chat_task (taskSeq, wx_main_id, wx_id, type, content, createTime, noticeName, msgId)
                                    VALUES ('%s', '%s', '%s', '2', '%s', now(), NULL, '%s') """ % (taskSeq, wxIdFind, groupId, picName, str(taskSeq))
                mySqlUtil.excSql(sql)
                sql = """SELECT uuid from wx_account_info where wx_id = '%s'""" % (wxIdFind)
                uuidFind = mySqlUtil.getData(sql)[0][0]
                sql = """INSERT INTO wx_task_manage (taskSeq, uuid, actionType, createTime, startTime, endTime, priority, remarks, status, alarm, cronTime,operViewName)
                                                    VALUES ('%s', '%s', '%s', now(),NULL, NULL, '1', "", '1', '0', '%s','%s');
                                                    """ % (taskSeq, uuidFind, taskType, scheduleTime,oper_name)
                mySqlUtil.excSql(sql)
                # if scheduleType == "1":
                #     sql = "insert into wx_chat_info(wx_main_id, wx_id, send_time, type, content, send_type, status, msgId)" \
                #           "values('%s', '%s', now(), '2', '%s', '1', '0', '%s') " % (wxIdFind, groupId, picName.split("|")[1], str(taskSeq))
                #     mySqlUtil.excSql(sql)
        ret["retStatus"] = 1
    except Exception as e:
        ret["retStatus"] = -1
        logger.warn(traceback.format_exc())
    return HttpResponse(json.dumps(ret))

def groupScheduleCheck(request):
    ret = {}
    ret['CheckStatus'] = 1
    ret['dataList'] = ""
    try:
        groupId = request.GET.get("groupId")
        wx_id = request.GET.get("wx_id")
        grouoInfoCheckSql = """SELECT A.taskMain,A.planName,min(A.createTime),A.actionTime,A.actionMaxNum,B.name,A.status from wx_schedule_task A
                                    join wx_system_operator B on A.creatorId = B.oper_id
                                    where A.groupId = '%s' and A.wxId='%s'
                                    group by A.taskMain,A.planName,A.actionTime,A.actionMaxNum,B.name,A.status""" % (groupId, wx_id)
        grouoInfo = mySqlUtil.getData(grouoInfoCheckSql)
        if grouoInfo:
            dataList = []
            for groupInfoItem in grouoInfo:
                if groupInfoItem[4] == 0:
                    deadLine = (
                    datetime.datetime.strptime(str(groupInfoItem[2]), "%Y-%m-%d %H:%M:%S") + datetime.timedelta(
                        days=365)).strftime("%Y-%m-%d %H:%M:%S")
                elif groupInfoItem[4] == 1:
                    deadLine = str(groupInfoItem[3])
                else:
                    deadLine = (
                    datetime.datetime.strptime(str(groupInfoItem[2]), "%Y-%m-%d %H:%M:%S") + datetime.timedelta(
                        days=int(groupInfoItem[4]))).strftime("%Y-%m-%d %H:%M:%S")
                dataList.append({
                    "taskMain": groupInfoItem[0],
                    "planName": groupInfoItem[1],
                    "createTime": str(groupInfoItem[2]),
                    "actionTime": str(groupInfoItem[3]),
                    "deadLine": deadLine,
                    "creator": groupInfoItem[5],
                    "status": groupInfoItem[6]
                })
            ret['dataList'] = dataList
            # print(ret['dataList'])
    except Exception as e:
        ret['CheckStatus'] = -1
        logger.warn(traceback.format_exc())

    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))


def scheduleTaskAction(request):
    ret = {}
    ret["actionStatus"] = -1
    try:
        taskSeqMain = request.GET.get("taskSeqMain")
        actType = request.GET.get("type")
        if actType == "0":
            status_S = 0
            status_M = 6
        elif actType == "1":
            status_S = 1
            status_M = 1

        taskScheduleStopSql = """UPDATE wx_schedule_task SET status=\'%s\' 
                                    WHERE (taskMain= \'%s\');""" % (status_S, taskSeqMain)
        mySqlUtil.excSql(taskScheduleStopSql)
        taskManagerStopSql = """UPDATE wx_task_manage SET status= %s
                                    WHERE taskSeq in (SELECT taskSeq from wx_schedule_task where taskMain = \"%s\")""" % (
        status_M, taskSeqMain)
        mySqlUtil.excSql(taskManagerStopSql)
        ret["actionStatus"] = 1
    except Exception as e:
        logger.warn(traceback.format_exc())
    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))


def modalBack(request):
    ret = {}
    try:
        pass
    except Exception as e:
        logger.warn(traceback.format_exc())
    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))


def scheduleByTaskSeqMian(request):
    ret = {}
    ret["actionStatus"] = -1
    ret["groupName"] = ""
    ret["wxName"] = ""
    ret["planName"] = ""
    ret["planType"] = ""
    ret["actionTime"] = ""
    ret["sendText"] = ""
    ret["sendPic"] = []
    try:
        taskSeqMain = request.GET.get("taskMain")
        taskInfoGetSql = """select A.planName,B.group_name,A.taskType,C.view_name,A.actionTime  from wx_schedule_task A
                                join wx_group_info B on A.groupId = B.group_id
                                join wx_group_member C on A.wxId = C.wx_id and B.group_id = C.group_id
                                where A.taskMain = \'%s\'
                                limit 1""" % taskSeqMain
        taskInfo = mySqlUtil.getData(taskInfoGetSql)
        # print(taskInfo)  # (('测试10', 'hahaha', 1, '愁容骑士'),)
        if taskInfo:
            ret["planName"] = taskInfo[0][0]
            ret["groupName"] = taskInfo[0][1]
            ret["planType"] = taskInfo[0][2]
            ret["wxName"] = taskInfo[0][3]
            ret["actionTime"] = str(taskInfo[0][4])

        infoTypeByTaskMainSql = """select A.taskSeq,B.type from wx_schedule_task A
                                    join wx_chat_task B on A.taskSeq = B.taskSeq
                                    where A.taskMain = \'%s\'""" % (taskSeqMain)
        infoType = mySqlUtil.getData(infoTypeByTaskMainSql)
        for infoItem in infoType:
            taskSeq = infoItem[0]
            taskType = infoItem[1]
            if int(taskType) == 1:
                textInfoSql = """SELECT content from wx_chat_task
                                    where taskSeq = \'%s\'""" % (taskSeq)
                ret["sendText"] = mySqlUtil.getData(textInfoSql)[0][0]
            if int(taskType) == 2:
                textInfoSql = """SELECT content from wx_chat_task
                                                    where taskSeq = \'%s\'""" % (taskSeq)
                ret["sendPic"].append(mySqlUtil.getData(textInfoSql)[0][0].split('|')[1])
        ret["actionStatus"] = 1
        # print(ret)
    except Exception as e:
        logger.warn(traceback.format_exc())
    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))
