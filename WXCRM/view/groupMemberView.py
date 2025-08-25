import traceback, pymysql, json, time, random, base64
import urllib.request
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import MysqlDbPool,common
from lib.DateEncoder import DateEncoder
from lib.FinalLogger import getLogger

# 初始化logger
loggerFIle = 'log/groupMemberView.log'
logger = getLogger(loggerFIle)
from django_redis import get_redis_connection

redis_con = get_redis_connection("default")
try:
    mySqlUtil=MysqlDbPool.MysqlDbPool()
except Exception as e:
    logger.error(traceback.format_exc())

@csrf_exempt
def groupMember(request):
    try:
        if(common.getValue(request,'oper') == 'getMemberInfo'): #获取成员信息+标签信息
            ret=getMemberInfo(request)
            return HttpResponse(json.dumps(ret, ensure_ascii=False, cls=DateEncoder))

        elif(common.getValue(request,'oper') == 'getDictData'): #获取成员信息+标签信息
            ret=getDictData(request)
            return HttpResponse(json.dumps(ret))

        elif (common.getValue(request, 'oper') == 'saveMemberInfoExt'):  # 获取成员信息+标签信息
            ret = saveMemberInfoExt(request)
            return HttpResponse(json.dumps(ret))

        elif (common.getValue(request, 'oper') == 'getAreaData'):  # 获取地区信息
            ret = getAreaData(request)
            return HttpResponse(json.dumps(ret))
    except(Exception) as e:
        logger.error(traceback.format_exc())

def getMemberInfo(request):
    ret = {}
    memberInfoExt={}
    memberFlags=[]
    flagIds=[]
    try:
        #wx_main_id = common.getValue(request, 'wx_main_id')
        #group_id = common.getValue(request, 'group_id')
        member_wx_id =common.getValue(request, 'member_wx_id')
        sql = """select seqId,real_name,sex,
                (select name from wx_dictionary where a.sex=value and type='sex') as sexName,
                 birthday,province,city,area,
                 (select name from wx_province where code=a.province) provinceName,
                 (select name from wx_city where code=a.city) cityName,
                 (select name from wx_area where code=a.area) areaName,address from wx_group_member_ext a where member_wx_id='%s' """ % member_wx_id
        result = mySqlUtil.getData(sql)
        if result:
            info = result[0]
            memberInfoExt = {'seqId': info[0], 'real_name': info[1], 'sex': info[2],'sexName': info[3], 'birthday': info[4], 'province': info[5],
                       'city': info[6], 'area': info[7],'areaFullName':str(info[8] or '')+" "+str(info[9] or '')+" "+str(info[10] or ''),'headPic':'','address':info[11]}
        sql ="select d.value,d.name from wx_group_member_flag c, wx_dictionary d  where c.flag_id=d.value and d.type='flag' and c.member_wx_id='%s'" % member_wx_id
        flagInfos=mySqlUtil.getData(sql)
        if flagInfos:
            for flagInfo in flagInfos:
                flag={'flagValue':flagInfo[0],'flagName':flagInfo[1]}
                flagIds.append(flagInfo[0])
                memberFlags.append(flag)
        memberInfoExt["flagIds"]=flagIds
        memberInfoExt["member_wx_id"]=member_wx_id
        ret["memberInfoExt"]=memberInfoExt;
        ret["memberFlags"]=memberFlags;
    except(Exception) as e:
        logger.error(traceback.format_exc())
    return ret

def getDictData(request):
    ret = []
    try:
        dictType=common.getValue(request,"dictType")
        sql = "select value,name from wx_dictionary where type='%s' order by seq" %dictType
        flagList = mySqlUtil.getData(sql)
        if flagList:
            for flagInfo in flagList:
                flag={'dictValue':flagInfo[0],'dictName':flagInfo[1]}
                ret.append(flag)
    except(Exception) as e:
        logger.error(traceback.format_exc())
    return ret

def saveMemberInfoExt(request):
    ret = {}
    try:
        group_id = common.getValue(request,"group_id")
        member_wx_id = common.getValue(request,"member_wx_id")
        wx_main_id = common.getValue(request,"wx_main_id")
        real_name = common.getValue(request,"real_name")
        sex = common.getValue(request,"sex")
        birthday = common.getValue(request,"birthday")
        if not birthday:
            birthday="null"
        else:
            birthday = "'"+birthday+ "'"
        province = common.getValue(request,"province")
        city = common.getValue(request,"city")
        area = common.getValue(request,"area")
        oper_id = request.session['oper_id']
        seqId = common.getValue(request,"seqId")
        flags = common.getValueList(request, 'flags')
        address = common.getValue(request,"address")
        if seqId:
            sql = "UPDATE wx_group_member_ext SET group_id = '%s', member_wx_id = '%s', wx_main_id = '%s', real_name = '%s', sex = '%s', birthday = %s, province = '%s', city = '%s', area = '%s', update_date = now(), oper_id = %s,address = '%s' WHERE seqId = %s " % (group_id, member_wx_id, wx_main_id, real_name, sex, birthday, province, city, area, oper_id,address, seqId)
        else:
            sql = "INSERT INTO wx_group_member_ext(group_id, member_wx_id, wx_main_id, real_name, sex, birthday, province, city, area, update_date, oper_id,address) VALUES ('%s', '%s', '%s', '%s', '%s', %s, '%s', '%s', '%s',now(), %d,'%s')" % (group_id, member_wx_id, wx_main_id, real_name, sex, birthday, province, city, area, oper_id,address)
        mySqlUtil.excSql(sql)

        sql = "select flag_id from wx_group_member_flag where member_wx_id='%s'" %member_wx_id
        existFlags = mySqlUtil.getData(sql)
        existArr=[]
        addFlags=[]
        delFlags=[]

        if existFlags:
            for ef in existFlags:
                existArr.append(ef[0])
            addFlags = set(flags).difference(set(existArr))
            delFlags = set(existArr).difference(set(flags))
        else:
            addFlags=flags
        if addFlags:
            sql = "INSERT INTO wx_group_member_flag(group_id, member_wx_id, wx_main_id, flag_id, flag_date, oper_id) VALUES ( %s, %s, %s, %s,now(), %s)"
            addFlagsParam = [(group_id, member_wx_id, wx_main_id, item, str(oper_id)) for item in addFlags]
            mySqlUtil.executeMany(sql, addFlagsParam)
        if delFlags:
            sql = "delete from wx_group_member_flag where member_wx_id = %s  and flag_id=%s "
            delFlagsParam = ((member_wx_id, item) for item in delFlags)
            mySqlUtil.executeMany(sql, delFlagsParam)
        ret['result'] = 1
    except(Exception) as e:
        logger.error(traceback.format_exc())
        ret['result'] = 0
    return ret

def getAreaData(request):
    ret = []
    try:
        parentCode = common.getValue(request, "parentCode")
        childName = common.getValue(request, "childName")
        parentSql=""
        if parentCode:
            parentSql=" and code_parent='%s'" %parentCode
        sql = "select code,name from %s where 1=1 %s order by name " %('wx_'+childName,parentSql)
        ret = mySqlUtil.getData(sql)
    except(Exception) as e:
        logger.error(traceback.format_exc())
    return ret