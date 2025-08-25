import time
import traceback

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from lib.ModuleConfig import ConfAnalysis
import os
import mySqlUtil
import json
from lib.DateEncoder import DateEncoder

from lib.Logger import FinalLogger
# 初始化logger
loggerFIle = 'log/operViews.log'
logger = FinalLogger().getConfLogger(loggerFIle)
# 初始化config
configFile = 'conf/moduleConfig.conf'
confAllItems = ConfAnalysis(logger, configFile)

# ........... new .......... #
def oper(request):
    sql = "select menu_id,menu_name,parent_menu_id,menu_desc,menu_link,menu_order,menu_icon,(select count(menu_id) from wx_menu_info where parent_menu_id=a.menu_id) as childNum from wx_menu_info a where menu_id in(select menu_id from wx_oper_menu where (menu_id <> 2 and menu_id <> 7 and menu_id <> 9 and menu_id <> 12 and menu_id <> 16 and menu_id <> 18 and menu_id <> 13 and menu_id <> 14 and menu_id <> 19 and menu_id <> 11))order by menu_order asc"
    menuList = mySqlUtil.getData(sql)
    return render(request,"account_manage.html", {'menuList': menuList})

@csrf_exempt
def operData(request):
    ret={}
    try:
        if request.method == 'GET':
            type=request.GET.get('type')
        else:
            type=request.POST.get('type')
        if(type == 'getOperList'):
            ret=getOperList(request)

    except(Exception) as e:
         logger.error(e)
    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))

# for menu authority, we have three functions similar to oper functions#
def Menu_Data_Ban(request):
    ret = {}
    operid = request.POST.get('operid')
    sql = "select menu_id from wx_oper_menu where oper_id='%s'%(operid)"
    ToBanList = request.POST.get('BANList')
    try:
        menu_list = mySqlUtil.getData(sql)
        for menu_id in ToBanList:
            if menu_id in menu_list:
                sql = "DELETE FROM wx_oper_menu WHERE (menu_id = '%s' and oper_id = '%s')" %(menu_id,operid)
                mySqlUtil.excSql(sql)
                ret['result'] = 1;
            else:
                ret['result'] = 0;
                break;
    except(Exception) as e:
        logger.error(e)
        ret['result'] = 0;
    return ret

def Menu_Data_Start(request):
    ret = {}
    operid = request.POST.get('operid')
    sql = "select menu_id from wx_oper_menu where oper_id='%s'%(operid)"
    ToStartList = request.POST.get('StartList')
    try:
        menu_list = mySqlUtil.getData(sql)
        for menu_id in ToStartList:
            if menu_id not in menu_list:
                sql = "INSERT INTO wx_oper_menu (oper_id, menu_id, add_time,oper_account_id) VALUES ('%s', '%s', curdate(),3)" %(menu_id,operid)
                mySqlUtil.excSql(sql)
                ret['result'] = 1;
            else:
                ret['result'] = 0;
                break;
    except(Exception) as e:
        logger.error(e)
        ret['result'] = 0;
    return ret

def getOperList(request):
    # "pageIndex": pageIndex,
    # "typeSearch":$("#typeSearch").val(),
    # "nameSearch":$("#nameSearch").val(),
    # "valueSearch":$("#valueSearch").val()
    if request.method == 'GET':
        operId = request.session['oper_id']
        typeSearch = request.GET.get('typeSearch')
        nameSearch = request.GET.get('nameSearch')
        valueSearch = request.GET.get('valueSearch')
        pageSize = request.GET.get("pageSize")
        pageIndex = request.GET.get("pageIndex")
    else:
        operId = request.session['oper_id']
        typeSearch = request.POST.get('typeSearch')
        nameSearch = request.POST.get('nameSearch')
        valueSearch = request.POST.get('valueSearch')
        pageSize = request.POST.get("pageSize")
        pageIndex = request.POST.get("pageIndex")

    # sql = "select oper_id,name,phone,email,state from wx_system_operator where level = 2 and top_level_id = %s" %(operId)
    operId = request.session['oper_id']
    sql = """select oper_id,name,viewName,phone,
            (SELECT count(distinct(object_id)) from wx_oper_wx o3 where o3.oper_id = o1.oper_id),
            (select viewName from wx_system_operator o2 where o2.oper_id=o1.top_level_id),state
            from wx_system_operator o1 
            where o1.level != 1
            and o1.top_level_id = %s
            """%(operId)
    # sql = "select oper_id,name,viewName,phone,email,(select name from wx_system_operator o2 where o2.oper_id=o1.top_level_id),state " \
    #       " from wx_system_operator o1 where level = 2 "
    if typeSearch.strip():
        sql=sql+" and phone like '%"+typeSearch.strip()+"%'"
    if nameSearch.strip():
        sql = sql + " and name like '%"+nameSearch.strip()+"%'"
    if valueSearch.strip():
        sql = sql + " and email like '%"+valueSearch.strip()+"%'"
    sql=sql+" order by name asc"
    ret = mySqlUtil.getDataByPage(sql,pageIndex,pageSize)
    #print(ret)
    return ret

