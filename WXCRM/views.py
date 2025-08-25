import uuid
import traceback
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import StreamingHttpResponse
from dwebsocket.decorators import accept_websocket,require_websocket
from lib.ModuleConfig import ConfAnalysis
from django_redis import get_redis_connection
import os, MysqlDbPool,common,json, time, random
from lib.DateEncoder import DateEncoder
from lib.FinalLogger import getLogger
import threading
# 初始化logger
loggerFIle = 'log/views.log'
logger = getLogger(loggerFIle)
# 初始化config
configFile = 'conf/moduleConfig.conf'
confAllItems = ConfAnalysis(confDir=configFile)
img_save_path = confAllItems.getOneOptions('img', 'imgsavepath')
alarm_server = confAllItems.getOneOptions('alarm', 'alarm_server')
redis_con = get_redis_connection("default")

try:
    chatVersion = confAllItems.getOneOptions('chat','version')
except Exception as e:
    chatVersion = ''

try:
    mySqlUtil=MysqlDbPool.MysqlDbPool()
except Exception as e:
    logger.info(traceback.format_exc())
@csrf_exempt
def loginSystem(request):
    account_name = common.getValue(request, 'account_name')
    account_pwd = common.getValue(request, 'account_pwd')
    msg = ""
    log_id = ""
    sql = "select oper_id, name, pwd, state from wx_system_operator where name='%s' and state in ('0','1')" % account_name
    account_info = mySqlUtil.getData(sql)
    if len(account_info) > 0:
        if account_info[0][3] == '0':
            msg = "账号未审核"
        else:
            if account_info[0][2] == account_pwd:
                sql = "select log_id from wx_oper_logtime where oper_id='%s' and logout_time is null" % account_info[0][0]
                login_info = mySqlUtil.getData(sql)
                if login_info is not None and len(login_info) > 0:
                    sql = "update wx_oper_logtime set logout_time=now() where oper_id='%s' and logout_time is null" % account_info[0][0]
                    mySqlUtil.excSql(sql)

                ip = request.META['REMOTE_ADDR']
                #关键信息写session
                request.session['oper_id'] = account_info[0][0]
                request.session['oper_name'] = account_info[0][1]
                #写登录日志
                log_id = uuid.uuid1()
                sql = "insert into wx_oper_logtime(ip,oper_id,login_time, log_id) values('%s', '%s', now(), '%s')" % (ip, request.session['oper_id'], log_id)
                mySqlUtil.excSql(sql)

                sql="select object_id from wx_oper_wx where oper_id='%s' and type='0' union select wx_id from wx_account_info where wx_login_id in(select object_id from wx_oper_wx where oper_id='%s' and type='0')" %(account_info[0][0],account_info[0][0])
                oper_main_wx = []
                mainWxList = mySqlUtil.getData(sql) #当前用户所能操作的微信主号

                if mainWxList:
                    for mainWx in mainWxList:
                        oper_main_wx.append(mainWx[0])
                        #flush_friend(request.session['oper_name'], mainWx[0])   #刷好友信息  暂时屏蔽
                request.session['oper_main_wx'] = oper_main_wx  # 把微信主号权限写入session
            else:
                msg = "密码错误"
    else:
        msg = "账号不存在"
    response = HttpResponse(json.dumps({"msg": msg}))
    if log_id != "":
        response.set_cookie('LOG_ID', log_id)
    return response

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


@csrf_exempt
def passwordChange(request):
    account_name = request.session['oper_name']
    account_pwd = common.getValue(request, 'account_pwd')
    account_original_pwd = common.getValue(request, 'account_original_pwd')
    msg = ''
    sql = "select pwd from wx_system_operator where name='%s' and state in ('0','1')" % account_name
    pwd_info = mySqlUtil.getData(sql)
    if(account_original_pwd  == pwd_info[0][0]):
        sql_password = "update wx_system_operator set pwd ='%s' where name = '%s'" % (account_pwd, account_name)
        mySqlUtil.excSql(sql_password)
        msg = "success"
    else:
        msg = "wrong password"

    return HttpResponse(json.dumps({"msg":msg}))

