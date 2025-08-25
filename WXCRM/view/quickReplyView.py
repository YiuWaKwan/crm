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
loggerFIle = './log/quickReply.log'
logger = getLogger(loggerFIle)

errlogger = "./log/quickReply-error.log"
errlogger = getLogger(errlogger)
# 初始化config
configFile = 'conf/moduleConfig.conf'
confAllItems = ConfAnalysis(logger, configFile)

def quickReply(request):
    return render(request,"quickReply.html")

@csrf_exempt
def quickReplyData(request):
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
        elif(type == 'getListJson'):
            ret=getListJson(request)
    except(Exception) as e:
        errlogger.error(e)
    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))

def getList(request):
    if request.method == 'GET':
        contentSearch = request.GET.get('contentSearch')
        pageSize = request.GET.get("pageSize")
        pageIndex = request.GET.get("pageIndex")
    else:
        contentSearch = request.POST.get('contentSearch')
        pageSize = request.POST.get("pageSize")
        pageIndex = request.POST.get("pageIndex")
    oper_id = request.session['oper_id']
    sql = "select a.seq,a.content,b.name,date_format(a.create_time, '%Y-%c-%d %H:%i:%s') from wx_quick_reply a left join wx_system_operator b on a.oper_id=b.oper_id where 1=1 and  a.oper_id='"+str(oper_id)+"'"
    if contentSearch.strip():
        sql=sql+" and a.content like '%"+contentSearch.strip()+"%'"
    sql=sql+" order by a.seq desc"
    ret = mySqlUtil.getDataByPage(sql,pageIndex,pageSize)
    return ret

def saveInfo(request):
    ret = {}
    oper_id = request.session['oper_id']
    seq = request.POST.get('seq')
    content = request.POST.get('content')
    try:
        if seq.strip(): #更新
            sql = "update wx_quick_reply set content='%s',oper_id='%s',create_time=now() where seq='%s'" % (content, oper_id,seq)
            mySqlUtil.excSql(sql);
        else:#添加
            sql = "insert into wx_quick_reply(oper_id, create_time, content) values('%s',now(),'%s')" % (oper_id, content)
            mySqlUtil.excSql(sql);
        ret['result'] = 1
    except(Exception) as e:
        errlogger.error(e)
        ret['result'] = 0
    return ret

def delInfo(request):
    ret = {}
    itemIds = request.POST.get('itemIds')
    try:
        if itemIds.strip(): #更新
            sql = "delete from  wx_quick_reply  where seq in(%s)" % (itemIds)
            mySqlUtil.excSql(sql);
        ret['result'] = 1
    except(Exception) as e:
        errlogger.error(e)
        ret['result'] = 0
    return ret

def getListJson(request):
    ret = {}
    retList = []
    try:
        oper_id = request.session['oper_id']
        sql = "select a.seq,a.content,b.name,date_format(a.create_time, '%Y-%c-%d %H:%i:%s') from wx_quick_reply a left join wx_system_operator b on a.oper_id=b.oper_id where 1=1 and  a.oper_id='"+str(oper_id)+"'  order by a.seq desc"
        dataList = mySqlUtil.getData(sql)
        for info in dataList:
            qkInfo={"seq":info[0],"content":info[1]}
            retList.append(qkInfo)
        ret["retList"]=retList
    except(Exception) as e:
        errlogger.error(e)
    return ret