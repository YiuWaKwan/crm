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
loggerFIle = 'log/groupSent.log'
logger = getLogger(loggerFIle)
# 初始化config
configFile = 'conf/moduleConfig.conf'
confAllItems = ConfAnalysis(logger, configFile)


def groupSentMain(request):
    return render(request, "groupSentMain.html")


def groupSentIndex(request):
    return render(request, "groupSentIndex.html")


def groupSentCreate(request):
    return render(request, "groupSentCreate.html")


def chooseFriends(request):
    return render(request, "chooseFriends.html")


def sentDetails(request):
    return render(request, "sentDetails.html")

@csrf_exempt
def getGroupSentInfo(request):
    ret = {}
    try:
        wx_ids_query = request.POST.get("wx_ids_query")
        sent_status = request.POST.get("sent_status")
        sent_beginTime = request.POST.get("sent_beginTime")
        sent_endTIme = request.POST.get("sent_endTIme")
        key_word = request.POST.get("key_word")

        if isinstance(wx_ids_query, str) and len(wx_ids_query) > 0:
            wx_ids_query = wx_ids_query.split(",")

        pageIndex = request.POST.get("pageIndex")
        if not pageIndex:
            pageIndex = 1
        pageSize = request.POST.get("pageSize")
        if not pageSize:
            pageSize = 5
        totalCount = request.POST.get("totalCount")

        oper_main_wx = request.session['oper_main_wx']

        sql = """select pkId,wx_id,wx_name,status,content,create_time,
                    GROUP_CONCAT(sent_success) as sent_success,GROUP_CONCAT(sent_failure) as sent_failure,
                    GROUP_CONCAT(remark_failure) as remark_failure,count(sent_success) as success_count,
                     count(sent_failure) as failure_count,type,
                     GROUP_CONCAT(sent_success_id) as sent_success_id,GROUP_CONCAT(sent_failure_id) as sent_failure_id from (
                select t.seq_id as pkId,t.wx_id,case WHEN ISNULL(ai.wx_name) THEN ai.wx_login_id ELSE ai.wx_name END as wx_name,t.status,t.content,t.create_time,
                (case when tr.status = '3' THEN aa.wx_name ELSE NULL END)  as sent_success,
                (case when tr.status = '4' THEN aa.wx_name ELSE NULL END)  as sent_failure,
                (case when tr.status = '4' THEN tr.remark ELSE NULL END)  as remark_failure,t.type,
                (case when tr.status = '3' THEN CONCAT(aa.wx_id,';',aa.wx_name) ELSE NULL END)  as sent_success_id,
                (case when tr.status = '4' THEN CONCAT(aa.wx_id,';',aa.wx_name) ELSE NULL END)  as sent_failure_id
                from wx_group_sent_info t 
                LEFT OUTER JOIN wx_account_info ai on t.wx_id = ai.wx_id
                LEFT OUTER JOIN wx_group_sent_rela tr on tr.group_sent_id = t.seq_id
                LEFT OUTER JOIN (select fr.wx_main_id,fr.wx_id,case WHEN ISNULL(fr.remark) or TRIM(fr.remark)='' then fl.wx_name ELSE fr.remark END as wx_name from wx_friend_rela fr,wx_friend_list fl 
								where fr.wx_id = fl.wx_id and fr.wx_main_id in ('%s')) aa on tr.wx_id = aa.wx_id and t.wx_id = aa.wx_main_id
                where 1 = 1 and t.wx_id in ('%s')
        """ % ("','".join(oper_main_wx), "','".join(oper_main_wx))

        if(wx_ids_query and len(wx_ids_query) > 0):
            insql = ''
            for wx_id in wx_ids_query:
                insql += "'" + str(wx_id) + "',"
            insql = insql[:-1]
            sql += " and t.wx_id in (%s)" % insql
        if sent_status:
            sql += " and t.status = '%s'" % sent_status
        if sent_beginTime:
            sql += " and t.create_time > '%s'" % sent_beginTime
        if sent_endTIme:
            sql += " and t.create_time < '%s'" % sent_endTIme
        if key_word:
            sql += " and t.content like '%" + key_word + "%'"
        sql += " ) tt group by pkId,wx_id,wx_name,status,content,create_time,type order by create_time desc "

        ret["data"] = mySqlUtil.queryByPage(sql, pageIndex, pageSize, totalCount)

    except(Exception) as e:
        logger.error(e)

    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))


