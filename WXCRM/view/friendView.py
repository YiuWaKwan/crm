import time

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from lib.ModuleConfig import ConfAnalysis
import os
import mySqlUtil
import json, common
from lib.DateEncoder import DateEncoder

from lib.FinalLogger import getLogger
# 初始化logger
loggerFIle = 'log/friendViews.log'
logger = getLogger(loggerFIle)
# 初始化config
configFile = 'conf/moduleConfig.conf'
confAllItems = ConfAnalysis(logger, configFile)
def friend(request):
    if request.method == 'GET':
        oper_id = request.session['oper_id']
        oper_name = request.session['oper_name']

    groupPerSql = """select NAME,VALUE from wx_dictionary where type='flag'"""
    groupIdList = mySqlUtil.getData(groupPerSql)
    groupIdListRet = [i for i in groupIdList]

    RegIdListRet = [oper_name]
    file_dir = './WXCRM/static/img/headImg'
    tmp_v=[i[2] for i in os.walk(file_dir)]
    if len(tmp_v)>0:
        picList = tmp_v[0]
    else:
        picList=[]

    return render(request, "friend.html",
                  {'groupIdList': list(groupIdListRet), 'RegList': list(RegIdListRet), 'picList': picList})
def friendMainIdList(request):
    if request.method == 'GET':
        wxId = request.GET.get('wxId')
    else:
        wxId = request.POST.get('wxId')
    ret={}
    ret['wxId']=wxId
    return render(request,"friendMainIdList.html",ret)
@csrf_exempt
def friendData(request):
    ret={}
    try:
        if request.method == 'GET':
            type=request.GET.get('type')
        else:
            type=request.POST.get('type')
        if(type == 'getFriendList'):
            ret=getFriendList(request)
        elif(type == 'getFlagData'):
            ret=getFlagData(request)
        elif(type == 'saveEditWxInfo'):
            ret=saveEditWxInfo(request)
        elif(type == 'getFriendMainIdList'):
            ret = getFriendMainIdList(request)
        elif(type == 'addRefreshTask'):
            ret = addRefreshTask(request)
    except(Exception) as e:
         logger.error(e)

    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))

def getFriendList(request):
    wxMainIdSearch = common.getValue(request,'wxMainIdSearch')
    friendNameSearch = common.getValue(request,'friendNameSearch')
    friendFlag = common.getValue(request, 'friendFlag')

    pageSize = common.getValue(request, "pageSize")
    pageIndex = common.getValue(request, "pageIndex")

    oper_id=request.session['oper_id']
    main_wx_str = "','".join(request.session['oper_main_wx'])

    sql = """select b.wx_id,b.wx_name,b.phone_no,b.sex,b.zone,b.signature,b.head_picture,b.qq,b.email,b.weibo,b.other_account,b.other_contacts,b.active_level,b.realname,b.description,
          (select name from wx_dictionary where b.sex=value and type='sex') as sexName,
         (select GROUP_CONCAT(DISTINCT(d.value)) as flagValues from wx_friend_flag c, wx_dictionary d  where c.flag_id=d.value and d.type='flag' and c.wx_id=b.wx_id) as flagValues,
          (select GROUP_CONCAT(DISTINCT(d.name)) as flagNames  from wx_friend_flag c, wx_dictionary d  where c.flag_id=d.value and d.type='flag' and c.wx_id=b.wx_id) as flagNames,
          (select name from wx_dictionary where b.active_level=value and type='active_level') as activeLevelName
            from wx_friend_list b where 1=1 and b.wx_id not like '%@chatroom' """

    if wxMainIdSearch.strip():
        sql = sql+""" and exists (select 1 from wx_friend_rela where wx_main_id in('%s') and wx_id=b.wx_id) """ % wxMainIdSearch
    else:
        sql = sql + """ and exists (select 1 from wx_friend_rela where wx_main_id in('%s') and wx_id=b.wx_id) """ % main_wx_str

    if friendNameSearch.strip():
        sql = sql + " and wx_name like '%"+friendNameSearch+"%'"
    if friendFlag:
        sql = sql + " and exists (select 1 from wx_friend_flag c, wx_dictionary d  where c.flag_id=d.value and d.type='flag' and c.wx_id=b.wx_id and d.value='" + friendFlag + "')"
    # logger.info(sql)
    ret = mySqlUtil.getDataByPage(sql,pageIndex,pageSize)
    return ret

