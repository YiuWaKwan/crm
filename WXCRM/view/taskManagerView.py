from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from lib.ModuleConfig import ConfAnalysis
import mySqlUtil
import json
import time
import random
import os,requests
import signal
import common
import uuid,pymysql

from lib.FinalLogger import getLogger
# 初始化logger
loggerFIle = 'log/taskManagerViews.log'
logger = getLogger(loggerFIle)
# 初始化config
configFile = 'conf/moduleConfig.conf'
confAllItems = ConfAnalysis(logger, configFile)
PIDFILE = confAllItems.getOneOptions('task','pidFile')
imgsavepath = confAllItems.getOneOptions('img','imgsavepath')
fileServiceURL = confAllItems.getOneOptions('fileSystemService', 'fileServiceURL')

DEV_ID = confAllItems.getOneOptions('devInfo','dev')

def wxTaskManager(request):
    if request.method == 'GET':
        oper_id = request.session['oper_id']
        oper_name = request.session['oper_name']
    groupPerSql = """SELECT A.name,A.value from wx_dictionary A
                        join wx_oper_wx B
                        on (A.value = B.object_id)
                        where B.oper_id = %s
                        and B.type = 1""" %(oper_id)
    groupIdList = mySqlUtil.getData(groupPerSql)
    groupIdListRet = [ i for i in groupIdList ]
    taskTypeSql = """select name,value from wx_dictionary
                        where type = 'task_type'  and value not in (5,6,7,8)
                        order by `value`"""
    taskTypeList = mySqlUtil.getData(taskTypeSql)

    taskStatusSql = """select name,value from wx_dictionary
                            where type = 'task'
                            order by `value`"""
    taskStatusList = mySqlUtil.getData(taskStatusSql)
    # print(taskTypeList)
    return render(request, "wxTaskManager.html",{'groupIdList': list(groupIdListRet),'taskTypeList':taskTypeList,'taskStatusList':taskStatusList})

