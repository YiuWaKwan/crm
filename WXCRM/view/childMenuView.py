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
loggerFIle = './log/childMenuViews.log'
logger = getLogger(loggerFIle)

errorFile = "./log/childMenu-error.log"
errlogger = getLogger(errorFile)
# 初始化config
configFile = 'conf/moduleConfig.conf'
confAllItems = ConfAnalysis(logger, configFile)

def sysManageMenu(request):
    if request.method == 'GET':
        parentMenu = request.GET.get('parentMenu')
    else:
        parentMenu = request.POST.get('parentMenu')
    return render(request,"sysManageMenu.html", {'parentMenu': parentMenu})

@csrf_exempt
def childMenuData(request):
    ret={}
    try:
        if request.method == 'GET':
            type=request.GET.get('type')
        else:
            type=request.POST.get('type')
        if(type == 'getChildMenus'):
            ret=getChildMenus(request)
    except(Exception) as e:
        errlogger.error(e)
    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))

def getChildMenus(request):
    ret={}
    oper_id = request.session['oper_id']
    parentMenu = request.POST.get('parentMenu')
    sql = "select menu_id,menu_name,parent_menu_id,menu_desc,menu_link,menu_order,menu_icon,(select count(menu_id) from wx_menu_info where parent_menu_id=a.menu_id) as childNum,type from wx_menu_info a where type='2' and parent_menu_id='%s'and menu_id in(select menu_id from wx_oper_menu where oper_id='%s')order by menu_order asc" % (parentMenu,oper_id)
    menuList = mySqlUtil.getData(sql)
    ret["dataList"]=menuList;
    return ret