@csrf_exempt
def To_Creat_Task(request):
    ret = {}
    Taskid = request.POST.get('Taskid')
    TaskName = request.POST.get('TaskName')
    sql = "select Task_Id from wx_assign_task"
    TaskList = mySqlUtil.getData(sql)
    try:
        if Taskid not in TaskList:
            sql_1 = "INSERT INTO wx_assign_task (Task_id, Task_name, Master_operid, Slave_operid) VALUES ('%s', '%s', 0,0)" % (
            Taskid, TaskName)
            mySqlUtil.excSql(sql_1)
            ret['result'] = 1;
        else:
            ret['result'] = 0;
    except(Exception) as e:
        logger.error(e)
        ret['result'] = 0;
    return ret

@csrf_exempt
def To_Create_Group(request):
    ret = {}
    Master = request.POST.get('Master')
    Slave = request.POST.get('Slave')
    TaskName = request.POST.get('TaskName')
    try:
        sql_1 = "INSERT INTO wx_assign_task (Master_operid, Slave_operid) VALUES ('%s', '%s') WHERE Task_Name = '%s' " %(
        Master, Slave, TaskName)
        mySqlUtil.excSql(sql_1)
        ret['result'] = 1;
    except(Exception) as e:
        logger.error(e)
        ret['result'] = 0;
    return ret

@csrf_exempt
def operManage_ban(request):
    ret={}
    operIdList = request.POST.get('oper_id_str')
    try:
        for operid in operIdList.split('|'):
            sql = "select state from wx_system_operator where oper_id='%s'" %(operid)
            stateinfo = mySqlUtil.getData(sql)
            if stateinfo == (('1',),):
                if operIdList.strip():
                    sql = "update wx_system_operator set state ='2' where oper_id ='%s'" % operid
                    mySqlUtil.excSql(sql)
                    ret['result'] = 1;
                else:
                    ret['result'] = 0;
            else:
                ret['result'] = 0;
                break;
    except(Exception) as e:
        logger.error(e)
        ret['result'] = 0;
    return HttpResponse(json.dumps(ret))

@csrf_exempt
def operManageStart(request):
    ret={}
    ret['retStatus'] = 1
    try:
        operIdList = request.GET.get("oper_id_str")
        for operid in operIdList.split('|'):
            sql = "update wx_system_operator set state ='1' where oper_id ='%s'" %(operid)
            print(sql)
            mySqlUtil.excSql(sql)
        ret['result'] = 1
    except(Exception) as e:
        logger.error(e)
    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))

def examine(request):
    return render(request, "examine.html")

def operMenuInfo(request):
    ret = {}
    ret['retStatus'] = -1
    try:
        operPersonId = request.GET.get("operPersonId")
        operId = request.session['oper_id']
        # 获取用户当前菜单表
        operPersonMenuInfoSql = """SELECT menu_id from wx_oper_menu
                                    where oper_id = %s""" % (operPersonId)
        operPersonMenuInfo = mySqlUtil.getData(operPersonMenuInfoSql)
        if operPersonMenuInfo:
            operPersonMenuInfoList = [ i[0] for i in operPersonMenuInfo]
        else:
            operPersonMenuInfoList = []
        # 获取全部菜单表
        menuInfoSql = """SELECT parent_menu_id,menu_id,menu_name from wx_menu_info"""
        menuInfo = mySqlUtil.getData(menuInfoSql)
        menuDict = {}
        for menuItem in menuInfo:
            topMenuId = menuItem[0]
            menuId  = menuItem[1]
            menuName  = menuItem[2]
            if topMenuId not in menuDict:
                menuDict[topMenuId] = []
            if menuId in operPersonMenuInfoList:
                menuAuthStatus = 1
            else:
                menuAuthStatus = 0
            menuDict[topMenuId].append((topMenuId,menuId,menuName,menuAuthStatus))
        ret['menuInfo'] = menuDict
        ret['retStatus'] = 1
    except Exception as e:
        ret['retStatus'] = -1
        logger.warn(traceback.format_exc())
    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))