def queryWxTask(request):
    if request.method == 'GET':
        wxCheckId=request.GET.get('wxCheckId')
        phCheckId = request.GET.get('phCheckId')
        groupCheckId = request.GET.get('groupCheckId')
        typeCheckId = request.GET.get('typeCheckId')
        statusCheckId = request.GET.get('statusCheckId')
        pageShowNum = int(request.GET.get('pageShowNum'))
        oper_id = request.session['oper_id']
        oper_name = request.session['oper_name']

        if groupCheckId == "营销分组":
            groupCheckId = ""
        if typeCheckId == "0":
            typeCheckId = ""
        if statusCheckId == "任务状态":
            statusCheckId = ""
        pageIndex = request.GET.get('pageIndex')
        pageNum = int(pageIndex)

    # if typeCheckId == "任务类型":
    #     typeCheckId = ""
    # elif typeCheckId == "添加好友":
    #     typeCheckId = 1
    # elif typeCheckId == "养号聊天":
    #     typeCheckId = 2
    # elif typeCheckId == "朋友圈(原创)":
    #     typeCheckId = 4
    # elif typeCheckId == "朋友圈(转发)":
    #     typeCheckId = 3
    # elif typeCheckId == "聊天营销":
    #     typeCheckId = 5
    #
    # if statusCheckId == "任务状态":
    #     statusCheckId = ""
    # elif statusCheckId == "初始化":
    #     statusCheckId = 0
    # elif statusCheckId == "下发中":
    #     statusCheckId = 1
    # elif statusCheckId == "执行中":
    #     statusCheckId = 2
    # elif statusCheckId == "完成":
    #     statusCheckId = 4
    # elif statusCheckId == "失败":
    #     statusCheckId = 3
    # elif statusCheckId == "暂停":
    #     statusCheckId = 5


    pageStart = (pageNum - 1) * pageShowNum
    pageNum = pageShowNum

    if wxCheckId == "" and phCheckId == "" and groupCheckId == "" and typeCheckId == "" and statusCheckId == "":
        wxTaskCheckSql = """select B.wx_login_id wx_id,A.actionType,A.createTime,A.startTime,A.endTime,A.`status`,A.taskSeq,B.wx_name,d.name,A.remarks
                            from wx_task_manage A
                            join wx_account_info B on (A.uuid = B.uuid)
                            join wx_dictionary d on d.value=actionType and d.type='task_type' and value not in (5,6,7,8)
                            where B.wx_login_id in ( SELECT C.object_id from wx_oper_wx C where C.oper_id = %s and type = 0)
                            or B.wx_id IN (SELECT C.object_id from wx_oper_wx C where C.oper_id = %s and type = 0)
                            order by A.createTime desc,A.`status` asc,A.taskSeq
                            limit %s,%s""" % (oper_id,oper_id, pageStart, pageNum)
        countSql = """select count(1) from wx_task_manage A
                            join wx_account_info B on (A.uuid = B.uuid)
                            join wx_dictionary d on d.value=actionType and d.type='task_type'  and value not in (5,6,7,8)
                            where B.wx_login_id in ( SELECT C.object_id from wx_oper_wx C where C.oper_id = %s and type = 0)
                            or B.wx_id IN (SELECT C.object_id from wx_oper_wx C where C.oper_id = %s and type = 0)""" % (oper_id,oper_id)
    else:
        sqlConditions = """ where """
        if wxCheckId != "":
            sqlConditions += "B.wx_id like '%%%s%%' and " % wxCheckId
        if phCheckId != "":
            sqlConditions += "B.phone_no like '%%%s%%' and " % phCheckId
        if groupCheckId != "":
            sqlConditions += "B.groupId like '%%%s%%' and " % groupCheckId
        if typeCheckId != "":
            sqlConditions += "A.actionType = '%s' and " % typeCheckId
        if statusCheckId != "":
            sqlConditions += "A.status like '%%%s%%' and " % statusCheckId
        wxTaskCheckSql = """select B.wx_login_id wx_id,A.actionType,A.createTime,A.startTime,A.endTime,A.`status`,A.taskSeq , B.wx_name,
                            (select name from wx_dictionary d where d.value=actionType and d.type='task_type'),A.remarks
                             from wx_task_manage A
                            join wx_account_info B
                            on (A.uuid = B.uuid)
                            %s
                            and (B.wx_login_id in ( SELECT C.object_id from wx_oper_wx C where C.oper_id = %s and type = 0)
                            OR B.wx_id IN (SELECT C.object_id from wx_oper_wx C where C.oper_id = %s and type = 0))
                            order by A.createTime desc,A.`status` asc,A.taskSeq
                            limit %s,%s""" % (sqlConditions[:-4],oper_id,oper_id,pageStart, pageNum)
        countSql = """select count(1) from wx_task_manage A
                            join wx_account_info B
                            on (A.uuid = B.uuid) %s
                            and (B.wx_login_id in ( SELECT C.object_id from wx_oper_wx C where C.oper_id = %s and type=0)
                            or B.wx_id IN (SELECT C.object_id from wx_oper_wx C where C.oper_id = %s and type = 0))
                            """ %(sqlConditions[:-4],oper_id,oper_id)
    taskInfoList = mySqlUtil.getData(wxTaskCheckSql)
    countNum = mySqlUtil.getData(countSql)

    statusDict = {
        1: '下发中',
        2: '执行中',
        4: '完成',
        3: '失败'
    }
    taskActionDict = {
        1: '添加好友',
        2: '养号聊天',
        4: '朋友圈（原创）',
        3: '朋友圈（转发）'
    }
    retList = {}
    index=0
    for info in taskInfoList:
        retList[index] ={'wx_id': info[0],
             'task_type': info[1],
             'create_time': str(info[2]),
             'start_time': '等待启动' if info[3] is None else str(info[3]),   # a if a>b else b
             'end_time':'等待结束' if info[4] is None else str(info[4]),
             # 'status': statusDict[info[5]]
             'status': info[5],
             'taskSeq' : info[6],
             'task_type_name':info[8],
             'wx_name' :info[7],
             'taskRemarks' : '无备注' if info[9] is None else str(info[9])
             }
        index=index+1

    pageCount = int((int(countNum[0][0]) / pageShowNum)) + 1
    retList['countNum'] = int(countNum[0][0])
    retList['pageCount'] = pageCount

    return HttpResponse(json.dumps(retList))

def createWxTask(request):
    retList = {}
    return HttpResponse(json.dumps(retList))