@csrf_exempt
def user_time_manage(request):
    return render(request, "user_tracker.html")

@csrf_exempt
def logout(request):
    logoutTask(request)
    response = HttpResponse(json.dumps({"msg": ""}))
    response.delete_cookie("LOG_ID")
    return response

def logoutTask(request):
    if request.COOKIES.get("LOG_ID") :
        sql_logout = "update wx_oper_logtime set logout_time = now() where logout_time is null and log_id = '%s' " % request.COOKIES.get("LOG_ID")
        print(sql_logout)
        mySqlUtil.excSql(sql_logout)
    del request.session['oper_id']
    if request.session.get('oper_name', None) is not None :
        del request.session['oper_name']
    if request.session.get('oper_main_wx', None) is not None :
        del request.session['oper_main_wx']

def login(request):
    return render(request, "login.html")

def sessionLost(request):
    return render(request, "sessionLost.html")

def loginLost(request):
    return render(request, "loginLost.html")

def index(request):
    return render(request, "index.html")

@csrf_exempt
def total(request):
    ret={}
    # print(request.session.session_key)
    sql="""select count(1),ifnull(sum(case when if_start=1 then 1 else 0 end) ,0) from wx_account_info A 
         where (wx_login_id in ( SELECT C.object_id from wx_oper_wx C where C.oper_id = %s and C.type='0') 
        or wx_id in (SELECT C.object_id from wx_oper_wx C where C.oper_id = %s and C.type='0'))
    """% (request.session['oper_id'], request.session['oper_id'])
    statData = mySqlUtil.getData(sql)
    if len(statData) > 0:
        ret["wx_num"]=str(statData[0][0]) #主号数
        ret["wx_online"] = str(statData[0][1])   #在线数
    #目前好友总数
    sql="""select count(*)
             from wx_friend_list b where 1=1  and wx_id in(select wx_id from wx_friend_rela where wx_main_id in(
             (select object_id from wx_oper_wx where oper_id=%s and type='0' 
              union 
             select wx_id from wx_account_info where wx_login_id in(select object_id from wx_oper_wx where oper_id=%s and type='0'))
             ))
    """% (request.session['oper_id'], request.session['oper_id'])
    statData = mySqlUtil.getData(sql)
    if len(statData) > 0:
        ret["fensi_num"] = str(statData[0][0])
    #昨天成功新加好友数
    sql="""select count(1) from wx_friend_list b where 1=1  and wx_id in(
            select wx_id from wx_friend_rela 
            where add_time < CAST(Now() AS DATE) 
            and add_time >= CAST(DATE_ADD(Now(),interval -1 DAY)AS DATE) 
            and wx_main_id in(
             (select object_id from wx_oper_wx where oper_id=%s and type='0' 
              union 
             select wx_id from wx_account_info where wx_login_id in(select object_id from wx_oper_wx where oper_id=%s and type='0'))
             ))
    """% (request.session['oper_id'], request.session['oper_id'])
    statData = mySqlUtil.getData(sql)
    if len(statData) > 0:
        ret["wx_new"] = str(statData[0][0])
    # 昨天加好友数 暂时改为任务数
    # sql="""select count(1) from wx_task_manage
    #        where actiontype='1' and createtime < date_format(Now(),'%Y-%m-%d')
    #        and createtime >=date_format(DATE_ADD(Now(),interval -1 DAY),'%Y-%m-%d')"""
    sql = """ select count(1) from wx_task_manage m,wx_account_info i
               where m.actiontype='1' and m.createtime < CAST(Now() AS DATE) 
               and m.createtime >= CAST(DATE_ADD(Now(),interval -1 DAY)AS DATE) 
                and i.uuid = m.uuid  
                and i.wx_id in ((select object_id from wx_oper_wx where oper_id=%s and type='0' 
                 union 
                select wx_id from wx_account_info where wx_login_id in(select object_id from wx_oper_wx where oper_id=%s and type='0')))
	"""% (request.session['oper_id'], request.session['oper_id'])
    statData = mySqlUtil.getData(sql)
    if len(statData) > 0:
        ret["wx_add"] = str(statData[0][0])

    #sql="select count(distinct(wx_id)) from wx_chat_info_his where send_type='2' and send_time < date_format(Now(),'%Y-%m-%d') and send_time >=date_format(DATE_ADD(Now(),interval -1 DAY),'%Y-%m-%d')"
    sql = """select count(1) from wx_friend_list b where 1=1  and wx_id in(
            select wx_id from wx_friend_rela 
            where last_chart_time < CAST(Now() AS DATE) 
            and last_chart_time >= CAST(DATE_ADD(Now(),interval -1 DAY)AS DATE)  and last_chart_time !=null
            and wx_main_id in
             (select object_id from wx_oper_wx where oper_id=%s and type='0' 
            union 
             select wx_id from wx_account_info where wx_login_id in(select object_id from wx_oper_wx where oper_id=%s and type='0')))
    """% (request.session['oper_id'], request.session['oper_id'])
    statData = mySqlUtil.getData(sql)
    if len(statData) > 0:
        ret["wx_huoyue"] = str(statData[0][0])

    mainWxStr = "','".join(request.session['oper_main_wx'])
    sql = """SELECT COUNT(DISTINCT i.group_id) FROM wx_group_info i, (select group_id, wx_id, view_name from wx_group_member  where wx_id in ('%s')) g
          WHERE g.group_id = i.group_id and i.STATUS != 0 AND i.group_name != ''
          and exists(select 1 from wx_friend_rela where wx_id=i.group_id and state='1' and wx_main_id in ('%s')) 
    """ % (mainWxStr, mainWxStr)
    statData = mySqlUtil.getData(sql)
    if len(statData) > 0:
        ret["wx_group"] = str(statData[0][0])

    return HttpResponse(json.dumps(ret))