def menuAuthModify(request):
    ret = {}
    ret['retStatus'] = -1
    try:
        operPersonId = request.GET.get("operPersonId")
        menuIdList = request.GET.get("menuIdList")
        operId = request.session['oper_id']
        if menuIdList.endswith('_'):
            menuIdListHere = menuIdList[:-1].split('_')
        else:
            menuIdListHere = ""

        if menuIdListHere:
            clearMenuInfoByIdSql = """DELETE FROM wx_oper_menu WHERE oper_id =%s""" %(operPersonId)
            mySqlUtil.excSql(clearMenuInfoByIdSql)

            addMenuList = ""
            for menuItem in menuIdListHere:
                addMenuList += "(\'%s\', \'%s\', curdate(), \'%s\'),"%(operPersonId,menuItem,operId)
            addMenuListMod = addMenuList[:-1]
            addMenuInfoByIdSql = """INSERT INTO `wx_oper_menu` (`oper_id`, `menu_id`, `add_time`, `oper_account_id`) VALUES %s""" %(addMenuListMod)
            mySqlUtil.excSql(addMenuInfoByIdSql)
        else:
            clearMenuInfoByIdSql = """DELETE FROM wx_oper_menu WHERE oper_id =%s""" % (operPersonId)
            mySqlUtil.excSql(clearMenuInfoByIdSql)
        ret['retStatus'] = 1
    except Exception as e:
        logger.warn(traceback.format_exc())
    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))



def queryWxAuthInfo(request):
    ret = {}
    ret['retStatus'] = -1
    try:
        operId = request.session['oper_id']
        selectItemsId = request.GET.get('selectItemsId')
        sql="""select wx_id,wx_name,head_picture,if_start,
        (select count(1) from wx_oper_wx where object_id=s3.wx_id and oper_id='%s'),
         (select max(s2.viewName) from wx_oper_wx s1,wx_system_operator s2 where s2.oper_id=s1.oper_id and s1.object_id=s3.wx_id),
         wx_login_id
         from wx_account_info s3
         where wx_id in (
            select wx_id from wx_account_info A
                                        join wx_oper_wx B on A.wx_login_id = B.object_id
                                        where B.oper_id = %s
                                        and B.type = 0
                                        UNION
                                        select object_id from wx_oper_wx
                                        where oper_id = %s
                                        and type = 0
            )""" %(selectItemsId,operId,operId)

        accountInfoList = mySqlUtil.getData(sql)
        index = 0

        for info in accountInfoList:
            ret[index] = {'wx_id': info[0],
                              'wx_name': info[1],
                              'head_picture': info[2],
                              'if_start': info[3],
                              'wxHasAuth' : info[4],
                              'owner_name': info[5],
                              'wx_login_id' : info[6]
                          }
            index = index + 1
        #
        ret['retStatus'] = 1
    except Exception as e:
        logger.warn(traceback.format_exc())
    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))

def wxAccountAuthModify(request):
    ret = {}
    ret['retStatus'] = -1
    try:
        operId = request.session['oper_id']
        wxAccountList = request.GET.get("wxAccountList")
        selectItemsId = request.GET.get("selectItemsId")
        chkFlag = request.GET.get("chkFlag")
        logger.info((wxAccountList, selectItemsId,chkFlag))
        if int(chkFlag) == 1:
            selectItemIdClearSql = """DELETE from wx_oper_wx where oper_id = %s""" %(selectItemsId)
            mySqlUtil.excSql(selectItemIdClearSql)

        else:
            wxAccountListHere = wxAccountList[:-1].split('@')
            wxAccountDelTmp = ""
            wxAccountInsTmp = ""
            for wxAccount in wxAccountListHere:
                wxAccountDelTmp += "\'%s\'," %(wxAccount)
                wxAccountInsTmp += "(\'%s\', '0', \'%s\', curdate(), \'%s\')," %(selectItemsId,wxAccount,operId)
            wxAccountAuthDeleteCondi = "(%s)" %(wxAccountDelTmp[:-1])
            wxAccountAuthinsCondi = wxAccountInsTmp[:-1]
            deleteWxAuthSql = """delete from wx_oper_wx
                                where oper_id = %s
                                """ %(selectItemsId)
            logger.info(deleteWxAuthSql)
            mySqlUtil.excSql(deleteWxAuthSql)
            deleteWxAccountSql = """DELETE from wx_oper_wx
                                    where object_id in %s and oper_id not in (select oper_id from wx_system_operator where level=1)""" %(wxAccountAuthDeleteCondi)
            logger.info(deleteWxAccountSql)
            mySqlUtil.excSql(deleteWxAccountSql)
            insertWxAuthSql = """INSERT INTO `wx_oper_wx` (`oper_id`, `type`, `object_id`, `add_time`, `oper_account_id`) VALUES
                           %s """ %(wxAccountAuthinsCondi)
            logger.info(insertWxAuthSql)
            mySqlUtil.excSql(insertWxAuthSql)
        #
        ret['retStatus'] = 1
    except Exception as e:
        logger.warn(traceback.format_exc())
    return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))

def setManager(request):
    try:
        selectItemsId = request.GET.get("selectItemsId")
        flag = request.GET.get("flag")
        sql="update wx_system_operator set level='%s' where oper_id='%s'" % (flag, selectItemsId)
        mySqlUtil.excSql(sql)
    except Exception as e:
        logger.warn(traceback.format_exc())
    return HttpResponse(json.dumps({"code":"1"}))