def startWxTask(request,loopGap = 4):
    if request.method == 'GET':
        startValue = request.GET.get('startValue')
    dataValue = startValue[:-1].split(',')
    slicesNum = int(len(dataValue) / loopGap)

    slicesStartIndex = 0
    # checkUniqTypeSql = """SELECT distinct(actionType) FROM `wx_task_manage`
    #                     where `status` = 1 or `status` = 2"""
    # checkUniqTypeRet = mySqlUtil.getData(checkUniqTypeSql)

    # if (len(checkUniqTypeRet) != 0 and checkUniqTypeRet[0][0] != dataValue[2]):
    #     retStatus = -1
    # else:
    dataValueList = []
    for i in range(slicesNum):
        dataValueList.append(dataValue[ slicesStartIndex : slicesStartIndex + loopGap])
        slicesStartIndex += loopGap
    replaceVauleTmp = ""
    for taskItem in dataValueList:
        replaceVauleTmp += "\'%s\'," %(taskItem[0])
    replaceVaule = "(%s)" %replaceVauleTmp[:-1]
    replaceSql = """update wx_task_manage set STATUS = 1
          where taskSeq in %s""" %replaceVaule

    # 启动养号聊天子任务
    startRandomChatSql = """REPLACE INTO wx_randomChat_task (uuid,`status`)
                                                select B.uuid,1 from wx_task_manage B
                                                join wx_machine_info C
                                                on (B.uuid = C.uuid)
                                                where C.clientId = \'%s\'
                                                and B.taskSeq in %s
                                                group by B.uuid""" % (DEV_ID, replaceVaule)
    try:
        startSqlExec = mySqlUtil.excSql(replaceSql)
        startSubRandomChatSqlExec = mySqlUtil.excSql(startRandomChatSql)
        retStatus = 1
    except Exception as e:
        retStatus = -1
        logger.warn(e)
    retList = {}
    retList['retStatus'] = retStatus
    return HttpResponse(json.dumps(retList))

def stopWxTask(request,loopGap = 4):
    if request.method == 'GET':
        stopTypeFlag=request.GET.get('stopTypeFlag')
        stopList = request.GET.get('stopList')

    if stopTypeFlag == "0":
        # 0: 全部任务停止

        # 将 任务主表 全部下发或运行中任务 置为暂停 ,只包含
        stopSql = """update wx_task_manage  A
                        join wx_machine_info B
                        on (A.uuid = B.uuid)
                        set A.`status` = 5
                        where B.clientId = \'%s\'
                        and (A.`status` = 2 or A.`status` = 1)""" %DEV_ID

        # 更新养号聊天任务子表
        stopRandomChatSql = """ REPLACE INTO wx_randomChat_task (uuid,`status`)
                                    select B.uuid,0 from wx_machine_info B
                                    where B.clientId = \'%s\'
                                    group by B.uuid""" %DEV_ID
        try:
            stopSqlExec = mySqlUtil.excSql(stopSql)
            stopRandomChatExec = mySqlUtil.excSql(stopRandomChatSql)
            with open(PIDFILE, 'r') as pidFile:
                pid = int(pidFile.readline())
            try:
                os.kill(pid, signal.SIGTERM)
            except Exception:
                pass
            retStatus = 1
        except Exception as e:
            retStatus = -1
            logger.warn(e)
    else :
        dataValue = stopList[:-1].split(',')
        slicesNum = int(len(dataValue) / loopGap)
        slicesStartIndex = 0
        dataValueList = []
        for i in range(slicesNum):
            dataValueList.append(dataValue[slicesStartIndex: slicesStartIndex + loopGap])
            slicesStartIndex += loopGap
        replaceVauleTmp = ""
        for taskItem in dataValueList:
            replaceVauleTmp += "\'%s\'," % (taskItem[0])
        replaceVaule = "(%s)" % replaceVauleTmp[:-1]
        replaceSql = """update wx_task_manage set STATUS = 5
                      where taskSeq in %s""" % replaceVaule

        # 处理养好聊天子任务表
        replaceSubRandomChatTaskSql = """REPLACE INTO wx_randomChat_task (uuid,`status`)
                                            select B.uuid,0 from wx_task_manage B
                                            where B.taskSeq in %s
                                            group by B.uuid""" %(replaceVaule)
        try:
            # #当前任务运行中进行kill
            # ifStartSql = """select count(1) from wx_task_manage where STATUS=2 and taskSeq in %s""" % replaceVaule
            # ifStart =  mySqlUtil.getData(replaceSql)
            # if ifStart != 0:
            #     with open(PIDFILE, 'r') as pidFile:
            #         pid = int(pidFile.readline())
            #     try:
            #         os.kill(pid, signal.SIGTERM)
            #     except Exception:
            #         pass
            # 任务状态更新
            stopSqlExec = mySqlUtil.excSql(replaceSql)
            stopSqlExec = mySqlUtil.excSql(replaceSubRandomChatTaskSql)
            retStatus = 1
        except Exception as e:
            retStatus = -1
            logger.warn(e)


    retList = {}
    retList['retStatus'] = retStatus
    return HttpResponse(json.dumps(retList))

