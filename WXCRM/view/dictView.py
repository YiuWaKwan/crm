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
loggerFIle = 'log/dictViews.log'
logger = getLogger(loggerFIle)
# 初始化config
configFile = 'conf/moduleConfig.conf'
confAllItems = ConfAnalysis(logger, configFile)

def dict(request):
    return render(request,"dict.html")

@csrf_exempt
def dictData(request):
    ret={}
    try:
        if request.method == 'GET':
            type=request.GET.get('type')
        else:
            type=request.POST.get('type')
        if(type == 'getDictList'):
            ret=getDictList(request)
        elif(type == 'saveDictInfo'):
            ret=saveDictInfo(request)
        elif(type == 'delDictInfo'):
            ret=delDictInfo(request)
    except(Exception) as e:
         logger.error(e)
    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))

def getDictList(request):
    if request.method == 'GET':
        typeSearch = request.GET.get('typeSearch')
        nameSearch = request.GET.get('nameSearch')
        valueSearch = request.GET.get('valueSearch')
        pageSize = request.GET.get("pageSize")
        pageIndex = request.GET.get("pageIndex")
    else:
        typeSearch = request.POST.get('typeSearch')
        nameSearch = request.POST.get('nameSearch')
        valueSearch = request.POST.get('valueSearch')
        pageSize = request.POST.get("pageSize")
        pageIndex = request.POST.get("pageIndex")
    sql = "select seq,type,name,value from wx_dictionary where 1=1"
    if typeSearch.strip():
        sql=sql+" and type like '%"+typeSearch.strip()+"%'"
    if nameSearch.strip():
        sql = sql + " and name like '%"+nameSearch.strip()+"%'"
    if valueSearch.strip():
        sql = sql + " and value like '%"+valueSearch.strip()+"%'"
    sql=sql+" order by seq desc"
    ret = mySqlUtil.getDataByPage(sql,pageIndex,pageSize)
    return ret

def saveDictInfo(request):
    ret = {}
    seq = request.POST.get('seq')
    dictType = request.POST.get('dictType')
    name = request.POST.get('name')
    value = request.POST.get('value')
    try:
        if seq.strip(): #更新
            sql = "update wx_dictionary set type='%s',name='%s',value='%s' where seq='%s'" % (dictType, name, value, seq)
            mySqlUtil.excSql(sql);
        else:#添加
            sql = "insert into wx_dictionary(type, name, value) values('%s','%s','%s')" % (dictType, name, value)
            mySqlUtil.excSql(sql);
        ret['result'] = 1
    except(Exception) as e:
        logger.error(e)
        ret['result'] = 0
    return ret

def delDictInfo(request):
    ret = {}
    itemIds = request.POST.get('itemIds')
    try:
        if itemIds.strip(): #更新
            sql = "delete from  wx_dictionary  where seq in(%s)" % (itemIds)
            mySqlUtil.excSql(sql);
        ret['result'] = 1
    except(Exception) as e:
        logger.error(e)
        ret['result'] = 0
    return ret