@csrf_exempt
def queryZone(request):
    ret = {}
    try:
        mainWxStr = "','".join(request.session['oper_main_wx'])
        sql = """select DISTINCT case WHEN ISNULL(zone) or zone=''  THEN '未知' ELSE replace(zone,' ' ,'') END as zone
                from wx_friend_list f, wx_friend_rela fr
                where 1 = 1 and f.wx_id = fr.wx_id 
                and fr.wx_main_id in ('%s')
                ORDER BY 1   
        """ % mainWxStr


        ret['data'] = mySqlUtil.getData(sql)

    except(Exception) as e:
        logger.error(e)

    return HttpResponse(json.dumps(ret))


@csrf_exempt
def queryFriends(request):
    ret = {}
    wx_main_id = request.POST.get("sent_wxId")
    friend_nickname = request.POST.get("friend_nickname")
    friend_zone = request.POST.get("friend_zone")
    friend_remark = request.POST.get("friend_remark")
    friend_flag = request.POST.get("friend_flag")

    pageIndex = request.POST.get("pageIndex")
    if not pageIndex:
        pageIndex = 1
    pageSize = request.POST.get("pageSize")
    if not pageSize:
        pageSize = 5
    totalCount = request.POST.get("totalCount")

    try:
        sql = """SELECT wx_id,wx_name,zone,remark, GROUP_CONCAT(name) as flag,head_picture from (
            select f.wx_id, case when ISNULL(fr.remark) then f.wx_name else fr.remark end as wx_name, case WHEN ISNULL(f.zone) or f.zone=''  THEN '未知' ELSE replace(f.zone,' ' ,'') END as zone,
            fr.remark, d.name, f.head_picture
            from wx_friend_list f, wx_friend_rela fr
            LEFT OUTER JOIN wx_friend_flag ff on ff.wx_id = fr.wx_id
            LEFT OUTER JOIN (select * from wx_dictionary _d where _d.type = 'flag') d on ff.flag_id = d.value 
            where 1 = 1 and f.wx_id = fr.wx_id 
            and fr.wx_main_id in ('%s')
            ) t 
            where 1 = 1
        """ % wx_main_id

        if friend_nickname:
            sql += " and wx_name like '%" + friend_nickname + "%'"
        if friend_zone:
            sql += " and zone like '%" + friend_zone + "%'"
        if friend_remark:
            sql += " and remark like '%" + friend_remark + "%'"
        if friend_flag:
            sql += " and name like '%" + friend_flag + "%'"

        sql += " GROUP BY wx_id,wx_name,zone,remark,head_picture ORDER BY 1"

        ret['data'] = mySqlUtil.queryByPage(sql, pageIndex, pageSize, totalCount)

    except Exception as e:
        logger.error(e)

    return HttpResponse(json.dumps(ret))