def main(request):
    oper_id = request.session.get('oper_id',None)
    # if oper_id is None:
    #     oper_id = request.COOKIES.get("ID")
    #     if oper_id is not None and oper_id != "":  # 清除登录信息
    #         mySqlUtil.excSql( "update wx_oper_logtime set logout_time = now() where logout_time is null and oper_id = '%s' " % oper_id)
    #     return render(request, "login.html")

    sql = "select menu_id,menu_name,parent_menu_id,menu_desc,menu_link,menu_order,menu_icon,(select count(menu_id) from wx_menu_info where parent_menu_id=a.menu_id) as childNum,type from wx_menu_info a where type='1' and menu_id in(select menu_id from wx_oper_menu where oper_id='%s')order by menu_order asc" %oper_id
    menuList = mySqlUtil.getData(sql)
    #print(menuList)
    return render(request, "main.html", {'menuList': menuList})

def login_data(request):
    oper_id = request.session['oper_id']
    sql = "select * from wx_oper_logtime where oper_id = '%s' order by login_time desc "%(oper_id)
    log_data_list = mySqlUtil.getData(sql)
    return HttpResponse(json.dumps(log_data_list, ensure_ascii=False, cls=DateEncoder))
    #return render(request,"user_tracker.html", {'logList': log_data_list})

def wxAccount(request):
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

    # RegPerSql = """SELECT name FROM `wx_dictionary`
    #                     where type = 'persionId'
    #                     GROUP BY name;"""
    # RegIdList = mySqlUtil.getData(RegPerSql)
    # RegIdListRet = [ i[0] for i in RegIdList]
    RegIdListRet = [oper_name]
    file_dir = './WXCRM/static/img/headImg'
    tmp_va= [i[2] for i in os.walk(file_dir)]
    if len(tmp_va)>0:
        picList = tmp_va[0]
    else:
        picList=[]
    return render(request, "wxAccount.html",  {'groupIdList': list(groupIdListRet),'RegList': list(RegIdListRet),'picList':picList})

