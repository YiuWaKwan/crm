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
loggerFIle = './log/announceViews.log'
logger = getLogger(loggerFIle)

errorFile = "./log/announce-error.log"
errlogger = getLogger(errorFile)
# 初始化config
configFile = 'conf/moduleConfig.conf'
confAllItems = ConfAnalysis(logger, configFile)

def announce(request):
    return render(request,"announce.html")

@csrf_exempt
def announceData(request):
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
    sql = "select a.seq,a.content,b.name,date_format(a.create_time, '%Y-%c-%d %H:%i:%s') from wx_system_announce a left join wx_system_operator b on a.oper_id=b.oper_id where 1=1 "
    sql=sql+" and a.oper_id in(select oper_id from wx_system_operator where organization=(select organization from wx_system_operator where oper_id='"+str(oper_id)+"'))"
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
            sql = "update wx_system_announce set content='%s',oper_id='%s',create_time=now() where seq='%s'" % (content, oper_id,seq)
            mySqlUtil.excSql(sql);
        else:#添加
            sql = "insert into wx_system_announce(oper_id, create_time, content) values('%s',now(),'%s')" % (oper_id, content)
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
            sql = "delete from  wx_system_announce  where seq in(%s)" % (itemIds)
            mySqlUtil.excSql(sql);
        ret['result'] = 1
    except(Exception) as e:
        errlogger.error(e)
        ret['result'] = 0
    return ret