@csrf_exempt
def addGroupSentTask(request):
    ret = {}
    flag = True
    sent_wxId = request.POST.get("sent_wxId")
    receive_wxIds = request.POST.get("receive_wxIds")
    type = request.POST.get("type")
    content = request.POST.get("content")

    oper_name = request.session['oper_name']
    ctime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    if isinstance(receive_wxIds, str) and len(receive_wxIds) > 0:
        receive_wxIds = receive_wxIds.split(",")

    taskSeq = round(time.time() * 1000 + random.randint(100, 999))

    # 插入群发信息表
    sql = """insert into wx_group_sent_info(wx_id, status, create_time, content, type, task_seq) 
              value('%s','%s','%s','%s','%s','%d')
          """ % (sent_wxId, "1", ctime, content, type, taskSeq)
    try:
        groupSentId = mySqlUtil.insert(sql)
        if groupSentId:
            for wx_id in receive_wxIds:
                # 插入群发关系表
                sql_rela = """insert into wx_group_sent_rela(group_sent_id, wx_id, status) value('%d','%s','%s')""" % (groupSentId, wx_id, "1")
                mySqlUtil.excSql(sql_rela)

            # 下发任务
            sql = """insert into wx_task_manage(taskSeq, Uuid, actionType, Status, createTime, priority, operViewName) 
                    values(%d, (select uuid from wx_account_info where wx_id='%s'), 35 , 1 , now(), 5, '%s')
                  """ % (taskSeq, sent_wxId, oper_name)
            mySqlUtil.excSql(sql)
        else:
            flag = False
            logger.error("群发表插入失败")

    except Exception as e:
        flag = False
        logger.error(e)

    if flag:
        success_wxIds = []
        failure_wxIds = []
        failure_remarks = []
        times = -1
        while times < 600:  # 循环5600次，预计10分钟左右
            times += 1
            try:
                check = _checkTask(taskSeq)
                if check in (3, 4):
                    rdata = _getGsRelaData(groupSentId)
                    if rdata:
                        for r in rdata:
                            if r[1] == "3":
                                success_wxIds.append(r[0])
                            elif r[1] == "4":
                                failure_wxIds.append(r[0])
                                failure_remarks.append([r[2]])
                            else:
                                failure_wxIds.append(r[0])
                                failure_remarks.append("群发任务执行异常")
                                logger.warn("有异常数据")
                    break  # 微信任务执行完毕后退出循环
                time.sleep(1)  # 循环间隔为1s
            except Exception as e:
                logger.error(e)
        if not times < 600:
            flag = False
            logger.error("群发任务执行超过600秒")

    ret["flag"] = flag
    ret["success_wxIds"] = success_wxIds
    ret["failure_wxIds"] = failure_wxIds
    ret["failure_remarks"] = failure_remarks
    ret["ctime"] = ctime
    ret["groupSentId"] = groupSentId
    return HttpResponse(json.dumps(ret))


def _getGsRelaData(groupSentId):
    rt = False
    try:
        sql = """select wx_id,status,remark from wx_group_sent_rela gsr where gsr.group_sent_id = %s""" % groupSentId
        rdata = mySqlUtil.getData(sql)
        rt = rdata
    except Exception as e:
        logger.error(e)
    return rt


def _checkTask(taskSeq):
    # 检查任务是否执行完毕
    rt = False
    try:
        sql = """select status from wx_task_manage where taskSeq = %s""" % taskSeq
        rdata = mySqlUtil.getData(sql)
        rt = rdata[0][0]
    except Exception as e:
        logger.error(e)

    return rt


@csrf_exempt
def deleteSent(request):
    # 删除群发记录
    ret = {}
    flag = False
    group_sent_id = request.POST.get("group_sent_id")
    if group_sent_id:
        try:
            sql = "delete from wx_group_sent_info where seq_id = %s" % group_sent_id
            mySqlUtil.excSql(sql)

            sql = "delete from wx_group_sent_rela where group_sent_id = %s" % group_sent_id
            mySqlUtil.excSql(sql)

            flag = True
        except Exception as e:
            logger.error(e)

    ret["flag"] = flag
    return HttpResponse(json.dumps(ret))