def wxFriendAdd(request):
    sql = """SELECT groupId FROM `wx_account_info`
                group by groupId,register_time
                ORDER BY register_time;"""
    groupIdList = mySqlUtil.getData(sql)
    groupIdListRet = [ i[0] for i in groupIdList]
    return render(request, "wxFriendAdd.html" , {'groupIdList': list(groupIdListRet)})


def wxRandomChat(request):
    return render(request, "index.html")


def wxCommentSend(request):
    return render(request, "index.html")


def friend(request):
    # return HttpResponse("hello world")
    return render(request, "friend.html")

@csrf_exempt
def AccountManage(request):
    return render(request, "user_assign.html")


@csrf_exempt
def friendData(request):
    type = common.getValue(request, 'type')
    ret = {}
    if (type == 'getFriendList'):
        ret = getFriendList(request)
    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))


def getFriendList(request):
    sql = "select a.*,b.* from wx_friend_rela a left join wx_friend_list b on a.wx_id=b.wx_id where 1=1 "
    friendList = mySqlUtil.getData(sql)
    ret = {}
    ret['friendList'] = friendList
    return ret

def queryWxInfo(request):
    pageIndex = common.getValue(request, 'pageIndex')
    pageNum = int(pageIndex)
    pageStart = (pageNum - 1) * 10
    pageEnd = pageNum * 10 -1
    sql = """SELECT wx_id,wx_name,phone_no,pword,sex,zone,signature,register_time,head_picture,groupId,client_id,devId,registrar 
              FROM `wx_account_info` limit %s,%s""" %(pageStart,pageEnd)
    accountInfoList = mySqlUtil.getData(sql)
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
             'group': info[9],
             'client_id': info[10],
             'devId': info[11],
             'registrar': info[12]}

        index=index+1

    return HttpResponse(json.dumps(retList))


def wxTaskManager(request):
    sql = """SELECT A.groupId FROM `wx_account_info` A
                join wx_auto_task B
                on (A.uuid = B.uuid)
                group by groupId;"""
    groupIdList = mySqlUtil.getData(sql)
    groupIdListRet = [ i[0] for i in groupIdList]
    file_dir = './WXCRM/static/img/headImg'
    picList =  [i[2] for i in os.walk(file_dir)][0]

    return render(request, "wxTaskManager.html",{'groupIdList': list(groupIdListRet),'picList': picList})

def chat(request):
    oper_id = request.session['oper_id']
    v = common.getValue(request, 'v')
    sql = "select object_id from wx_oper_wx where oper_id='%s' and type='0' union select wx_id from wx_account_info where wx_login_id in(select object_id from wx_oper_wx where oper_id='%s' and type='0')" % (oper_id, oper_id)
    mainWxList = mySqlUtil.getData(sql)  # 当前用户所能操作的微信主号
    if mainWxList:
        for mainWx in mainWxList:
            if mainWx[0] not in request.session['oper_main_wx']:
                request.session['oper_main_wx'].append(mainWx[0])

    if v:
        if v == 'default':
            page = "wxChart.html"
        else:
            page = "wxChart-%s.html" % v
    elif chatVersion:
        page = "wxChart-%s.html" % chatVersion
    else:
        page = "wxChart.html"
    return render(request, page)