def delWxTask(request,loopGap = 4):
    # delValue
    if request.method == 'GET':
        delValue = request.GET.get('delValue')
    dataValue = delValue[:-1].split(',')

    slicesNum = int(len(dataValue) / loopGap)

    slicesStartIndex = 0
    dataValueList = []
    for i in range(slicesNum):
        dataValueList.append(dataValue[ slicesStartIndex : slicesStartIndex + loopGap])
        slicesStartIndex += loopGap
    delVauleTmp = ""
    for taskItem in dataValueList:
        delVauleTmp += "\'%s\'," %(taskItem[0])
    delVaule = " (%s) " %delVauleTmp[:-1]
    delSql = """DELETE FROM wx_task_manage
        where taskSeq in %s """ %delVaule
    try:
        delSqlExec = mySqlUtil.excSql(delSql)
        retStatus = 1
    except Exception as e:
        retStatus = -1
        logger.warn(e)
    retList = {}
    retList['retStatus'] = retStatus
    return HttpResponse(json.dumps(retList))

def wxAccountInfoQuery(request):
    # 获取用户id
    oper_id = request.session['oper_id']
    oper_name = request.session['oper_name']

    wxAccountInfoSql = """SELECT head_picture,wx_id,groupId,if_start,wx_login_id,wx_name FROM `wx_account_info`
                        where if_start = 1
                        and (wx_id in (select object_id from wx_oper_wx where oper_id=%s and type=0)
                        or wx_login_id in (select object_id from wx_oper_wx w where type=0 and oper_id=%s))
                        group by head_picture,wx_id,groupId,if_start,wx_login_id,wx_name"""%( oper_id, oper_id )
    try:
        print(wxAccountInfoSql)
        wxAccountInfoRet = mySqlUtil.getData(wxAccountInfoSql)
    except Exception as e:
        logger.warn(e)
    index = 0
    retList = {}

    for info in wxAccountInfoRet:

        retList[index]={'head_picture': info[0],
             'wx_id': info[1],
             'groupId': str(info[2]),
            'if_start' : info[3],
            'wx_login_id':info[4],
            'wx_name':info[5]
             }
        index += 1

    return HttpResponse(json.dumps(retList))


def addFriendTaskCreate(request,loopGap = 3):
    oper_name = request.session['oper_name']
    if request.method == 'GET':
        createTaskValue = request.GET.get('createTaskValue')
        sayHi = request.GET.get('sayHi')
        friendNumMax = request.GET.get('friendNumMax') #TODO
        wxIdList = request.GET.get('wxIdList')
    # data pre process
    # taskSeq


    dataValue = createTaskValue[:-1].split(',')

    slicesNum = int(len(dataValue) / loopGap)

    slicesStartIndex = 0
    dataValueList = []
    for i in range(slicesNum):
        dataValueList.append(dataValue[ slicesStartIndex : slicesStartIndex + loopGap])
        slicesStartIndex += loopGap

    # 拼装账号
    accountList = ""
    for accoutItem in dataValueList:
        accountList += "\'%s\'," %accoutItem[1]
    accountListMod = "(%s)" %accountList[:-1]
    accountUuidGetSql = """SELECT `uuid` from wx_account_info
            where wx_id in %s""" %accountListMod
    # 拼价添加信息
    addFreindList = "#".join(wxIdList.split('\n'))

    try:
        # 任务信息
        uuidGetList = mySqlUtil.getData(accountUuidGetSql)
        createTaskValue = ""
        addFriendList = ""
        for uuid in uuidGetList:
            taskSeq = round(time.time() * 1000 + random.randint(100,999))
            createTaskValue += "(\'%s\',\'%s\',1,now(),'3','1',\'%s\')," %(taskSeq,uuid[0],oper_name)
            addFriendList += "(\'%s\',\'%s\',\'%s\')," %(taskSeq,addFreindList,sayHi)
        taskCreateSql = """INSERT INTO `wx_task_manage` (`taskSeq`, `uuid`, `actionType`, `createTime`,`priority`,`status`,`operViewName`) VALUES %s""" %(createTaskValue[:-1])
        addFreindInsertSql = """INSERT INTO `wx_add_friend` (`taskSeq`, `frinedIdList`, `sayHi`) VALUES %s""" %(addFriendList[:-1])
        addFreindInsertSqlRun = mySqlUtil.excSql(addFreindInsertSql)
        taskCreateSqlRun = mySqlUtil.excSql(taskCreateSql)
        retStatus = 1
    except Exception as e:
        retStatus = -1
        logger.warn(e)
    retList = {}
    retList['retStatus'] = retStatus
    return HttpResponse(json.dumps(retList))