def getFlagData(request):
    sql="select value,name from wx_dictionary where type='flag' order by seq"
    flagList = mySqlUtil.getData(sql)
    ret = {}
    ret['flagList'] = flagList
    return ret

def saveEditWxInfo(request):
    wxId=request.POST.get('wxId')
    realname=request.POST.get('realname')
    qq=request.POST.get('qq')
    email=request.POST.get('email')
    weibo=request.POST.get('weibo')
    otherAccount=request.POST.get('otherAccount')
    otherContacts=request.POST.get('otherContacts')
    flag=request.POST.getlist('flag')
    ret = {}
    try:
        #更新好友信息
        sql = "update wx_friend_list set realname='%s',qq='%s',email='%s',weibo='%s',other_account='%s',other_contacts='%s' where wx_id='%s'"  %(realname,qq,email,weibo,otherAccount,otherContacts,wxId)
        mySqlUtil.excSql(sql);
        ret['result'] = 1
        #更新好友标签信息

        sql="delete from wx_friend_flag where wx_id='%s'" %wxId #删除标签
        mySqlUtil.excSql(sql);
        if len(flag)>0:#插入标签
            for flagValue in flag:
                sql="INSERT INTO wx_friend_flag(wx_id,flag_id,flag_date) VALUES ('%s', '%s', CURRENT_TIMESTAMP)" %(wxId,flagValue)
                mySqlUtil.excSql(sql);

    except(Exception) as e:
        logger.error(e)
        ret['result'] = 0
    return ret

def getFriendMainIdList(request):
    ret={}
    try:
        if request.method == 'GET':
            wxId = request.GET.get('wxId')
            pageSize = request.GET.get("pageSize")
            pageIndex = request.GET.get("pageIndex")
        else:
            wxId = request.POST.get('wxId')
            pageSize = request.POST.get("pageSize")
            pageIndex = request.POST.get("pageIndex")
        sql = u"select (select b.wx_login_id from wx_account_info b where b.wx_id=a.wx_main_id),wx_id,add_time,add_type,state,source,last_chart_time,(select name from wx_dictionary where a.state=value and type='friend_state') as stateName," \
              u"(select name from wx_dictionary where a.add_type=value and type='friend_add_type') as addTypeName, " \
              u"(select name from wx_dictionary where a.source=value and type='friend_source') as sourceName, " \
              u" remark " \
              u" from wx_friend_rela a where 1=1 "
        if wxId.strip():
            sql=sql+" and wx_id='%s'" %wxId
        ret = mySqlUtil.getDataByPage(sql,pageIndex,pageSize)
    except(Exception) as e:
        logger.error(e)
    return ret

def addRefreshTask(request):
    ret={}
    try:
        oper_name = request.session['oper_name']
        if request.method == 'GET':
            wxId = request.GET.get('wxId')
        else:
            wxId = request.POST.get('wxId')
        sql = "select wx_id,uuid from wx_account_info where wx_id=(select wx_main_id from wx_friend_rela where wx_id='%s' limit 1)" %wxId
        returnData = mySqlUtil.getData(sql)
        wx_main_id=returnData[0][0]
        uuid=returnData[0][1]
        taskSeq = round(time.time() * 1000)
        mySqlUtil.excSql("insert into wx_task_manage(taskSeq,Uuid,actionType,Status,createTime,priority,operViewName)values(%d,'%s',9,1,now(),5,'%s')" % (taskSeq, uuid, oper_name))
        mySqlUtil.excSql("insert into wx_friend_refresh(taskSeq,wx_main_id,wx_friend_id)values(%d,'%s','%s')" % ( taskSeq,wx_main_id, wxId))
        ret['flag']=1
    except(Exception) as e:
        logger.error(e)
        ret['flag'] =0
    return ret