def newcount(request):
    sql = "SELECT count(1)  FROM wx_chat_info c , wx_account_info w where c.wx_main_id=w.wx_id and w.if_start='1' " \
          "and (exists (select 1 from wx_oper_wx where type=0 and object_id=w.wx_id and oper_id='%s') " \
          "or exists (select 1 from wx_oper_wx where type=0 and object_id=w.wx_login_id and oper_id='%s'))" % \
          (request.session['oper_id'],request.session['oper_id'])
    newsList = mySqlUtil.getData(sql)
    ret = {}
    ret["newscount"] = newsList[0][0]

    if len(newsList) > 0:
        # 用于检测新号 by JMing in 20190312
        for item in request.session['oper_main_wx']:
            if 'wxid_' not in str(item):
                sql = """select wx_id from wx_account_info where wx_login_id in ('%s')""" % str(item)
                weids_list = mySqlUtil.getData(sql)
                if len(weids_list) > 0:
                    request.session['oper_main_wx'].remove(item)
                    if str(weids_list[0][0]) not in request.session['oper_main_wx']:
                        request.session['oper_main_wx'].append(str(weids_list[0][0]))

    logger.debug("session['oper_main_wx']: " + str(request.session['oper_main_wx']))

    return HttpResponse(json.dumps(ret))

@accept_websocket
def getNotice(request):

    if request.is_websocket():
        for message in request.websocket:

            try:
                oper_main_wx=request.session['oper_main_wx']

                joinStr = "','"
                mainWxStr = "'" + joinStr.join(oper_main_wx) + "'"
                sql = """select t.wx_main_id,t.wx_id,date_format(t.send_time,'%%Y-%%c-%%d %%H:%%i'),t.content, t.type
                      from wx_chat_info t
                      where  1=1  and exists (select 1 from wx_account_info w where w.if_start='1'  and wx_id=t.wx_main_id) 
                      and t.wx_main_id in (%s)
                  order by  t.wx_main_id asc,t.wx_id asc, t.send_time asc,t.createTime asc """ % mainWxStr
                chatList = mySqlUtil.getData(sql)

                wxMain = {}
                wxId = {}
                lastChartTime={}
                lastChartContent={}
                for chat in chatList:
                    if chat[0] in wxMain:
                        wxMain[chat[0]] = wxMain[chat[0]] + 1
                    else:
                        wxMain[chat[0]] = 1
                    if chat[0] in wxId:
                        if chat[1] in wxId[chat[0]]:
                            wxId[chat[0]][chat[1]] = wxId[chat[0]][chat[1]] + 1
                        else:
                            wxId[chat[0]][chat[1]] = 1
                    else:
                        wxId[chat[0]] = {chat[1]: 1}

                    if chat[0] in lastChartTime:
                        lastChartTime[chat[0]][chat[1]] = chat[2]
                        lastChartContent[chat[0]][chat[1]] = common.chartTypeTranslate(chat[3], chat[4])
                    else:
                        lastChartTime[chat[0]] = {chat[1]: chat[2]}
                        lastChartContent[chat[0]] = {chat[1]: common.chartTypeTranslate(chat[3], chat[4])}

                message = {}
                message["wxMainNotice"] = wxMain
                message["wxNotice"] = wxId
                message["heartbeat"] = {"heart": ""}
                #@的消息
                message["groupChatNoticeAtResult"] = getGroupChatNoticeAtResult(request)
                #上次聊天时间及内容
                message["lastChartTimeNotice"] = lastChartTime
                message["lastChartContentNotice"] = lastChartContent
                # 公告信息
                #message["announceNotice"] = getAnnounceNotice(request)
                #通知客户端
                request.websocket.send(json.dumps(message).encode())
                time.sleep(0.5)
            except(Exception) as e :
                logger.exception(e)
                print("socket error")
                break


