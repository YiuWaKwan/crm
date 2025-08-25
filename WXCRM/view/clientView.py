import json
import random
import time

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import mySqlUtil
from lib.FinalLogger import getLogger
from lib.ModuleConfig import ConfAnalysis

# 初始化logger
loggerFIle = 'log/clientViews.log'
logger = getLogger(loggerFIle)
# 初始化config
configFile = 'conf/moduleConfig.conf'
confAllItems = ConfAnalysis(logger, configFile)


@csrf_exempt
def client(request):
    try:
        if request.method == 'GET':
            return render(request, 'client.html')
        else:
            if request.POST.get("pageSize") == None:
                pageSize = 10
            else:
                pageSize = request.POST.get("pageSize")
            pageNumber = request.POST.get("pageIndex")
            pageStart = (int(pageNumber) - 1) * int(pageSize)
            clause_sql = "where 1=1"
            if request.POST.get("clientId1") != None and request.POST.get("clientId1") != "":
                clientId1 = request.POST.get("clientId1").strip()
                clause_sql += " and clientId like '%" + clientId1 + "%'"
            if request.POST.get("vmName1") != None and request.POST.get("vmName1") != "":
                vmName1 = request.POST.get("vmName1").strip()
                clause_sql += " and devName like '%" + vmName1 + "%'"
            # if request.POST.get("vmIp1") != None and request.POST.get("vmIp1") != "":
            #     vmIp1 = request.POST.get("vmIp1").strip()
            #     clause_sql += " and devIp ='" + vmIp1 + "'"
            if request.POST.get("vmStatus1") != None and request.POST.get("vmStatus1") != "":
                vmStatus1 = request.POST.get("vmStatus1").strip()
                print(vmStatus1)
                if vmStatus1 == u"在线":
                    status = "1"
                else:
                    status = "0"
                clause_sql += " and status ='" + status + "'"
            sql = "select id,uuid,clientId,devId,devName,devDir,devIp,devPort,status,create_time,memu_imei," \
                  "memu_mac,memu_phone,vm_manufacturer,vm_model,telecom from wx_machine_info  " + clause_sql + " limit " \
                  + str(pageSize) + " offset " + str(pageStart) + ""
            client_list = mySqlUtil.getData(sql)
            index = 0
            result_list = {}
            pageIndex = request.POST.get("pageIndex")
            logger.info(pageIndex)
            for info in client_list:
                result_list[index] = {'itemId': info[0],
                                      'uuid': info[1],
                                      'clientId': info[2],
                                      'devId': info[3],
                                      'devName': info[4],
                                      'devDir': info[5],
                                      'devIP': info[6],
                                      'devPort': str(info[7]),
                                      'devStatus': info[8],
                                      'memu_imei': info[10],
                                      'memu_mac': info[11],
                                      "memu_phone": info[12],
                                      "vm_manufacturer": info[13],
                                      "vm_model": info[14],
                                      "telecom": info[15]
                                      }
                index = index + 1
            sql_count = "select count(*) from wx_machine_info  " + clause_sql + ""
            client_count = mySqlUtil.query_data(sql_count)
            result_list["pageCount"] = client_count[0]["count(*)"]
            return HttpResponse(json.dumps(result_list))
    except(Exception) as e:
        logger.warn(e)
    finally:
        pass


@csrf_exempt
def machineDel(request):
    itemIds = request.POST.get("itemIds")
    print(itemIds)
    try:
        sql = "update wx_machine_info set if_ready=0 where id in (" + itemIds + ")"
        logger.info("失效客户端sql：" + sql)
        mySqlUtil.excSql(sql)
        result_list = {"status": 200}
        return HttpResponse(json.dumps(result_list))
    except(Exception) as e:
        logger.error(e)
    finally:
        pass


@csrf_exempt
def machineEdit(request):
    oper_name = request.session['oper_name']
    telecom = request.POST.get("telecom")
    vm_manufacturer = request.POST.get("vm_manufacturer")
    memu_phone = request.POST.get("memu_phone")
    memu_imei = request.POST.get("memu_imei")
    memu_mac = request.POST.get("memu_mac")
    machineItemId = request.POST.get("machineItemId")
    manufacturer = ""
    model = ""
    if "|" in vm_manufacturer:
        manufacturer = vm_manufacturer.split(u"|")[0]
        model = vm_manufacturer.split(u"|")[1]

    sql = "select memu_imei,memu_mac,memu_phone,vm_manufacturer,vm_model,telecom,uuid from wx_machine_info  where id='%s'" % machineItemId
    clientInfo = mySqlUtil.getData(sql)
    if len(clientInfo) > 0:
        updateFlag = False
        if clientInfo[0][0] != memu_imei:  # memu_imei有改动
            updateFlag = True
        elif clientInfo[0][1] != memu_mac:  # memu_mac有改动
            updateFlag = True
        elif clientInfo[0][2] != memu_phone:  # memu_phone有改动
            updateFlag = True
        elif clientInfo[0][4] != model:  # vm_model有改动
            updateFlag = True
        elif clientInfo[0][5] != telecom:  # vm_model有改动
            updateFlag = True
        if updateFlag:
            taskSeq = round(time.time() * 1000 + random.randint(100, 999))
            sql = "insert into wx_task_manage(taskSeq,uuid,actionType,createTime,status,priority,operViewName)values(%d,'%s',8,now(),1,4,'%s')" % (
            taskSeq, clientInfo[0][6],oper_name)
            mySqlUtil.excSql(sql)

    sql = "update wx_machine_info set telecom='%s',vm_manufacturer='%s',memu_phone='%s',memu_imei='%s',memu_mac='%s',vm_model='%s' where id='%s' " % \
          (telecom, manufacturer, memu_phone, memu_imei, memu_mac, model, machineItemId)
    mySqlUtil.excSql(sql)
    result = {"status": 200}
    return HttpResponse(json.dumps(result))


@csrf_exempt
def getMachineDic(request):
    try:
        # 手机品牌和厂商
        sql = "SELECT name dic_name,value dic_value FROM wx_dictionary where type='vm_manufacturer' order by name"
        logger.info(sql)
        manufacturer = mySqlUtil.getData(sql)
        manufacturerList = []
        for item in manufacturer:
            manufacturerList.append({"dic_name": item[0], "dic_value": item[1]})
        # 电销运营商
        sql = "SELECT name dic_name,value dic_value FROM wx_dictionary where type='telecom'"
        logger.info(sql)
        telecom = mySqlUtil.getData(sql)
        telecomList = []
        for item in telecom:
            telecomList.append({"dic_name": item[0], "dic_value": item[1]})

        result = {}
        result["manufacturerList"] = manufacturerList
        result["telecomList"] = telecomList
        return HttpResponse(json.dumps(result))
    except(Exception) as e:
        logger.error(e)
    finally:
        pass
