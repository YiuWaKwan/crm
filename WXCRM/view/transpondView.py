import random
import time

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from lib.ModuleConfig import ConfAnalysis
import os
import mySqlUtil
import json
from lib.DateEncoder import DateEncoder

from lib.FinalLogger import getLogger
# 初始化logger
loggerFIle = './log/transpondViews.log'
logger = getLogger(loggerFIle)

errorFile = "./log/transpond-error.log"
errlogger = getLogger(errorFile)
# 初始化config
configFile = 'conf/moduleConfig.conf'
confAllItems = ConfAnalysis(logger, configFile)

def transpond(request):
    oper_id = request.session['oper_id']
    sql = "select wx_name NAME,wx_id VALUE from wx_account_info where 1=1 "
    sql = sql + """ and (wx_id in( select object_id from wx_oper_wx where oper_id='%s' and type='0') or 
                     wx_login_id in(select object_id from wx_oper_wx where oper_id='%s' and type='0'))""" % (
    oper_id, oper_id)

    wxMainList = mySqlUtil.getData(sql)
    wxMainListRet = [i for i in wxMainList]

    return render(request, "transpond.html",
                  {'wxMainList': list(wxMainListRet)})

@csrf_exempt
def transpondData(request):
    ret={}
    try:
        if request.method == 'GET':
            type=request.GET.get('type')
        else:
            type=request.POST.get('type')
        if(type == 'getList'):
            ret=getList(request)
        elif(type == 'saveInfo'):
            ret=saveInfo(request)
        elif(type == 'delInfo'):
            ret=delInfo(request)
        elif(type == 'getGroupAndFriendData'):
            ret=getGroupAndFriendData(request)
    except(Exception) as e:
         logger.error(e)
    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))

def getList(request):
    if request.method == 'GET':
        wxMainIdSearch = request.GET.get('wxMainIdSearch')
        pageSize = request.GET.get("pageSize")
        pageIndex = request.GET.get("pageIndex")
    else:
        wxMainIdSearch = request.POST.get('wxMainIdSearch')
        pageSize = request.POST.get("pageSize")
        pageIndex = request.POST.get("pageIndex")
    oper_id = request.session['oper_id']
    sql = """select a.rule_id,a.group_id,(case a.isVliad when '1' then '已生效' else '未生效' end) isVliad ,(case a.state when '1' then '正常' else '已删除'  end) state ,b.head_picture,b.wx_name,c.group_name 
,a.wx_main_id,
(select GROUP_CONCAT(wx_id) from wx_transpond_rule_relation where rule_id=a.rule_id) rule_ids 
from wx_transpond_rule a left join wx_account_info b
on a.wx_main_id=b.wx_id 
left join wx_group_info c on a.group_id=c.group_id where  a.wx_main_id in (
                      select object_id from wx_oper_wx where oper_id='%s' and type='0'
                      union select wx_id from wx_account_info where wx_login_id in(select object_id from wx_oper_wx where oper_id='%s' and type='0'))""" %(oper_id,oper_id)

    if wxMainIdSearch and wxMainIdSearch.strip():
        sql=sql+" and a.wx_main_id = '"+wxMainIdSearch.strip()+"'"
    sql=sql+" order by a.rule_id desc"
    ret = mySqlUtil.getDataByPage(sql,pageIndex,pageSize)
    return ret

def saveInfo(request):
    ret = {}
    oper_id = request.session['oper_id']
    seq = request.POST.get('seq')
    wxMainId=request.POST.get('wxMainId')
    groupId=request.POST.get('groupId')
    friendWxIds=request.POST.getlist('friendWxIds')
    oper_name = request.session['oper_name']
    try:
        if seq.strip(): #更新
            sql = "update wx_transpond_rule set wx_main_id='%s',group_id='%s',isVliad='0',state='1',creator='%s',modify_time=now() where rule_id='%s'" % (wxMainId,groupId,oper_id,seq)
            mySqlUtil.excSql(sql);
            # 删除好友信息
            sql = "delete from wx_transpond_rule_relation where rule_id='%s'" % seq  # 删除标签
            mySqlUtil.excSql(sql);
        else:#添加
            seq = round(time.time() * 1000)
            sql = "insert into wx_transpond_rule(rule_id, wx_main_id, group_id,isVliad,state,creator,create_time) values('%s','%s','%s',0,1,'%s',now())" % (str(seq), wxMainId,groupId,oper_id)
            mySqlUtil.excSql(sql);

        # 插入好友信息
        if len(friendWxIds) > 0:
            for value in friendWxIds:
                sql = "INSERT INTO wx_transpond_rule_relation(rule_id,wx_id) VALUES ('%s', '%s')" % ( seq, value)
                mySqlUtil.excSql(sql);
         #插入任务
        addTask(wxMainId,oper_name)
        ret['result'] = 1

    except(Exception) as e:
        logger.error(e)
        ret['result'] = 0
    return ret

def delInfo(request):
    ret = {}
    itemIds = request.POST.get('itemIds')
    oper_name = request.session['oper_name']
    try:
        if itemIds.strip(): #更新
            sql = "update wx_transpond_rule set state='0',modify_time=now()  where rule_id in(%s)" % (itemIds)
            mySqlUtil.excSql(sql)
            # sql = "delete from  wx_transpond_rule  where rule_id in(%s)" % (itemIds)
            # mySqlUtil.excSql(sql);
            # sql = "delete from  wx_transpond_rule_relation  where rule_id in(%s)" % (itemIds)
            # mySqlUtil.excSql(sql);
            sql="select distinct wx_main_id from wx_transpond_rule  where rule_id in(%s)"  % (itemIds)
            wxMainList=mySqlUtil.getData(sql)
            if wxMainList:
                for wxMainId in wxMainList:
                    addTask(wxMainId[0],oper_name)
        ret['result'] = 1
    except(Exception) as e:
        logger.error(e)
        ret['result'] = 0
    return ret

def getGroupAndFriendData(request):
    ret = {}
    wxMainId = request.GET.get('wxMainId')
    try:
        sql="select wx_id,remark from wx_friend_rela where wx_main_id='"+wxMainId+"' and wx_id like '%@chatroom'"
        dataList = mySqlUtil.getData(sql)
        ret['groupList'] = dataList
        sql = "select wx_id,remark from wx_friend_rela where wx_main_id='" + wxMainId + "' and wx_id not like '%@chatroom'"
        friendList = mySqlUtil.getData(sql)
        ret['friendList'] = friendList
    except(Exception) as e:
        logger.error(e)
    return ret

def addTask(wxMainId,oper_name):
    # 添加任务
    taskSeq = round(time.time() * 1000 + random.randint(100, 999))
    sql = "insert into wx_task_manage(taskSeq,uuid,actionType,createTime,priority,status,operViewName) select '%s',uuid,25,now(),3,1,'%s' as operViewName from wx_account_info where wx_id='%s' " % (
        taskSeq, oper_name, wxMainId)
    mySqlUtil.excSql(sql)