def getGroupChatNoticeAtResult(request):
    message = {}
    try:
        threading.Thread(target=updateAtSession, args=(request,)).start()  #会话生成

        oper_main_wx = request.session['oper_main_wx']
        joinStr = "','"
        mainWxStr = "'" + joinStr.join(oper_main_wx) + "'"

        sql = """select * from (
                    select s.seq_id,s.wx_main_id,t.group_member_name,s.group_member_id,s.group_id,
                    (select group_name from wx_group_info where group_id=s.group_id) group_name,notice_count, 
                    date_format(t.send_time,'%%Y-%%c-%%d %%H:%%i') latest_time,ifnull(t.head_picture,s.head_picture)head_picture,
                    ifnull(t.content,'')content,t.send_type,s.type
                            from (
                            select s.seq_id,s.wx_main_id,s.group_member_name,s.group_member_id,s.group_id,s.group_name,
                             count(ci.send_time) notice_count,IFNULL(max(ci.send_time),s.send_time) send_time,s.msgId,s.head_picture,ci.type
                            from  wx_group_at_session s LEFT OUTER JOIN wx_chat_info ci
                            on ci.group_member_id = s.group_member_id 
                            and ci.wx_id= s.group_id 
                            and ci.wx_main_id= s.wx_main_id 
                            and ci.send_time >= s.send_time
                            and ci.wx_main_id in (%s)
                            where s.end_time is null and s.wx_main_id in (%s)
                            group by s.seq_id,s.wx_main_id,s.group_member_id,s.group_id 
                            having notice_count > 0
                            ) s
                            LEFT OUTER JOIN (
                            select ci.wx_main_id,ci.group_member_id,ci.group_member_name,ci.wx_id,ci.send_time,ci.head_picture,ci.content,ci.send_type from wx_chat_info ci
                            where ci.type != 4 
                            and ci.group_member_id != ''
                            and ci.group_member_id is not null 
                            and ci.wx_main_id in (%s)
                            ) t on t.wx_main_id=s.wx_main_id and t.group_member_id = s.group_member_id and t.wx_id = s.group_id and t.send_time >= s.send_time
                    order by wx_main_id,group_member_id,group_id ,t.send_time desc
                    ) g group by wx_main_id,group_member_id,group_id """ % (mainWxStr, mainWxStr, mainWxStr)
        chatListAt = mySqlUtil.getData(sql)

        if len(chatListAt) > 0:
            _chatListAt = []
            for info in chatListAt:
                nickName = info[2]
                wx_pic = info[8]

                if info[4] != '' or info[7] > 0:
                    if info[10] == '1':
                        MMIsSend = True
                    else:
                        MMIsSend = False
                chatData = {'show': True, 'NickName': info[5], 'wx_id': info[4], 'pic': wx_pic,
                            'pic_big': wx_pic, 'isTop': False, 'SendMin': info[7], 'LastChart': info[9],
                            'MMIsSend': MMIsSend, 'NoticeCount': info[6], 'RemarkName': nickName, 'isGroup': "1",
                            "notice": "", "group_wx_name": '', "state": '1', "groupOwnerId": info[3],
                            "memberNum": '', "memberName": nickName, "memberId": info[3], "chatAt": True,
                            "seq_id": info[0], "wx_main_id": info[1]}
                _chatListAt.append(chatData)
            message["chatListAt"] = _chatListAt

        wxMain = {}
        wxId = {}
        lastChartTime = {}
        lastChartContent = {}
        for chat in chatListAt:
            wxMainId = chat[1]
            key = chat[3] + '__' + chat[4]
            unitNum = chat[6]

            if wxMainId in wxMain:
                wxMain[wxMainId] = wxMain[wxMainId] + unitNum
            else:
                wxMain[wxMainId] = unitNum

            if wxMainId in wxId:
                if key in wxId[wxMainId]:
                    wxId[wxMainId][key] = wxId[wxMainId][key] + unitNum
                else:
                    wxId[wxMainId][key] = unitNum
            else:
                wxId[wxMainId] = {key: unitNum}

            if wxMainId in lastChartTime:
                lastChartTime[wxMainId][key] = chat[7]
                lastChartContent[wxMainId][key] = common.chartTypeTranslate(chat[9], chat[11])
            else:
                lastChartTime[wxMainId] = {key: chat[7]}
                lastChartContent[wxMainId] = {key: common.chartTypeTranslate(chat[9], chat[11])}

        message["wxMainNotice"] = wxMain
        message["wxNotice"] = wxId
        message["lastChartTimeNotice"] = lastChartTime
        message["lastChartContentNotice"] = lastChartContent

    except Exception as e:
        logger.error(e)

    return message


