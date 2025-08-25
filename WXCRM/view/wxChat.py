import traceback, pymysql, json, time, random, base64
import urllib.request
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from lib.ModuleConfig import ConfAnalysis
import MysqlDbPool, common
from lib.FinalLogger import getLogger

# 初始化logger
loggerFIle = 'log/wxChat.log'
logger = getLogger(loggerFIle)
# 初始化config
configFile = 'conf/moduleConfig.conf'
confAllItems = ConfAnalysis(logger, configFile)
imgsavepath = confAllItems.getOneOptions('img', 'imgsavepath')
fileServiceURL = confAllItems.getOneOptions('fileSystemService', 'fileServiceURL')
alarm_server = confAllItems.getOneOptions('alarm', 'alarm_server')
from django_redis import get_redis_connection


redis_con = get_redis_connection("default")
try:
    mySqlUtil=MysqlDbPool.MysqlDbPool()
except Exception as e:
    logger.error(traceback.format_exc())


def chat(request):
    return render(request, "wxChart.html", {'fileServiceURL': json.dumps(fileServiceURL)})

@csrf_exempt
def wxChatInfo(request):
    try:
        if(common.getValue(request,'oper') == 'getGroupInfo'): #获取分组及主号
            ret=getGroupInfo(request)
            return HttpResponse(json.dumps(ret))
        elif(common.getValue(request,'oper') == 'getFriendInfo'): #获取好友
            ret=getFriendInfo(request)
            return HttpResponse(json.dumps(ret))
        elif(common.getValue(request,'oper') == 'getChatAtInfo'): #获取艾特信息
            ret=getChatAtInfo(request)
            return HttpResponse(json.dumps(ret))
        elif (common.getValue(request, 'oper') == 'getWxInfo'):  # 获取艾特信息
            ret = getWxInfo(request)
            return HttpResponse(json.dumps(ret))
        elif (common.getValue(request, 'oper') == 'closeAtSession'):  # 关闭艾特会话
            ret = closeAtSession(request)
            return HttpResponse(json.dumps(ret))
        elif (common.getValue(request, 'oper') == 'saveChat'):  #保存聊天记录
            ret = saveChat(request)
            return HttpResponse(json.dumps(ret))
        elif (common.getValue(request, 'oper') == 'loadChat'):  #清理未读并且读取未读消息
            ret = loadChat(request)
            return HttpResponse(json.dumps(ret))
        elif (common.getValue(request, 'oper') == 'loadChatHis'):  #获取历史聊天记录
            ret = loadChatHis(request)
            return HttpResponse(json.dumps(ret))
        elif (common.getValue(request, 'oper') == 'getGroupMember'):  #获取群成员信息
            ret = getGroupMemberInfo(request)
            return HttpResponse(json.dumps(ret))
        elif (common.getValue(request, 'oper') == 'clearAtMsg'):  #获取群成员信息
            ret = clearAtMsg(request)
            return HttpResponse(json.dumps(ret))
        elif (common.getValue(request, 'oper') == 'transpond'):  #转发消息
            ret = transpond(request)
            return HttpResponse(json.dumps(ret))
        elif (common.getValue(request, 'oper') == 'writeAnnounceViewHis'):  # 写浏览公告信息
            ret = writeAnnounceViewHis(request)
            return HttpResponse(json.dumps(ret))
        elif (common.getValue(request, 'oper') == 'voiceRead'):  # 语音消息状态修改
            ret = voiceRead(request)
            return HttpResponse(json.dumps(ret))
        elif (common.getValue(request, 'oper') == 'downloadFile'):  # 附件下载
            ret = downloadFile(request)
            return HttpResponse(json.dumps(ret))
        elif (common.getValue(request, 'oper') == 'getTaskResult'):  # 任务结果获取
            ret = getTaskResult(request)
            return HttpResponse(json.dumps(ret))
        elif (common.getValue(request, 'oper') == 'getAnnounceNotice'):  #读公告信息
            ret = getAnnounceNotice(request)
            return HttpResponse(json.dumps(ret))
        elif (common.getValue(request, 'oper') == 'addFriend'):  # 根据个人名片添加好友或关注群
            ret = addFriend(request)
            return HttpResponse(json.dumps(ret))
        elif (common.getValue(request, 'oper') == 'joinGroup'):  # 邀请加入群
            ret = joinGroup(request)
            return HttpResponse(json.dumps(ret))
        elif (common.getValue(request, 'oper') == 'modifyWx'):  # 微信属性修改
            ret = modifyWx(request)
            return HttpResponse(ret)
        elif (common.getValue(request, 'oper') == 'clearUnread'):  #清理未读消息
            ret = clearUnread(request)
            return HttpResponse(ret)
    except(Exception) as e:
        logger.error(traceback.format_exc())


def getWxInfo(request):
    ret = {}
    wx_main_id = common.getValue(request, 'wx_main_id')
    wx_id = common.getValue(request, 'wx_id')
    member_id = common.getValue(request, 'member_id')
    try:
        isGroup = False
        if not member_id and wx_id and not '@chatroom' in wx_id: #好友
            sql  = """select fl.wx_id,fl.wx_name,IFNULL(gm.sex,fl.sex) sex,fl.zone,fl.head_picture,fr.remark,
                            gm.real_name,gm.birthday,(select name from wx_province where code=gm.province) province,
                            (select name from wx_city where code=gm.city) city,(select name from wx_area where code=gm.area) area,gm.address from wx_friend_list fl
                        LEFT OUTER JOIN wx_friend_rela fr on fr.wx_main_id = '%s' and fr.wx_id='%s' and fl.wx_id = fr.wx_id
                        LEFT OUTER JOIN wx_group_member_ext gm on gm.member_wx_id='%s' and fl.wx_id = gm.member_wx_id and gm.wx_main_id = '%s'
                        where fl.wx_id = '%s'""" % (wx_main_id, wx_id, wx_id, wx_main_id, wx_id)
            data = mySqlUtil.getData(sql)

            sql = """select DISTINCT * from (
                        select fl.flag_id,d.name from wx_friend_flag fl 
                        LEFT OUTER JOIN wx_dictionary d on d.type = 'flag' and d.value = fl.flag_id
                        where fl.wx_id = '%s'
                        union all
                        select gm.flag_id,d.name from wx_group_member_flag gm 
                        LEFT OUTER JOIN wx_dictionary d on d.type = 'flag' and d.value = gm.flag_id
                        where gm.member_wx_id = '%s' and gm.wx_main_id = '%s'
                        ) t""" % (wx_id , wx_id , wx_main_id)
            flags = mySqlUtil.getData(sql)

        if not member_id and wx_id and '@chatroom' in wx_id: #群
            sql = """select group_id,group_name,head_picture,description,create_date from wx_group_info gi where gi.group_id = '%s'""" % wx_id
            data = mySqlUtil.getData(sql)
            isGroup = True

        if member_id and wx_id and '@chatroom' in wx_id:  # 群成员
            sql = """select g.wx_id,IFNULL(g.view_name,fl.wx_name)wx_name,IFNULL(gm.sex,fl.sex) sex,fl.zone,IFNULL(g.head_picture,fl.head_picture)head_picture,'' remark,
                            gm.real_name,gm.birthday,(select name from wx_province where code=gm.province) province,
                            (select name from wx_city where code=gm.city) city,(select name from wx_area where code=gm.area) area,gm.address 
                    from wx_group_member g 
                    LEFT OUTER JOIN wx_group_member_ext gm on gm.member_wx_id='%s' and g.wx_id = gm.member_wx_id
                    LEFT OUTER JOIN wx_friend_list fl on g.wx_id='%s' and fl.wx_id = g.wx_id
                    where g.wx_id = '%s' and g.group_id = '%s' """ % (member_id, member_id, member_id, wx_id)
            data = mySqlUtil.getData(sql)

            sql = """select DISTINCT * from (
                        select fl.flag_id,d.name from wx_friend_flag fl 
                        LEFT OUTER JOIN wx_dictionary d on d.type = 'flag' and d.value = fl.flag_id
                        where fl.wx_id = '%s'
                        union all
                        select gm.flag_id,d.name from wx_group_member_flag gm 
                        LEFT OUTER JOIN wx_dictionary d on d.type = 'flag' and d.value = gm.flag_id
                        where gm.group_id = '%s' and gm.member_wx_id = '%s' and gm.wx_main_id = '%s'
                        ) t""" % (member_id, wx_id, member_id, wx_main_id)
            flags = mySqlUtil.getData(sql)

        if isGroup:
            info = data[0]
            if info:
                ret["groupInfo"] = {
                    'group_id' : info[0],
                    'group_name' : info[1],
                    'head_picture' : info[2],
                    'description' : info[3],
                    'create_date':str(info[4])
                }
        else:
            flagsTemp = []
            for flag in flags:
                flagsTemp.append({"flagValue":flag[0], "flagName":flag[1]})

            info = data[0]
              # 省 市 区县
            if not info[8]:
                p = ""
            else:
                p = info[8]
            if not info[9]:
                c = ""
            else:
                c = info[9]
            if not info[10]:
                a = ""
            else:
                a = info[10]
            if info[3]:
                zone = (info[3])
            else:
                zone = p +" "+ c +" "+ a
            if info[7]:
                bfd = str(info[7])
            else:
                bfd = ''
            sex = ['男','女','未知']
            sexName = ""
            if info[2]:
                sexName = sex[int(info[2])]
            if not sexName:
                sexName = "未知"
            if info:
                ret["customInfo"] = {
                    'pic': info[4],
                    'pic_big': info[4],
                    'NickName': info[1],
                    'remarkName': info[5],
                    'phone': '',
                    'sex': sexName,
                    'birthday': bfd,
                    'zone': zone,
                    'address': info[11],
                    'flags' : flagsTemp
                }

    except Exception as e:
        logger.error(e)

    return ret