def randomChatTaskCreate(request,loopGap = 3):
    oper_name = request.session['oper_name']
    if request.method == 'GET':
        createTaskValue = request.GET.get('createTaskValue')
    dataValue = createTaskValue[:-1].split(',')

    slicesNum = int(len(dataValue) / loopGap)

    slicesStartIndex = 0
    dataValueList = []
    for i in range(slicesNum):
        dataValueList.append(dataValue[ slicesStartIndex : slicesStartIndex + loopGap])
        slicesStartIndex += loopGap

    # 拼装账号
    accountList = ""
    for accoutItem in dataValueList:
        accountList += "\'%s\'," %accoutItem[1]
    accountListMod = "(%s)" %accountList[:-1]
    accountUuidGetSql = """SELECT `uuid` from wx_account_info
            where wx_id in %s""" %accountListMod

    try:
        # 任务信息
        uuidGetList = mySqlUtil.getData(accountUuidGetSql)
        createTaskValue = ""
        replaceTaskValue = ""
        for uuid in uuidGetList:
            taskSeq = round(time.time() * 1000 + random.randint(100, 999))
            createTaskValue += "(\'%s\',\'%s\',2,now(),'99','1',\'%s\')," %(taskSeq,uuid[0],oper_name)
            replaceTaskValue += "(\'%s\',1)," %(uuid[0])
        taskCreateSql = """INSERT INTO `wx_task_manage` (`taskSeq`, `uuid`, `actionType`, `createTime`,`priority`,`status`,`operViewName`) VALUES %s""" %(createTaskValue[:-1])

        subTaskReplace = """REPLACE INTO wx_randomChat_task(uuid,status) 
                                VALUES %s """ %(replaceTaskValue[:-1])

        taskCreateSqlRun = mySqlUtil.excSql(taskCreateSql)
        subtaskCreateSqlRun = mySqlUtil.excSql(subTaskReplace)
        retStatus = 1
    except Exception as e:
        retStatus = -1
        logger.warn(e)
    retList = {}
    retList['retStatus'] = retStatus
    return HttpResponse(json.dumps(retList))

def commentTaskCreate(request,loopGap = 3):
    oper_name = request.session['oper_name']
    typePick = request.GET.get('typePick')
    commentContent = request.GET.get('commentContent')
    wx_id_str = request.GET.get('wx_id_str')
    wx_id_list = []
    pickFileList=""
    if wx_id_str is not None:
        wx_id_list = wx_id_str[:-1].split(',')
    if typePick == "0":
        pickFileList = request.GET.get('pickFileList')
        if pickFileList is None:
            pickFileList=""
    elif typePick == "1":
        urlLinkInput = request.GET.get('urlLinkInput')

    try:
        picTaskSeq=0
        # 保存图片信息
        if len(pickFileList) > 0:
            picTaskSeq = round(time.time() * 1000 + random.randint(100, 999))
            for pic in pickFileList.split(r'|'):
                fp = open(imgsavepath+pic,'rb')
                img = fp.read()
                fp.close()
                #print(img)
                pic_insert = "insert into wx_moments_pic(picTaskSeq, picture, picture_name)values("+str(picTaskSeq)+", %s, '"+pic+"')"
                mySqlUtil.excBLOB(pic_insert, img)
                #删除上传文件
                os.remove(imgsavepath+pic)
        # 任务信息
        for wx_id in wx_id_list:
            taskSeq = round(time.time() * 1000 + random.randint(100, 999))
            if typePick == "0":# 原创
                taskCreateSql="""INSERT INTO wx_task_manage(taskSeq, uuid, actionType, createTime,priority,status,operViewName)
                                 select %d, uuid ,4,now(),3,1,'%s' as operViewName from wx_account_info where wx_id = '%s' """ % (taskSeq,oper_name,wx_id)
                commentCreateSql = """INSERT INTO wx_moments_picType(taskSeq, picRoot, picNames, momentContents, picTaskSeq) VALUES (%d,'','','%s', %d)""" \
                                   % (taskSeq,commentContent, picTaskSeq)

            elif typePick == "1":# 转发
                taskCreateSql = """INSERT INTO wx_task_manage(taskSeq, uuid, actionType, createTime,priority,status,operViewName)
                                  select %d, uuid ,3,now(),3,1,'%s' as operViewName from wx_account_info where wx_id = '%s' """ % (taskSeq,oper_name,wx_id)
                commentCreateSql = """INSERT INTO wx_moments_linkType(taskSeq, linkUrl, momentContents) VALUES (%d,'%s','%s')""" \
                                   % (taskSeq, urlLinkInput, commentContent)

            mySqlUtil.excSql(taskCreateSql)
            mySqlUtil.excSql(commentCreateSql)
        retStatus = 1
    except Exception as e:
        retStatus = -1
        logger.warn(e)
    retList = {}
    retList['retStatus'] = retStatus
    return HttpResponse(json.dumps(retList))