def updateAtSession(request):
    oper_main_wx = request.session['oper_main_wx']
    joinStr = "','"
    mainWxStr = "'" + joinStr.join(oper_main_wx) + "'"
    try:
        # 更新会话表
        sql = """insert into wx_group_at_session(wx_main_id,group_member_name,group_member_id,group_id,group_name,send_time,end_time,msgId,head_picture) 
                        select * from (
                        select ci.wx_main_id,ci.group_member_name,ci.group_member_id,ci.wx_id as group_id,
                        (select group_name from wx_group_info where group_id=ci.wx_id) group_name,min(ci.send_time) send_time,null end_time,ci.msgId,ci.head_picture
                        from wx_chat_info ci, wx_account_info ai
                        where ci.wx_main_id = ai.wx_id
                        and locate(CONCAT('@',ai.wx_name),ci.content)
                        and ci.type != 4 
                        and ci.group_member_id != ''
                        and ci.group_member_id is not null 
                        and ci.wx_main_id in (%s)
                        group by ci.wx_main_id,ci.wx_id,ci.group_member_id
                        ) t where not exists (select 1 from wx_group_at_session s where s.wx_main_id=t.wx_main_id and s.group_member_id = t.group_member_id and s.group_id= t.group_id and s.end_time is null)
                        """ % mainWxStr
        mySqlUtil.excSql(sql)
    except Exception as e:
        logger.error(e)


# @csrf_exempt
# def getGroupChatNotice(request):
#     groupChatNoticeAtResult={}
#     groupChatNoticeAt={} #各个群at的数量 二维json
#     chatGroupNames={}
#     chatGroupAtWxNames={}
#     chatGroupAtMsgIds={} #存每个消息的msgId，同一用户同一群@同一人只存最旧的msgId即可，因为需要合并 用于点消息时定位
#     try:
#         oper_main_wx = request.session['oper_main_wx']
#         joinStr = "','"
#         mainWxStr = "'" + joinStr.join(oper_main_wx) + "'"
#         #oper_main_wx_name = request.session['oper_main_wx_name']
#         # atStr=" content like '%@所有人%'"
#         # for wxName in oper_main_wx_name:
#         #     atStr = atStr+ " or content like '%@"+wxName+"%'"
#
#         sql=u"""select a.wx_id,a.group_id,msgId,(select group_name from wx_group_info b where b.group_id=a.group_id  limit 1) chatGroupName,
#               (select view_name from wx_group_member c where c.wx_id=a.wx_id limit 1) chatGroupAtWxName,wx_main_id,send_time from wx_group_at_info a where
#               exists (select wx_id from wx_account_info where wx_id=a.wx_main_id and if_start='1') and a.wx_main_id in (%s)
#              and (content REGEXP (select concat('@',wx_name) from wx_account_info where wx_id=a.wx_main_id  and wx_status=1 limit 1) or content REGEXP '@所有人')
#                order by wx_main_id asc,send_time asc""" % mainWxStr
#
#         atInfoList=mySqlUtil.getData(sql)
#         #print(sql)
#         if atInfoList:
#             for atInfo in atInfoList:
#                 atId=atInfo[5]+"#"+atInfo[1]+"#"+atInfo[0] #   +"#"+atInfo[2]   msgId单独传递
#                 if atId in groupChatNoticeAt:
#                     groupChatNoticeAt[atId] = groupChatNoticeAt[atId] + 1
#                 else:
#                     chatGroupAtMsgIds[atId]=atInfo[2] #只存 最旧的未读msgId
#                     groupChatNoticeAt[atId] = 1
#                     chatGroupNames[atId]=atInfo[3]
#                     chatGroupAtWxNames[atId]=atInfo[4]
#         groupChatNoticeAtResult["groupChatNoticeAt"]=groupChatNoticeAt
#         groupChatNoticeAtResult["chatGroupNames"] = chatGroupNames
#         groupChatNoticeAtResult["chatGroupAtWxNames"] = chatGroupAtWxNames
#         groupChatNoticeAtResult["chatGroupAtMsgIds"] = chatGroupAtMsgIds
#     except(Exception) as e:
#         print("getGroupChatNotice error")
#         logger.exception(e)
#     return groupChatNoticeAtResult