def getGroupInfo(request):
    ret = {}
    try:
        oper_main_wx = request.session['oper_main_wx']
        joinStr = "','"
        mainWxStr = "'" + joinStr.join(oper_main_wx) + "'"
        sql = """SELECT wx_id, wx_name, phone_no, sex, zone, signature, head_picture, if_start,
                (select count(1)  from wx_chat_info c where c.wx_main_id=w.wx_id), wx_login_id FROM wx_account_info w
                where w.if_start='1' and w.wx_id in (%s)""" % mainWxStr
        accountInfoList = mySqlUtil.getData(sql)
        retList = []
        groupinfo = {}
        #retGroup = []
        for info in accountInfoList:
            accInfo = {'wx_id': info[0], 'NickName': info[1], 'phone_no': info[2], 'Sex': info[3], 'zone': info[4],
                       'signature': info[5], 'pic': info[6],
                       'pic_big': info[6], 'if_start': info[7],'NoticeCount':info[8], 'RemarkName': info[1], 'wx_login_id': info[9]}
            retList.append(accInfo)
        #     if info[7] in groupinfo:
        #         groupinfo[info[7]] = groupinfo[info[7]]+info[9]
        #     else:
        #         groupinfo[info[7]] = info[9]
        # for keys in groupinfo:
        #     retGroup.append({'groupName': keys, 'show': False,'NoticeCount':groupinfo[keys]})
        ret["retList"] = retList
        #ret["retGroup"] = retGroup
    except(Exception) as e:
        logger.error(traceback.format_exc())
    return ret