@csrf_exempt
def sentAgain(request):
    # 再次发送
    ret = {}
    flag = False
    group_sent_id = request.POST.get("group_sent_id")
    ctime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if group_sent_id:
        try:
            taskSeq = round(time.time() * 1000 + random.randint(100, 999))
            sql = """insert into wx_group_sent_info(wx_id,status,create_time,content,type,task_seq) 
                     select wx_id,'1' as status,'%s' as create_time,content,type,%s as task_seq from wx_group_sent_info
                     where seq_id = %s """ % (ctime, taskSeq, group_sent_id)
            new_groupSentId = mySqlUtil.insert(sql)
            if new_groupSentId:
                sql = """insert into wx_group_sent_rela(group_sent_id,wx_id,status)
                         select %s as group_sent_id,wx_id,'1' as status from wx_group_sent_rela
                         where group_sent_id = %s """ % (new_groupSentId, group_sent_id)
                mySqlUtil.excSql(sql)

                oper_name = request.session['oper_name']
                # 下发任务
                sql = """insert into wx_task_manage(taskSeq, Uuid, actionType, Status, createTime, priority, operViewName) 
                                    values(%d, (select ai.uuid from wx_account_info ai,wx_group_sent_info si 
                                    where ai.wx_id=si.wx_id and si.seq_id = %s), 35 , 1 , now(), 5, '%s') """ % (taskSeq, group_sent_id, oper_name)
                mySqlUtil.excSql(sql)

                flag = True
            else:
                flag = False
                logger.error("群发，复制记录失败")

        except Exception as e:
            logger.error(e)

    if flag:
        success_wxIds = []
        failure_wxIds = []
        failure_remarks = []
        times = -1
        while times < 600:  # 循环600次，预计10分钟左右
            times += 1
            try:
                check = _checkTask(taskSeq)
                if check in (3, 4):
                    rdata = _getGsRelaData(new_groupSentId)
                    if rdata:
                        for r in rdata:
                            if r[1] == "3":
                                success_wxIds.append(r[0])
                            elif r[1] == "4":
                                failure_wxIds.append(r[0])
                                failure_remarks.append([r[2]])
                            else:
                                failure_wxIds.append(r[0])
                                failure_remarks.append("群发任务执行异常")
                                logger.warn("有异常数据")
                    break  # 微信任务执行完毕后退出循环
                time.sleep(1)  # 循环间隔为1s
            except Exception as e:
                logger.error(e)
        if not times < 600:
            flag = False
            logger.error("群发任务执行超过600秒")

    ret["flag"] = flag
    ret["success_wxIds"] = success_wxIds
    ret["failure_wxIds"] = failure_wxIds
    ret["failure_remarks"] = failure_remarks
    ret["ctime"] = ctime
    ret["group_sent_id"] = new_groupSentId
    return HttpResponse(json.dumps(ret))

@csrf_exempt
def resend(request):
    # 重新发送
    ret = {}
    flag = False
    group_sent_id = request.POST.get("group_sent_id")
    ctime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    taskSeq = round(time.time() * 1000 + random.randint(100, 999))
    if group_sent_id:
        try:

            # 修改任务状态，不能直接修改任务序列号，有防重复执行机制,需要把任务序列座变更处理
            sql = """ select task_seq from wx_group_sent_info gsi where gsi.seq_id = %s """ % group_sent_id
            old_task_seq = mySqlUtil.getData(sql)[0][0]

            sql = """update wx_group_sent_info set task_seq = %d where seq_id = %s""" % (taskSeq, group_sent_id)
            mySqlUtil.excSql(sql)

            sql = """insert into wx_task_manage(taskSeq, Uuid, actionType, Status, createTime, priority, operViewName) 
                     select %d, t.Uuid, t.actionType, 1, t.createTime, t.priority, t.operViewName from wx_task_manage t
                     where t.taskSeq = %d """ % (taskSeq, old_task_seq)
            mySqlUtil.excSql(sql)

            flag = True
        except Exception as e:
            logger.error(e)

    if flag:
        success_wxIds = []
        failure_wxIds = []
        failure_remarks = []
        times = -1
        while times < 600:  # 循环600次，预计10分钟左右
            times += 1
            try:
                check = _checkTask(taskSeq)
                if check in (3, 4):
                    rdata = _getGsRelaData(group_sent_id)
                    if rdata:
                        for r in rdata:
                            if r[1] == "3":
                                success_wxIds.append(r[0])
                            elif r[1] == "4":
                                failure_wxIds.append(r[0])
                                failure_remarks.append([r[2]])
                            else:
                                failure_wxIds.append(r[0])
                                failure_remarks.append("群发任务执行异常")
                                logger.warn("有异常数据")
                    break  # 微信任务执行完毕后退出循环
                time.sleep(1)  # 循环间隔为1s
            except Exception as e:
                logger.error(e)
        if not times < 600:
            flag = False
            logger.error("群发任务执行超过600秒")

    ret["flag"] = flag
    ret["success_wxIds"] = success_wxIds
    ret["failure_wxIds"] = failure_wxIds
    ret["failure_remarks"] = failure_remarks
    ret["ctime"] = ctime
    ret["group_sent_id"] = group_sent_id
    return HttpResponse(json.dumps(ret))