def getWxFlag(request):
    sql="select GROUP_CONCAT(flag_id) from wx_friend_flag where wx_id = '%s'" % common.getValue(request, 'wx_id')
    flagList = mySqlUtil.getData(sql)
    ret="";
    if len(flagList) > 0:
        ret=flagList[0][0]
    return HttpResponse(json.dumps({"flag": ret}))

def file_download(request):
    def file_iterator(file_name, chunk_size=512):
        with open(file_name,'rb+') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    file_name=common.getValue(request, 'file_name')
    response = StreamingHttpResponse(file_iterator(img_save_path + file_name))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(file_name)
    return response

def infoModifyMain(request):
    ret = {}
    ret["retStatus"] = -1
    try:
        infoaccName= request.GET.get("infoaccName")
        infoPhone = request.GET.get("infoPhone")
        infoViewName = request.GET.get("infoViewName")
        operId = request.session['oper_id']
        updateSql = """UPDATE `wx_system_operator`
                    SET `viewName` = \'%s\',
                     `phone` = \'%s\'
                    WHERE
                        `name` = \'%s\';"""%(infoViewName,infoPhone,infoaccName)
        mySqlUtil.excSql(updateSql)
        ret["retStatus"] = 1
    except(Exception) as e:
        ret["retStatus"] = -1
        logger.warn(traceback.format_exc())
    return HttpResponse(json.dumps(ret))

def infoCheck(request):
    ret = {}
    ret["retStatus"] = -2
    try:
        ret["retStatus"] = 1
        operId = request.session['oper_id']
        getInfoSql = """SELECT phone,email,create_time,viewName,name from wx_system_operator where oper_id = %s""" %(operId)
        userInfo = mySqlUtil.getData(getInfoSql)[0]
        oriPhone = userInfo[0]
        oriMail = userInfo[1]
        oriCreateTime = userInfo[2]
        oriViewName = userInfo[3]
        oriName = userInfo[4]
        ret['oriPhone'] = oriPhone
        ret['oriMail'] = oriMail
        ret['oriCreateTime'] = oriCreateTime
        ret['oriViewName'] = oriViewName
        ret['oriName'] = oriName
    except Exception as e:
        ret["retStatus"] = -2
        logger.warn(traceback.format_exc())
    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))

def pwChangeConfirm(request):
    ret = {}
    ret["retStatus"] = -1
    try:
        pwChangeOriVal = request.GET.get("pwChangeOriVal")
        pwChangeModVal = request.GET.get("pwChangeModVal")
        operId = request.session['oper_id']
        getInfoSql = """SELECT pwd from wx_system_operator
                        where oper_id = %s""" % (operId)
        userInfo = mySqlUtil.getData(getInfoSql)[0]
        pwdOri = userInfo[0]
        if pwdOri != pwChangeOriVal:
            ret["retStatus"] = -2
        else:
            updateInfoSql = """UPDATE `wx_system_operator` SET `pwd`=\'%s\' WHERE (`oper_id`=\'%s\')""" % (
                pwChangeModVal, operId)
            mySqlUtil.excSql(updateInfoSql)
            ret["retStatus"] = 1
    except Exception as e:
        ret["retStatus"] = -2
        logger.warn(traceback.format_exc())
    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))