def getChatAtInfo(request):
    ret = {}
    try:
        wx_main_id = common.getValue(request, 'wx_main_id')

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
                and ci.wx_main_id='%s'
                group by ci.wx_main_id,ci.wx_id,ci.group_member_id
                ) t where not exists (select 1 from wx_group_at_session s where s.wx_main_id=t.wx_main_id and s.group_member_id = t.group_member_id and s.group_id= t.group_id and s.end_time is null)
                """ % wx_main_id
        mySqlUtil.excSql(sql)

        headHash = {}  # 标题
        chatList = []

        sql = u"""select * from (
                    select s.seq_id,s.wx_main_id,t.group_member_name,s.group_member_id,s.group_id,
                    (select group_name from wx_group_info where group_id=s.group_id) group_name,notice_count, 
                     date_format(t.send_time,'%%Y-%%c-%%d %%H:%%i') latest_time,ifnull(t.head_picture,s.head_picture)head_picture,
                     ifnull(t.content,'')content,t.send_type
                        from (
                        select s.seq_id,s.wx_main_id,s.group_member_name,s.group_member_id,s.group_id,s.group_name,
                         count(ci.send_time) notice_count,IFNULL(max(ci.send_time),s.send_time) send_time,s.msgId,s.head_picture
                        from  wx_group_at_session s LEFT OUTER JOIN wx_chat_info ci
                        on ci.group_member_id = s.group_member_id 
                        and ci.wx_id= s.group_id 
                        and ci.wx_main_id= s.wx_main_id 
                        and ci.send_time >= s.send_time
                        and ci.wx_main_id='%s'
                        where s.end_time is null and s.wx_main_id='%s'
                        group by s.seq_id,s.wx_main_id,s.group_member_id,s.group_id 
                        ) s
                        LEFT OUTER JOIN (
                        select ci.wx_main_id,ci.group_member_id,ci.group_member_name,ci.wx_id,ci.send_time,ci.head_picture,ci.content,ci.send_type from wx_chat_info ci
                        where ci.type != 4 
                        and ci.group_member_id != ''
                        and ci.group_member_id is not null 
                        and ci.wx_main_id='%s'
                        UNION ALL
                        select ci.wx_main_id,ci.group_member_id,ci.group_member_name,ci.wx_id,ci.send_time,ci.head_picture,ci.content,ci.send_type from wx_chat_info_his ci
                        where ci.type != 4 
                        and ci.group_member_id != ''
                        and ci.group_member_id is not null 
                        and ci.wx_main_id='%s'
                        ) t on t.wx_main_id=s.wx_main_id and t.group_member_id = s.group_member_id and t.wx_id = s.group_id and t.send_time >= s.send_time
                    order by wx_main_id,group_member_id,group_id ,t.send_time desc
                    ) g group by wx_main_id,group_member_id,group_id""" % (wx_main_id, wx_main_id, wx_main_id, wx_main_id)

        groupInfoList = mySqlUtil.getData(sql)
        for info in groupInfoList:
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
                        "memberNum": '', "memberName": nickName, "memberId": info[3], "chatAt": True, "seq_id": info[0]}
            chatList.append(chatData)

        ret["chatList"] = chatList
    except(Exception) as e:
        logger.error(traceback.format_exc())
    return ret


def closeAtSession(request):
    at_id = common.getValue(request, 'at_id')
    if not len(at_id):
        return
    try:
        sql = """update wx_group_at_session g set g.end_time = now()
                    ,g.resp_time = TIMESTAMPDIFF(SECOND, g.send_time ,(select min(ci.send_time)from wx_chat_info_his ci 
                    where ci.send_time >= g.send_time
                    and ci.send_time <= now()
                    and ci .send_type = '1'
                    and ci.wx_main_id = g.wx_main_id
                    and ci.wx_id = g.group_id
                    and ci.group_member_id = g.group_member_id)) 
                    ,receive_count= (select count(1) from wx_chat_info_his ci 
                    where ci.send_time >= g.send_time
                    and ci.send_time <= now()
                    and ci.wx_main_id = g.wx_main_id
                    and ci.wx_id = g.group_id
                    and ci.group_member_id = g.group_member_id
                    and ci .send_type = '1')
                    ,reply_count = (select count(1) from wx_chat_info_his ci 
                    where ci.send_time >= g.send_time
                    and ci.send_time <= now()
                    and ci.wx_main_id = g.wx_main_id
                    and ci.wx_id = g.group_id
                    and ci.group_member_id = g.group_member_id
                    and ci .send_type = '2')
                where seq_id = '%s' """ % at_id
        mySqlUtil.excSql(sql)

    except Exception as e:
        logger.error(e)

    return {'flag':True}

def getFriendInfo(request):
    ret = {}
    try:
        wx_main_id = common.getValue(request, 'wx_main_id')
        # 联系人
        sql = u"select replace(l.wx_name,' ',''),l.wx_id,date_format(r.last_chart_time,'%Y-%c-%d %H:%i'),l.signature," \
              u"l.zone,l.description,l.sex,l.head_picture,ifnull(r.last_chart_content,''),ifnull(isTop,'0'),send_type," \
              u"(select count(1) from wx_chat_info c where c.wx_main_id=r.wx_main_id and c.wx_id=r.wx_id) , ifnull(remark,'none'), r.state " \
              u" from wx_friend_rela r,wx_friend_list l where state!='4' and l.wx_id=r.wx_id and r.wx_main_id='" + wx_main_id + "'"
        #print(sql)
        friendInfoList = mySqlUtil.getData(sql)
        headHash = {}  # 标题
        chatList = []
        retlist = []
        for info in friendInfoList:
            if info[0] == '':
                continue
            remark=info[12]
            if info[12] == 'none' or len(info[12]) == 0:
                remark=info[0]
            # if ':' in remark:
            #     remark=emoji.emojize(remark)
            picture = info[7]
            if info[7] == '' or info[7] is None:
                picture='\static\img\header_none.png'
            data = {'show': True, 'NickName': info[0], 'wx_id': info[1], 'signature': info[3], 'zone': info[4],
                    'RemarkName': remark, 'Sex': info[6], 'type': '', 'pic': picture, 'pic_big': picture, 'isGroup': 0, "state": info[13]}
            if info[8] != '' or info[11] > 0:
                if info[9] == '0' :
                    isTop = False
                else:
                    isTop = True
                if info[10] == '1':
                    MMIsSend = True
                else:
                    MMIsSend = False
                chatData = {'show': True, 'NickName': info[0], 'wx_id': info[1], 'pic': picture, 'pic_big': picture,
                            'isTop': isTop, 'SendMin':  info[2], 'LastChart': info[8],
                            'MMIsSend':MMIsSend,'NoticeCount':info[11],'RemarkName':remark, 'isGroup':"0",
                            "notice": "", "group_wx_name": "", "state": info[13]}
                chatList.append(chatData)
            head = common.getPinyin(remark)
            if head in headHash:
                headHash[head].append(data)
            else:
                dataList = []
                dataList.append(data)
                headHash[head] = dataList

        # chatList加群信息 不显示群名为空的 and l.group_name !=''
        sql = u"select l.group_name,l.group_id,ifnull(date_format(r.last_chart_time,'%Y-%c-%d %H:%i'),date_format(l.create_date,'%Y-%c-%d %H:%i'))," \
              u" l.head_picture,ifnull(r.last_chart_content,''),ifnull(isTop,'0'),send_type," \
              u"(select count(1) from wx_chat_info c where c.wx_main_id=r.wx_main_id and c.wx_id=r.wx_id) ,r.state,l.wx_id," \
              u"(select count(1) from wx_group_member where group_id=l.group_id) memberNum " \
              u" from wx_friend_rela r,wx_group_info l where state!='4' and l.group_id=r.wx_id  and r.wx_main_id='" + wx_main_id + "'"

        qunDataList = []
        groupInfoList = mySqlUtil.getData(sql)
        for info in groupInfoList:
            if '@chatroom' in info[1] and info[0] == '':  # 不显示群名为空的
                continue

            remark=info[0]
            group_pic = info[3]
            if group_pic is None or group_pic == '':
                group_pic = u'\static\img\qun.jpg'
            data = {'show': True, 'NickName': remark, 'wx_id': info[1], 'signature': '', 'zone': '',
                    'RemarkName': remark, 'Sex': '', 'type': '', 'pic': group_pic, 'pic_big': group_pic,
                    'isGroup': 1, "state": info[8],"groupOwnerId":info[9],"memberNum":info[10]}

            qunDataList.append(data)

            if info[4] != '' or info[7] > 0:
                if info[5] == '0':
                    isTop = False
                else:
                    isTop = True
                if info[6] == '1':
                    MMIsSend = True
                else:
                    MMIsSend = False
            chatData = {'show': True, 'NickName': remark, 'wx_id': info[1], 'pic': group_pic,
                        'pic_big': group_pic, 'isTop': isTop, 'SendMin': info[2], 'LastChart': info[4],
                        'MMIsSend': MMIsSend, 'NoticeCount': info[7], 'RemarkName': remark, 'isGroup': "1",
                        "notice": "", "group_wx_name": info[4], "state": info[8],"groupOwnerId":info[9],"memberNum":info[10]}
            chatList.append(chatData)

        if len(qunDataList)>0:
            data = {'type': 'header', 'NickName': '群聊', 'pic': '', 'pic_big': ''}
            retlist.append(data)
            for dataitem in qunDataList:
                retlist.append(dataitem)

        if (len(headHash) > 0):
            keys = headHash.keys()
            keys = list(keys)
            keys.sort()  # 按字母排序
            for key in keys:
                data = {'type': 'header', 'NickName': key, 'pic': '', 'pic_big': ''}
                retlist.append(data)
                for dataitem in headHash[key]:
                    retlist.append(dataitem)

        ret["allContacts"] = retlist
        ret["chatList"] = chatList
    except(Exception) as e:
        logger.error(traceback.format_exc())
    return ret

def saveChat(request):
    try:
        wx_main_id = common.getValue(request, 'wx_main_id')
        wx_id = common.getValue(request, 'wx_id')
        content = common.getValue(request, 'content')
        type = common.getValue(request, 'type')
        noticeName = common.getValue(request, 'noticeName')
        noticeIdList = common.getValue(request, 'noticeIdList')
        oper_id = request.session['oper_id']
        oper_name = request.session['oper_name']
        msgId = common.getValue(request, 'msgId')
        group_member_name = common.getValue(request, 'group_member_name')
        group_member_id = common.getValue(request, 'group_member_id')
        sendChat(wx_main_id, wx_id, content, type, noticeName, False, oper_id, msgId,oper_name, group_member_name, group_member_id,noticeIdList)

    except(Exception) as e:
        logger.error(traceback.format_exc())
    return {}

def sendChat(wx_main_id, wx_id, content, type, noticeName, isTranspond,oper_id, msgId,oper_name, group_member_name, group_member_id,noticeIdList):
    try:
        sql = "select if_start from wx_account_info w where wx_id='%s' " % wx_main_id
        if_start = mySqlUtil.getData(sql)
        if if_start and len(if_start) > 0 and if_start[0][0] == 0:
            sql = "insert into wx_chat_info(wx_main_id,wx_id,send_time,type,content,send_type, msgId)" \
                  "values ('%s','%s',now(),'5','消息发送不成功，微信号已下线！','2', '%d')" \
                  % (wx_main_id, wx_id, round(time.time() * 1000 + random.randint(100, 999)))
            mySqlUtil.execSql(sql)
            return

        content = content.replace(u'<div>', '')
        content = content.replace(u'</div>', '')
        content = content.replace(u'<br>', '')

        his_content = content
        if noticeName is not None and noticeName != "":
            for name in noticeName.split(u"|"):
                his_content = "@" +name + " " +his_content #这里不是空格，是一个特殊字符，转换成unicode是\u2005
            noticeName=noticeIdList #只传需要@的wx_id
            content=his_content #完整内容，不需要去掉@name部分
        else:
            noticeName="null"
        if type == '2':
            contentInfo = his_content.split("|")
            if len(contentInfo) >= 6:
                his_content = contentInfo[5]
        createTime = int(round(time.time() * 1000))  # 发送时间的微秒时间戳
        # 写聊天历史表
        if isTranspond == False:
            sql = "insert into wx_chat_info_his(wx_main_id, wx_id,send_time,type,content,send_type,status,createTime,oper_id, msgId, group_member_name, group_member_id)" \
                  "values('%s','%s',now(),'%s','%s','1','1','%s',%d, '%s', '%s', '%s')" % (
            wx_main_id, wx_id, type, pymysql.escape_string(his_content), str(createTime),oper_id, msgId, group_member_name, group_member_id)
            mySqlUtil.excSql(sql)

        last_chart_content=content
        if type == '2':
            last_chart_content="[图片]"
            contentInfo = content.split("|")
            if len(contentInfo) >= 6:
                content = "%s|%s" % (contentInfo[0], contentInfo[5])
        elif type == '3':
            last_chart_content = "[附件]"
            contentInfo = content.split("|")
            if len(contentInfo) >= 6:
                content = "%s|%s" % (contentInfo[0], contentInfo[5])
        elif type == '6':
            last_chart_content = "[语音]"
            contentInfo = content.split("|")
            if len(contentInfo) >= 3:
                filename = contentInfo[0].split("/")
                filename = filename[-1]
                content = "%s|%s" % (filename, contentInfo[0])
            type = '3'
        elif type == '7':
            last_chart_content = "[视频]"
            contentInfo = content.split("|")
            if len(contentInfo) >= 6:
                filename = contentInfo[5].split("/")
                filename = filename[-1]
                content = "%s|%s" % (filename, contentInfo[5])

        # 写发送任务
        sql = "select r.uuid from wx_machine_info r,wx_account_info a where a.client_id=r.clientId and a.devId=r.devId and a.wx_id='%s'" % wx_main_id
        uuidList = mySqlUtil.getData(sql)
        uuid = None
        for uuidInfo in uuidList:
            uuid = uuidInfo[0]

        if uuid != None:
            taskSeq = round(time.time() * 1000 + random.randint(100, 999))
            if type in ['1', '2','3','7']:
                try:
                    sql = "select count(1) from wx_account_info w where wx_id='%s' " \
                          " and EXISTS (select 1 from wx_status_check s where s.program_type='1' and s.wx_main_id=w.wx_id and " \
                          " s.last_heartbeat_time <= date_sub(now(),interval 3 minute)) " % wx_main_id
                    health_state = mySqlUtil.getData(sql)
                    if health_state and health_state[0][0] > 0:
                        common.alarm(logger, "微信[%s]的app心跳已经停止，无法发送消息" % wx_main_id, alarm_server)
                        sql = "insert into wx_chat_info(wx_main_id,wx_id,send_time,type,content,send_type, msgId)" \
                              "values ('%s','%s',now(),'5','因网络波动等原因，目前无法发送消息，请联系管理员！','2', '%s')" \
                              % (wx_main_id, wx_id, taskSeq)
                        mySqlUtil.execSql(sql)
                        last_chart_content = "抱歉，网络开小差了，暂时无法发送消息，请稍后重试或联系系统管理员！"
                    else:
                        redis_con.publish("send_message", "%s:~:%d#^#%s#^#%s#^#%s#^#%s#^#%s"
                                          % (wx_main_id, taskSeq, wx_id, base64.b64encode(content.encode('utf-8')),
                                             noticeName, msgId, type))
                        # 添加刷新任务
                        sql = "INSERT INTO wx_task_manage(taskSeq,uuid,actionType,createTime,status,priority,operViewName, startTime)VALUES(%d, '%s', 6, now(), 2, 1, '%s', now())" % (
                            taskSeq, uuid, oper_name)
                        mySqlUtil.excSql(sql)

                        sql = "insert into wx_chat_task(taskSeq,wx_main_id,wx_id,type,content,createTime, noticeName, msgId)values(%d,'%s','%s','%s','%s','%s','%s', '%s')" % (
                            taskSeq, wx_main_id, wx_id, type, pymysql.escape_string(content), str(createTime), noticeName, msgId)
                        mySqlUtil.excSql(sql)
                except (Exception) as e:
                    logger.error(traceback.format_exc())
                    # 发送告警
                    common.alarm(logger, "redis连接不上，发送消息失败, 登录账号[%s]" % oper_name, alarm_server)
                    sql = "insert into wx_chat_info(wx_main_id,wx_id,send_time,type,content,send_type, msgId)" \
                                          "values ('%s','%s',now(),'5','网络堵塞，消息发送失败！','2', '%s')" \
                                          % (wx_main_id, wx_id, taskSeq)
                    mySqlUtil.execSql(sql)
                    last_chart_content = "网络堵塞，消息发送失败！"
            else:
                # 添加刷新任务
                sql = "INSERT INTO wx_task_manage(taskSeq,uuid,actionType,createTime,status,priority,operViewName)VALUES(%d, '%s', 6, now(), 1, 1, '%s')" % (
                    taskSeq, uuid, oper_name)
                mySqlUtil.excSql(sql)

                sql = "insert into wx_chat_task(taskSeq,wx_main_id,wx_id,type,content,createTime, noticeName, msgId)values(%d,'%s','%s','%s','%s','%s','%s', '%s')" % (
                    taskSeq, wx_main_id, wx_id, type, pymysql.escape_string(content), str(createTime), noticeName,
                    msgId)
                mySqlUtil.excSql(sql)

        #更新最后聊天内容
        sql = "update wx_friend_rela set last_chart_time=now(),last_chart_content='%s',send_type='%s' where wx_main_id='%s' and wx_id='%s'" % (
            last_chart_content, type, wx_main_id, wx_id)
        mySqlUtil.excSql(sql)
    except(Exception) as e:
        logger.error(traceback.format_exc())

def loadChat(request):
    wx_main_id = common.getValue(request, 'wx_main_id')
    wx_id = common.getValue(request, 'wx_id')
    type = common.getValue(request, 'type')
    isCurrent = common.getValue(request, 'isCurrent') #如果是当前聊天界面加载消息，为避免消息遗漏，删除时根据msgID删
    oper_id = request.session['oper_id']
    member_id = common.getValue(request, 'member_id')
    chatAt = common.getValue(request, 'chatAt')  # 艾特会话
    # 写聊天历史表 bux
    sql = """SELECT date_format(send_time,'%%Y-%%c-%%d %%H:%%i'),type,content,c.group_member_id ,c.group_member_name ,c.head_picture,c.msgId, c.send_type,c.SeqId 
           FROM wx_chat_info c 
           where c.wx_main_id='%s' and c.wx_id='%s' order by seqId  """ % (wx_main_id, wx_id)   # send_time asc,createTime asc,
    chatListdata = mySqlUtil.getData(sql)
    chatList=[]
    ret={}
    msgIDs=[]
    for info in chatListdata:
        data = setData(info)
        chatList.append(data)
        msgIDs.append(info[6])
        seqId=info[8]
        #print("loadchat:"+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))+"----"+info[2])
    #msgIDsSql = ""
    #更新最后聊天记录
    if len(chatList) > 0:#//只有查出有聊天记录才执行清除聊天记录的操作，否则在查询和删除聊天空隙有新信息进来会被移到历史表

        #sql = u"update wx_friend_rela set last_chart_time=now(),last_chart_content='%s',send_type='2' where wx_main_id='%s' and wx_id='%s'" %(chatList[len(chatList)-1]["content"],wx_main_id,wx_id)
        #mySqlUtil.excSql(sql)

        # if isCurrent == "1":
        #     joinStr = "','"
        #     joinStr = "'" + joinStr.join(msgIDs) + "'"
        #     msgIDsSql = " and msgId in(%s) " % joinStr

        ret["chatList"] = chatList

        if not chatAt:
            sql="""insert into wx_chat_info_his(wx_main_id, wx_id,send_time,type,content,send_type,status,
                      group_member_name,msgId,createTime,group_member_id,head_picture,oper_id,seqId) 
                      select wx_main_id, wx_id,send_time,type,content,send_type,status,group_member_name,msgId,createTime,
                      group_member_id,head_picture,%d,seqId from wx_chat_info 
                      where wx_main_id='%s' and wx_id='%s' and seqId<=%d""" % (oper_id,wx_main_id, wx_id,seqId)
            logger.info(sql)
            mySqlUtil.excSql(sql)
            sql="delete from wx_chat_info where wx_main_id='%s' and wx_id='%s' and seqId<=%d" % (wx_main_id, wx_id,seqId)
            logger.info(sql)
            mySqlUtil.excSql(sql)
        else :
            if member_id:
                sql="""insert into wx_chat_info_his(wx_main_id, wx_id,send_time,type,content,send_type,status,
                          group_member_name,msgId,createTime,group_member_id,head_picture,oper_id,seqId) 
                          select wx_main_id, wx_id,send_time,type,content,send_type,status,group_member_name,msgId,createTime,
                          group_member_id,head_picture,%d,seqId from wx_chat_info 
                          where wx_main_id='%s' and wx_id='%s' and group_member_id='%s' and seqId<=%d""" % (oper_id,wx_main_id, wx_id, member_id, seqId)
                logger.info(sql)
                mySqlUtil.excSql(sql)
                sql="delete from wx_chat_info where wx_main_id='%s' and wx_id='%s' and group_member_id='%s' and seqId<=%d" % (wx_main_id, wx_id,member_id, seqId)
                logger.info(sql)
                mySqlUtil.excSql(sql)
    else:
        ret["chatList"] = []
    return ret

def loadChatHis(request):
    wx_main_id = common.getValue(request, 'wx_main_id')
    wx_id = common.getValue(request, 'wx_id')
    limit_num = common.getValue(request, 'limit_num')


    # 写聊天历史表
    sql = u"select date_format(send_time,'%Y-%c-%d %H:%i'),type,content,c.group_member_id ,c.group_member_name ,c.head_picture,c.msgId ,c.send_type " \
          u" FROM wx_chat_info_his c " \
          u" where c.wx_main_id='" + wx_main_id + "' and c.wx_id='" + wx_id + "' order by send_time desc,createTime desc limit " + limit_num
    # t = time.time()
    chatListdata = mySqlUtil.getData(sql)
    # logger.debug(" ------ query chat his use : " + str(time.time()-t))
    chatList = []
    ret = {}
    for info in chatListdata:
        data = setData(info)
        chatList.append(data)
    ret["chatList"] = chatList
    return ret

#聊天信息设置
def setData(info):
    MMIsSend = True
    if info[7] == '2':
        MMIsSend = False
    picture = info[5]
    if info[5] == '' or info[5] is None:
        picture = '\static\img\header_none.png'
    group_member_name = info[4]
    message = info[2]
    data = {'MsgType': info[1], 'MMIsSend': MMIsSend, 'SendMin': info[0],
            'content': message, 'group_member_id': info[3], 'group_member_name': group_member_name,
            'headpic': picture, 'msgId': info[6]}

    if info[1] == '6':  # 语音
        if info[2] != None:
            messageInfo = info[2].split("|")
            if len(messageInfo) == 3:
                data['voiceUnRead'] = int(messageInfo[2])
                data['VoiceLength'] = messageInfo[1]
                data['content'] = messageInfo[0]

    if info[1] == '2':  # 图片
        if info[2] != None:
            messageInfo = info[2].split("|")
            if len(messageInfo) >= 2:
                data['FileStatus'] = messageInfo[1]
                data['content'] = messageInfo[0]
            else:
                data['FileStatus'] = "1" #默认不能下载原图
    if info[1] == '3' or info[1] == '7':  # 附件
        if info[2] != None:
            messageInfo = info[2].split("|")
            if len(messageInfo) >= 6:
                data['filename'] = messageInfo[0]
                data['FileExt'] = messageInfo[1]
                data['filesize'] = messageInfo[2]
                data['totallen'] = messageInfo[3]
                data['FileStatus'] = messageInfo[4]
                data['content'] = messageInfo[5]
    if info[1] == '8':#名片
        if info[2] != None:
            messageInfo = info[2].split("|")
            if len(messageInfo) >= 3:
                data['content'] = messageInfo[0]
                data['cardname'] = messageInfo[1]
                if "0" == messageInfo[2]:
                    data['VerifyFlag'] = 0
                else:
                    data['VerifyFlag'] = 1
    if info[1] == '9' or info[1] == '12':#入群邀请、连接
        if info[2] != None:
            messageInfo = info[2].split("|")
            if len(messageInfo) >= 3:
                data['content'] = messageInfo[2]
                data['title'] = messageInfo[0]
                data['des'] = messageInfo[1]
            if len(messageInfo) == 5:
                data['linkurl'] = messageInfo[4]
    if info[1] == '10':#入群邀请
        if info[2] != None:
            messageInfo = info[2].split("|")
            if len(messageInfo) == 2:
                data['content'] = messageInfo[0]
                data['location'] = messageInfo[1]
    return data

def getGroupMemberInfo(request):
    groupId = common.getValue(request, 'groupId')
    wx_main_id = common.getValue(request, 'wx_main_id')
    sql="select wx_id,view_name,(select f.head_picture from wx_friend_list f where wx_id=g.wx_id)," \
        "(select remark from wx_group_member_remark where wx_id=g.wx_id and wx_main_id='%s') from wx_group_member g where g.group_id='%s'" % (wx_main_id, groupId)
    memberListdata = mySqlUtil.getData(sql)
    memberList = []
    ret = {}
    for info in memberListdata:
        if info[3] is not None:
            memberList.append({"wx_id": info[0], "wx_name": info[3], "pic": info[2]})
        else:
            memberList.append({"wx_id":info[0],"wx_name":info[1],"pic":info[2]})
    ret["memberList"] = memberList
    return ret

def clearAtMsg(request):
    ret={}
    try:
        wxMainId = common.getValue(request, 'wxMainId')
        wxGroupId = common.getValue(request, 'wxGroupId')
        wxId = common.getValue(request, 'wxId')
        sql = "insert into wx_group_at_info_his(wx_main_id,wx_id, group_id,send_time,status,msgId,content) select wx_main_id,wx_id, group_id,send_time,1,msgId,content from wx_group_at_info where wx_main_id='%s' and group_id='%s' and wx_id='%s'" %(wxMainId,wxGroupId,wxId)
        logger.info(sql)
        mySqlUtil.excSql(sql)
        sql = "delete from wx_group_at_info where  wx_main_id='%s' and group_id='%s' and wx_id='%s'" %(wxMainId,wxGroupId,wxId)
        logger.info(sql)
        mySqlUtil.excSql(sql)

    except(Exception) as e:
        logger.error(traceback.format_exc())
    return ret

def transpond(request):
    ret = {}
    lastChartTimeNotice = {}
    lastChartContentNotice ={}

    wx_main_id = common.getValue(request, 'wx_main_id')
    target_wx_id = common.getValue(request, 'wx_id')
    target_wx_list = common.getValue(request, 'target_wx_list')
    content = common.getValue(request, 'content')
    type = common.getValue(request, 'type')
    oper_id = request.session['oper_id']
    oper_name = request.session['oper_name']
    group_member_name = common.getValue(request, 'group_member_name')
    group_member_id = common.getValue(request, 'group_member_id')
    msgId = str(round(time.time() * 1000 + random.randint(100, 999)))

    if type == '9' or type == '12' : #连接转发
        wx_id_str = target_wx_list.replace(",","','")
        contentInfo = content.split("|")
        title = ""
        if contentInfo and len(contentInfo) > 0:
           title = contentInfo[0]
        sql = "SELECT remark FROM wx_friend_rela where wx_id in ('%s') and wx_main_id='%s' " % (wx_id_str, wx_main_id)
        wxNameList = mySqlUtil.getData(sql)
        transpondName = ""
        if wxNameList and len(wxNameList) > 0:
           for name in wxNameList:
               if transpondName == "":
                   transpondName = name[0]
               else:
                   transpondName = "%s,%s" % (transpondName, name[0])

        if len(title) > 0 and len(transpondName) > 0:
            for wx_id in target_wx_list.split(","):
                # 生成读写任务
                createChatInfo(wx_main_id, wx_id, content, type, msgId)
                time.sleep(random.randint(10, 15))
                lastChartContentNotice[wx_main_id] = {wx_id: common.chartTypeTranslate(content, type)}
                lastChartTimeNotice[wx_main_id] = {wx_id: time.strftime("%Y-%m-%d %H:%M", time.localtime())}
            # 写发送任务
            taskSeq = round(time.time() * 1000 + random.randint(100, 999))
            sql = "INSERT INTO wx_task_manage(taskSeq,uuid,actionType,createTime,status,priority,operViewName) select %d, uuid, 29, now(), 1, 1,'%s' as  operViewName from wx_account_info a where a.wx_id='%s'" % (
                taskSeq, oper_name, wx_main_id)
            mySqlUtil.excSql(sql)
            sql = "insert into wx_transpond_task(taskSeq,wx_main_id,wx_id,type,content, transpondName, msgId)values(%d, '%s', '%s', '%s', '%s', '%s', '%s')" % (
                taskSeq, wx_main_id, target_wx_id, type, pymysql.escape_string(title),  transpondName, msgId)
            print(sql)
            mySqlUtil.excSql(sql)
    else:
        for wx_id in target_wx_list.split(","):
            # 生成读写任务
            createChatInfo(wx_main_id, wx_id, content, type, msgId)
            # 转发
            sendChat(wx_main_id, wx_id, content, type, "", True, oper_id, msgId, oper_name, group_member_name, group_member_id,[])
            time.sleep(random.randint(10, 15))
            lastChartContentNotice[wx_main_id] = {wx_id:common.chartTypeTranslate(content, type)}
            lastChartTimeNotice[wx_main_id] = {wx_id:time.strftime("%Y-%m-%d %H:%M", time.localtime())}

    ret["lastChartContentNotice"] = lastChartContentNotice
    ret["lastChartTimeNotice"] = lastChartTimeNotice
    return ret

def createChatInfo(wx_main_id, wx_id, content, type, msgId):
    tempContent=content
    if type == '2':
        contentInfo = content.split("|")
        if len(contentInfo) >= 6:
            tempContent = contentInfo[5]
    sql = "insert into wx_chat_info_his(wx_main_id,wx_id,send_time,type,content,createTime,send_type,msgId)values ('%s','%s',now(),'%s','%s',now(),'1','%s')"\
          % (wx_main_id, wx_id, type, pymysql.escape_string(tempContent), msgId)
    mySqlUtil.excSql(sql)

def writeAnnounceViewHis(request):
    ret={}
    try:
        seqId = common.getValue(request, 'seqId')
        operId= request.session["oper_id"]
        sql = "insert into wx_system_announce_view_his(oper_id,view_time, announce_id) values('%s',now(),%s)" %(str(operId),seqId)
        mySqlUtil.excSql(sql)
    except(Exception) as e:
        logger.error(traceback.format_exc())
    return ret

def voiceRead(request):
    """声音已读状态修改"""
    try:
        wx_main_id = common.getValue(request, 'wx_main_id')
        wx_id = common.getValue(request, 'wx_id')
        content = common.getValue(request, 'content')
        msgid = common.getValue(request, 'msgid')
        sql = "update wx_chat_info_his set content='%s' where wx_main_id='%s' and wx_id='%s' and msgid='%s'" % (content, wx_main_id, wx_id, msgid)
        mySqlUtil.excSql(sql)
    except(Exception) as e:
        logger.error(traceback.format_exc())
    return {}

def downloadFile(request):
    """附件下载状态修改"""
    try:
        wx_main_id = common.getValue(request, 'wx_main_id')
        wx_id = common.getValue(request, 'wx_id')
        wx_name = common.getValue(request, 'wx_name')
        content = common.getValue(request, 'content')
        msgid = common.getValue(request, 'msgid')
        oper_name = request.session['oper_name']
        sql = "select content,type from wx_chat_info_his where wx_main_id='%s' and wx_id='%s' and msgid='%s' and type in ('2', '3', '7')" % (
                wx_main_id, wx_id, msgid)
        msgInfo = mySqlUtil.getData(sql)

        if msgInfo is not None and len(msgInfo) > 0:
            tmpContent = msgInfo[0][0]
            tmpMessage = tmpContent.split("|")
            type = msgInfo[0][1]
            if type == '2': #下载原图
                return down_picture(wx_main_id, wx_id, wx_name, msgid, tmpMessage,oper_name)
            else: #下载文件和视频
                return down_file(wx_main_id, wx_id, wx_name, msgid, content, tmpMessage, type,oper_name)

    except(Exception) as e:
        logger.error(traceback.format_exc())

    return {"code": -1}

def down_file(wx_main_id, wx_id, wx_name, msgid, content, tmpMessage, msgtype,oper_name):
    if len(tmpMessage) >= 6:
        if tmpMessage[4] == '0' or tmpMessage[4] == '3':  # 下载或重新下载
            messageInfo = content.split("|")
            if len(messageInfo) == 6:
                if "http" in messageInfo[5]:
                    try:
                        returnObj = urllib.request.urlopen(messageInfo[5])
                        if returnObj.status == 200:
                            content = "%s|%s|%s|%s|1|%s" % (
                                messageInfo[0], messageInfo[1], messageInfo[2], messageInfo[3], messageInfo[5])
                            sql = "update wx_chat_info_his set content='%s' where wx_main_id='%s' and wx_id='%s' " \
                                  "and msgid='%s' and type in ('2', '3', '7') " % (
                                content, wx_main_id, wx_id, msgid)
                            mySqlUtil.excSql(sql)
                            return {"code": 1, "taskSeq": 0, "content": tmpMessage[5]}
                    except(Exception) as e:
                        logger.warn(e)

                taskSeq = round(time.time() * 1000 + random.randint(100, 999))

                filename = messageInfo[0]
                filesize = messageInfo[2]
                totallen = messageInfo[3]
                content = "%s|%s|%s|%s|2|%s|%s" % (
                    messageInfo[0], messageInfo[1], messageInfo[2], messageInfo[3], messageInfo[5], str(taskSeq))
                sql = "update wx_chat_info_his set content='%s' where wx_main_id='%s' and wx_id='%s' " \
                      "and msgid='%s' and type in ('2', '3', '7') " % (
                    content, wx_main_id, wx_id, msgid)
                mySqlUtil.excSql(sql)
                # 写任务记录

                type = '1'
                if msgtype == '7':
                    type = '2'
                    filenameInfo = filename.split("/")
                    filename = filenameInfo[-1]
                    filename = filename.replace("jpg", "mp4")

                sql = "INSERT INTO wx_task_manage(taskSeq,uuid,actionType,createTime,status,priority,operViewName)select %s,uuid,27,now(),1,2,'%s' as operViewName from wx_account_info where wx_id='%s'" % (
                    taskSeq,oper_name,wx_main_id)
                mySqlUtil.excSql(sql)
                sql = "INSERT INTO wx_fileLoad_task(taskSeq, objectId, objectName, fileName, viewName, volumeKbytes, volumeBytes,type,msgid,timelen)" \
                      "VALUES(%s,'%s','%s','%s','%s','%s','%s', %s, '%s','%s')" % (
                          taskSeq, wx_id, wx_name, filename, filename, filesize, totallen, type, msgid, filesize)
                mySqlUtil.excSql(sql)

                return {"code": 0, "taskSeq": taskSeq}
        elif tmpMessage[4] == '1':  # 已下载成功
            return {"code": 1, "taskSeq": 0, "content": tmpMessage[5]}
        elif tmpMessage[4] == '2':  # 下载中
            return {"code": 0, "taskSeq": tmpMessage[6]}

def down_picture(wx_main_id, wx_id, wx_name, msgid, tmpMessage,oper_name):
    try:
        #0下载 1下载成功 2下载中 3重新下载(下载失败)
        if len(tmpMessage) >= 2:
            if tmpMessage[1] == '0' or tmpMessage[1] == '3':   #下载或重新下载
                taskSeq = round(time.time() * 1000 + random.randint(100, 999))
                update_sql = "update wx_chat_info_his set content='%s|2|%d' where wx_main_id='%s' and wx_id='%s' and msgid='%s'" % (
                    tmpMessage[0], taskSeq, wx_main_id, wx_id, msgid)
                try:
                    sql = "select count(1) from wx_account_info w where wx_id='%s' " \
                          " and EXISTS (select 1 from wx_status_check s where s.program_type='1' and s.wx_main_id=w.wx_id and " \
                          " s.last_heartbeat_time <= date_sub(now(),interval 3 minute)) " % wx_main_id
                    health_state = mySqlUtil.getData(sql)
                    if health_state and health_state[0][0] > 0:
                        common.alarm(logger, "微信[%s]的app心跳已经停止，无法下载高清图" % wx_main_id, alarm_server)
                        sql = "INSERT INTO wx_task_manage(taskSeq,uuid,actionType,createTime,status,priority,operViewName) " \
                              "select %s,uuid,27,now(),3,2,'%s' as operViewName from wx_account_info where wx_id='%s'" % (
                            taskSeq, oper_name, wx_main_id)#直接写失败任务
                        mySqlUtil.excSql(sql)
                        update_sql = "update wx_chat_info_his set content='%s|3|%d' where wx_main_id='%s' and wx_id='%s' and msgid='%s'" % (
                            tmpMessage[0], taskSeq, wx_main_id, wx_id, msgid)
                        mySqlUtil.excSql(update_sql)
                    else:
                        mySqlUtil.excSql(update_sql)
                        redis_con.publish("download_picture", "%s:~:%s" % (wx_main_id, msgid))
                        # 添加下载任务
                        sql = "INSERT INTO wx_task_manage(taskSeq,uuid,actionType,createTime,status,priority,operViewName) " \
                              "select %s,uuid,27,now(),2,2,'%s' as operViewName from wx_account_info where wx_id='%s'" % (
                                  taskSeq, oper_name, wx_main_id)#直接写执行中的任务
                        mySqlUtil.excSql(sql)
                except (Exception) as e:
                    logger.error(traceback.format_exc())
                    # 发送告警
                    common.alarm(logger, "redis连接不上，下载高清图失败, 登录账号[%s]" % oper_name, alarm_server)
                return {"code": 0, "taskSeq": taskSeq}
            elif tmpMessage[1] == '1': #已下载成功
                return {"code": 1, "taskSeq": 0, "content":tmpMessage[0]}
            elif tmpMessage[1] == '2' : #下载中
                return {"code": 0, "taskSeq": tmpMessage[2]}
    except(Exception) as e:
        logger.error(traceback.format_exc())
    return {"code": -1}

def getTaskResult(request):
    try:
        taskSeq = common.getValue(request, 'taskSeq')
        wx_main_id = common.getValue(request, 'wx_main_id')
        wx_id = common.getValue(request, 'wx_id')
        msgid = common.getValue(request, 'msgid')
        sql = "select status from wx_task_manage where taskSeq=%s" % taskSeq
        statusInfo = mySqlUtil.getData(sql)
        status = 3
        content = "任务信息异常"
        if statusInfo and len(statusInfo) > 0:
            status = statusInfo[0][0]

            content="content"
            if status == 4 :
                sql = "select content from wx_chat_info_his where wx_main_id='%s' and wx_id='%s' and msgid='%s' and type in ('2', '3', '7')" % (
                    wx_main_id, wx_id, msgid)
                msgInfo = mySqlUtil.getData(sql)
                if msgInfo and len(msgInfo) > 0:
                    tmpContent = msgInfo[0][0]
                    tmpMessage = tmpContent.split("|")
                    if len(tmpMessage) >= 6:
                        content = tmpMessage[5]
                    elif len(tmpMessage) >= 2:
                        content = tmpMessage[0]

        return {"code": 0, "status": status, "content": content}
    except(Exception) as e:
        logger.error(traceback.format_exc())
        return {"code": -1}

@csrf_exempt
def getAnnounceNotice(request):
    ret={}
    try:
        operId=request.session['oper_id']
        sql="""select seq,oper_id,date_format(create_time, '%Y-%c-%d %H:%i:%s'),content from wx_system_announce a where
              oper_id in(select oper_id from wx_system_operator where organization=(select organization from wx_system_operator where oper_id='"""+str(operId)+"""'))
              and not EXISTS (select announce_id from wx_system_announce_view_his where announce_id=a.seq and oper_id='"""+str(operId)+"""')"""
        ret=mySqlUtil.getData(sql)
    except(Exception) as e:
        print("getAnnounceNotice error")
        logger.error(traceback.format_exc())
    return ret

#根据名片加好友或关注群
def addFriend(request):
    wx_main_id = common.getValue(request, 'wx_main_id')
    wx_id = common.getValue(request, 'wx_id')
    wx_name = common.getValue(request, 'wx_name')
    cardname = common.getValue(request, 'cardname')
    VerifyFlag = common.getValue(request, 'VerifyFlag')
    oper_name = request.session['oper_name']

    taskSeq = round(time.time() * 1000 + random.randint(100, 999))
    #查重
    sql = "INSERT INTO wx_task_manage(taskSeq,uuid,actionType,createTime,status,priority,operViewName)select %s,uuid,28,now(),1,2,'%s' as operViewName from wx_account_info where wx_id='%s'" % (
        taskSeq, oper_name,wx_main_id)
    mySqlUtil.excSql(sql)
    #sql = "INSERT INTO wx_fileLoad_task(taskSeq, objectId, objectName, fileName, viewName, volumeKbytes, volumeBytes,type,msgid,timelen)" \
    #      "VALUES(%s,'%s','%s','%s','%s','%s','%s', %s, '%s','%s')" % (
    #          taskSeq, wx_id, wx_name, filename, filename, filesize, totallen, type, msgid, totallen)
    mySqlUtil.excSql(sql)


#通过邀请进群
def joinGroup(request):
    try:
        wx_main_id = common.getValue(request, 'wx_main_id')
        wx_id = common.getValue(request, 'wx_id')
        wx_name = common.getValue(request, 'wx_name')
        title = common.getValue(request, 'title')
        des = common.getValue(request, 'des')
        msgid = common.getValue(request, 'msgid')
        oper_name = request.session['oper_name']
        # 查重
        taskSeq = round(time.time() * 1000 + random.randint(100, 999))
        sql = "INSERT INTO wx_task_manage(taskSeq,uuid,actionType,createTime,status,priority,operViewName)select %s,uuid,27,now(),1,2,'%s' as operViewName from wx_account_info where wx_id='%s'" % (
            taskSeq, oper_name, wx_main_id)
        mySqlUtil.excSql(sql)
        sql = "INSERT INTO wx_fileLoad_task(taskSeq, objectId, objectName, fileName, viewName, volumeKbytes, volumeBytes,type,msgid,timelen)" \
              "VALUES(%s,'%s','%s','%s','%s','0','0', 3, '%s','0')" % (
                  taskSeq, wx_id, wx_name, title, des, msgid)
        mySqlUtil.excSql(sql)
        return {"code": 0}

    except(Exception) as e:
        logger.error(traceback.format_exc())

    return {"code": -1}

def modifyWx(request):
    wx_main_id = common.getValue(request, 'wx_main_id')
    wx_id = common.getValue(request, 'wx_id')
    modify_type = common.getValue(request, 'modify_type')
    content = common.getValue(request, 'content')
    flag = common.getValue(request, 'flag')
    group_id = common.getValue(request, 'group_id')
    oper_name = request.session['oper_name']

    if "remark" == modify_type:#改备注
        sql = "select a.uuid from wx_account_info a where a.wx_id ='%s'" % wx_main_id
        wx_info = mySqlUtil.getData(sql)
        uuid = ""
        if len(wx_info) > 0:
            uuid = wx_info[0][0]

        #sql= "update wx_friend_rela set remark='%s' where wx_main_id='%s' and wx_id='%s'" % (content,wx_main_id,wx_id)
        #mySqlUtil.excSql(sql)
        taskSeq = round(time.time() * 1000 + random.randint(100, 999))
        sql = "insert into wx_task_manage(taskSeq,uuid,actionType,createTime,priority,status,operViewName)values('%s','%s',%d,now(),0,1,'%s')" % (
            taskSeq, uuid, 21, oper_name)
        mySqlUtil.excSql(sql)
        sql = "INSERT INTO wx_friend_refresh(taskSeq,wx_main_id,wx_friend_id,wx_name)VALUES(%d,'%s','%s','%s') " % ( taskSeq, wx_main_id, wx_id, content)
        mySqlUtil.excSql(sql)
    if "setTop" == modify_type:#置顶
        sql = "update wx_friend_rela set istop='1' where wx_main_id='%s' and wx_id='%s'" % (wx_main_id, wx_id)
        mySqlUtil.excSql(sql)
    if "cancelTop" == modify_type:#取消置顶
        sql = "update wx_friend_rela set istop='0' where wx_main_id='%s' and wx_id='%s'" % (wx_main_id, wx_id)
        mySqlUtil.excSql(sql)
    if "closeChat" == modify_type:#关闭聊天
        sql = "update wx_friend_rela set last_chart_time=null,last_chart_content=null where wx_main_id='%s' and wx_id='%s'" % (wx_main_id, wx_id)
        mySqlUtil.excSql(sql)
    if "setflag" == modify_type:#打标签
        sql = "select flag_id from wx_friend_flag where wx_id = '%s'" % common.getValue(request, 'wx_id')
        flagList = mySqlUtil.getData(sql)
        flag_id_dict = {};
        if len(flagList) > 0:
            for flagTuple in flagList:
                flag_id_dict[flagTuple[0]]=1;
        for flag_id in flag.split(","):
            if flag_id in flag_id_dict:
                del flag_id_dict[flag_id]
            else:
                sql = "insert into wx_friend_flag(wx_id,flag_id,flag_date)values('%s','%s',now())" % (wx_id,flag_id)
                mySqlUtil.excSql(sql)
        for key in flag_id_dict:
            sql = "delete from wx_friend_flag where wx_id='%s' and flag_id='%s'" % (wx_id, key)
            mySqlUtil.excSql(sql)
    if "group_wx_name" == modify_type:#改群名片
        sql = "select group_name,(select a.uuid from wx_account_info a where a.wx_id = g.wx_id) from wx_group_info g where group_id='%s'" % group_id
        group_info = mySqlUtil.getData(sql)
        group_name=""
        uuid = ""
        if len(group_info) > 0:
            group_name=group_info[0][0]
            uuid=group_info[0][1]

        #如果存在未开始的任务，则直接修改
        sql="select taskseq from wx_task_manage t where actionType=18 and status=1 and uuid='%s'" % uuid
        taskinfo = mySqlUtil.getData(sql)
        if len(taskinfo) > 0:
            sql="update wx_group_task set mainWxName='%s' where taskSeq='%s'" % (content,taskinfo[0][0])
            mySqlUtil.excSql(sql)
        else:
            createTask(group_id, wx_id, content, group_name, '', '', '', 18, uuid,oper_name)
    if "group_notice" == modify_type:#改群公告
        sql = "select group_name,(select a.uuid from wx_account_info a where a.wx_id = g.wx_id) from wx_group_info g where group_id='%s'" % group_id
        group_info = mySqlUtil.getData(sql)
        group_name = ""
        uuid = ""
        if len(group_info) > 0:
            group_name = group_info[0][0]
            uuid = group_info[0][1]

        # 如果存在未开始的任务，则直接修改
        sql = "select taskseq from wx_task_manage t where actionType=16 and status=1 and uuid='%s'" % uuid
        taskinfo = mySqlUtil.getData(sql)
        if len(taskinfo) > 0:
            sql = "update wx_group_task set groupNotice='%s' where taskSeq='%s'" % (content, taskinfo[0][0])
            mySqlUtil.excSql(sql)
        else:
            createTask(group_id, wx_id, '', group_name, '', content, '', 16, uuid,oper_name)

    if "add_member" == modify_type:#增加成员
        sql = "select group_name,(select a.uuid from wx_account_info a where a.wx_id = '%s') from wx_group_info g where group_id='%s'" % (wx_main_id,group_id)
        group_info = mySqlUtil.getData(sql)
        group_name = ""
        uuid = ""
        if len(group_info) > 0:
            group_name = group_info[0][0]
            uuid = group_info[0][1]

        # 如果存在未开始的任务，则直接修改
        sql = "select taskseq from wx_task_manage t where actionType in (13,14) and status in (1,2) and uuid='%s'" % uuid
        taskinfo = mySqlUtil.getData(sql)
        createTask(group_id, wx_id, '', group_name, '', '', content, 13, uuid)
    if "del_member" == modify_type:#删除成员
        sql = "select group_name,(select a.uuid from wx_account_info a where a.wx_id = '%s') from wx_group_info g where group_id='%s'" % (wx_main_id, group_id)
        group_info = mySqlUtil.getData(sql)
        group_name = ""
        uuid = ""
        if len(group_info) > 0:
            group_name = group_info[0][0]
            uuid = group_info[0][1]

        sql = "select taskseq from wx_task_manage t where actionType in (13,14) and status in (1,2) and uuid='%s'" % uuid
        taskinfo = mySqlUtil.getData(sql)
        createTask(group_id, wx_id, '', group_name, '', '', content, 14, uuid)

    if "hide_group" == modify_type:
        sql="update wx_friend_rela set state='4' where wx_main_id='%s' and wx_id='%s'" % (wx_main_id , wx_id)
        mySqlUtil.excSql(sql)

    return HttpResponse(json.dumps({"code":1}))

def createTask(group_id,wx_id,group_wx_name,group_name,groupUsage,groupNotice,friend_list,task_type,uuid,oper_name):
    taskSeq = round(time.time() * 1000 + random.randint(100, 999))
    sql = "insert into wx_task_manage(taskSeq,uuid,actionType,createTime,priority,status,operViewName)values('%s','%s',%d,now(),3,1,'%s')" % (
        taskSeq, uuid, task_type, oper_name)
    mySqlUtil.excSql(sql)
    sql = "INSERT INTO wx_group_task(taskSeq,wxId,mainWxName,groupName,friendList,groupUsage,groupNotice)VALUES" \
          "(%d,'%s','%s','%s','%s','%s','%s') " % ( taskSeq, wx_id, group_wx_name, group_name, friend_list, groupUsage, groupNotice)
    mySqlUtil.excSql(sql)


def clearUnread(request):
    wx_main_id = common.getValue(request, 'wx_main_id')
    sql="select SUBDATE(now(),interval 2 second)" #采用数据库时间，避免出现web服务器时间不对时导致功能失效
    chatTime=mySqlUtil.getData(sql)[0][0]
    operId = request.session["oper_id"]
    sql="insert into wx_chat_info_his(wx_main_id,wx_id,send_time,type,content,send_type,status,group_member_name,msgId,createTime,group_member_id,head_picture,oper_id) select wx_main_id,wx_id,send_time,type,content,send_type,status,group_member_name,msgId,createTime,group_member_id,head_picture,'%s' from wx_chat_info where wx_main_id='%s' and send_time<'%s'" %(operId,wx_main_id,chatTime)
    ret=mySqlUtil.excSql(sql)
    sql= "delete from wx_chat_info where wx_main_id='%s' and send_time<'%s'" %(wx_main_id,chatTime)
    mySqlUtil.excSql(sql)