@csrf_exempt
def bootTask(request):
    try:
        oper_name = request.session['oper_name']
        flag = request.GET.get('flag')
        wx_id_str = request.GET.get('wx_id_str')
        wx_id_list = wx_id_str[:-1].split(',')
        actionType=10
        if flag == "stop":
            actionType=11

        for wx_id in wx_id_list:
            taskSeq = round(time.time() * 1000 + random.randint(100, 999))
            sql = "INSERT INTO wx_task_manage(taskSeq,uuid,actionType,createTime,status,priority,operViewName) " \
                  " select %d, uuid ,%d,now(),1,4,'%s' as operViewName from wx_account_info where wx_id = '%s'" % (taskSeq, actionType,oper_name,wx_id)
            mySqlUtil.excSql(sql)
        retStatus=1
    except Exception as e:
        retStatus = -1
        logger.warn(e)
    retList = {}
    retList['retStatus'] = retStatus
    return HttpResponse(json.dumps(retList))

@csrf_exempt
def fileupload(request):
    ret={}
    flag = True
    try:
        if 'imgfiles' in request.FILES :
            filename = request.FILES['imgfiles']
            logger.info(filename)
            if r'.' in filename :
                filename = '.' + filename.split(r'.')[1]
            else:
                filename = '.jpg'
            filename = str(uuid.uuid1()) + filename
            allfilename = imgsavepath+filename
            logger.info(allfilename)
            with open(allfilename, 'wb+') as destination:
                for chunk in request.FILES['imgfiles'].chunks():
                    destination.write(chunk)
            ret={"data":filename}
        if 'chatfiles' in request.FILES :
            filename = request.FILES['chatfiles'].name
            #filesize = request.FILES['chatfiles'].size
            wx_id = common.getValue(request, "wx_id")
            uuid_name=str(uuid.uuid1())
            if r'.' in filename :
                file_tail = filename.split(r'.')[1]
                uuid_name = uuid_name+'.' + file_tail

            filename=filename
            allfilename = imgsavepath+uuid_name
            with open(allfilename, 'wb+') as destination:
                for chunk in request.FILES['chatfiles'].chunks():
                    destination.write(chunk)

            #fileServiceURL
            img_obj = open(allfilename, "rb")
            fileSendUrl = fileServiceURL+"/uploadMsgFile/"
            ret = requests.post(fileSendUrl,
                                files={"chatfiles": (filename, img_obj, "image/jpg")},
                                data={"wx_id": wx_id, "file_name": filename})
            logger.info(ret.text)
            img_obj.close()
            if ret.text:
                ret = json.loads(ret.text)
                ret["content"] = fileServiceURL+ret["content"]
                if ret["filename"][-3:]=="mp4":
                    ret["filename"] =fileServiceURL+ ret["filename"]

            #ret = {"data": uuid_name+"|"+filename,"filename":uuid_name,"filesize":filesize}
    except Exception as e:
        flag = False
        logger.warn(e)

    ret["flag"] = flag
    return HttpResponse(json.dumps(ret))
