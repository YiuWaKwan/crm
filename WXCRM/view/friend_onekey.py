import datetime
import math
import random
import threading
import traceback

import time
import uuid

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from lib.FinalLogger import getLogger
from lib.ModuleConfig import ConfAnalysis
import os
import mySqlUtil
import json
from lib.DateEncoder import DateEncoder



BASEDIR = os.getcwd()

# 初始化logger
logger = getLogger('./log/friend_onekey.log')
# 初始化config
configFile = 'conf/moduleConfig.conf'
confAllItems = ConfAnalysis(logger, configFile)

def friend_onekey(request):
    if(request.method=='GET'):
        return render(request, 'friend_onekey.html')

@csrf_exempt
def friend_sum(request):
    ret={}
    #粉丝规模
    sql="""select count(1) as f_sum FROM OKAY_USER_ADDRESS_BOOK"""
    statData = mySqlUtil.getDictData(sql)
    return HttpResponse(json.dumps(statData))

@csrf_exempt
#获取正在进行的任务列表
def get_tasklist_ing(request):
    ret={}
    #正在进行的任务
    try:
        oper_id = request.session['oper_id']
        sql = """select a.task_id,a.task_name,b.wx_login_id as wx_user,a.filter_fact,b.head_picture,b.wx_name,d.f_count,ifnull(m_count,0) m_count,
                case when d.f_count=0 then 0 else format(ifnull(m_count,0)/a.filter_fact*100,1) end as sum_count,ifnull(success_count,0) success_count,a.task_state
                from OKAY_TASK_INFO a
                inner join wx_account_info b on a.WX_USER=b.wx_id
                inner join OKAY_TASK_INFO_INDEX c on a.task_id=c.task_id
                left join (select a.wx_main_id,count(1) f_count from wx_friend_rela a,wx_friend_list b where a.wx_id=b.wx_id  group by a.wx_main_id) d on a.WX_USER=d.wx_main_id
                left join (SELECT task_id,count(1) m_count from OKAY_TASK_LIST where TASK_SEQ_FLAG='2' group by task_id) e on a.TASK_ID=e.task_id
                left join (
                    select b.task_id,c.wx_main_id,count(1) success_count from OKAY_TASK_INFO a
                    inner join OKAY_TASK_LIST b on a.TASK_ID=b.TASK_ID
                    inner join wx_friend_rela c on a.WX_USER=c.wx_main_id 
                        and case when IFNULL(b.TARGET_WX_ID,'')<>'' then b.TARGET_WX_ID else b.TARGET_WX_NAME end =
                                case when IFNULL(b.TARGET_WX_ID,'')<>'' then c.wx_id else c.remark end
                        and b.TARGET_WX_NAME <>'' and b.TARGET_WX_NAME is not null
                    where b.SEND_CODE='1' and b.TASK_SEQ_FLAG='2' and date_format(c.add_time,'%%Y%%m%%d%%H%%i%%s')>a.create_time
                    group by b.task_id,c.wx_main_id
                ) f on a.TASK_ID=f.task_id and a.WX_USER=f.wx_main_id 
                where a.task_state=1 and c.HUILIAO_USER=%s order by a.create_time desc""" % (oper_id)
        statData = mySqlUtil.getDictData(sql)
    except :
        logger.warn(traceback.format_exc())
        statData='fail'
    # print (statData)
    return HttpResponse(json.dumps(statData))

@csrf_exempt
#获取暂停的任务列表
def get_tasklist_pause(request):
    ret={}
    #正在暂停的任务
    try:
        oper_id = request.session['oper_id']
        sql = """select a.task_id,a.task_name,b.wx_login_id as wx_user,a.filter_fact,b.head_picture,b.wx_name,d.f_count,ifnull(m_count,0) m_count,
                case when d.f_count=0 then 0 else format(ifnull(m_count,0)/a.filter_fact*100,1) end as sum_count,ifnull(success_count,0) success_count,a.task_state
                from OKAY_TASK_INFO a
                inner join wx_account_info b on a.WX_USER=b.wx_id
                inner join OKAY_TASK_INFO_INDEX c on a.task_id=c.task_id
                left join (select a.wx_main_id,count(1) f_count from wx_friend_rela a,wx_friend_list b where a.wx_id=b.wx_id  group by a.wx_main_id) d on a.WX_USER=d.wx_main_id
                left join (SELECT task_id,count(1) m_count from OKAY_TASK_LIST where TASK_SEQ_FLAG='2' group by task_id) e on a.TASK_ID=e.task_id
                left join (
                    select b.task_id,c.wx_main_id,count(1) success_count from OKAY_TASK_INFO a
                    inner join OKAY_TASK_LIST b on a.TASK_ID=b.TASK_ID
                    inner join wx_friend_rela c on a.WX_USER=c.wx_main_id 
                        and case when IFNULL(b.TARGET_WX_ID,'')<>'' then b.TARGET_WX_ID else b.TARGET_WX_NAME end =
                                case when IFNULL(b.TARGET_WX_ID,'')<>'' then c.wx_id else c.remark end
                        and b.TARGET_WX_NAME <>'' and b.TARGET_WX_NAME is not null
                    where b.SEND_CODE='1' and b.TASK_SEQ_FLAG='2' and date_format(c.add_time,'%%Y%%m%%d%%H%%i%%s')>a.create_time
                    group by b.task_id,c.wx_main_id
                ) f on a.TASK_ID=f.task_id and a.WX_USER=f.wx_main_id 
                where a.task_state=2 and c.HUILIAO_USER=%s order by a.create_time desc""" % (oper_id)
        statData = mySqlUtil.getDictData(sql)
    except :
        logger.warn(traceback.format_exc())
        statData='fail'
    # print (statData)
    return HttpResponse(json.dumps(statData))

@csrf_exempt
#获取已完成任务列表
def get_tasklist_com(request):
    ret={}
    try:
        oper_id = request.session['oper_id']
        #正在进行的任务
        sql = """select a.task_id,a.task_name,b.wx_login_id as wx_user,a.filter_fact,b.head_picture,b.wx_name,d.f_count,ifnull(m_count,0) m_count,
                    case when d.f_count=0 then 0 else format(ifnull(m_count,0)/a.filter_fact*100,1) end as sum_count,ifnull(success_count,0) success_count,a.task_state
                    from OKAY_TASK_INFO a
                    inner join wx_account_info b on a.WX_USER=b.wx_id
                    inner join OKAY_TASK_INFO_INDEX c on a.task_id=c.task_id
                    left join (select a.wx_main_id,count(1) f_count from wx_friend_rela a,wx_friend_list b where a.wx_id=b.wx_id  group by a.wx_main_id) d on a.WX_USER=d.wx_main_id
                        left join (SELECT task_id,count(1) m_count from OKAY_TASK_LIST where TASK_SEQ_FLAG='2' group by task_id) e on a.TASK_ID=e.task_id
                    left join (
                        select b.task_id,c.wx_main_id,count(1) success_count from OKAY_TASK_INFO a
                        inner join OKAY_TASK_LIST b on a.TASK_ID=b.TASK_ID
                        inner join wx_friend_rela c on a.WX_USER=c.wx_main_id 
                            and case when IFNULL(b.TARGET_WX_ID,'')<>'' then b.TARGET_WX_ID else b.TARGET_WX_NAME end =
                                    case when IFNULL(b.TARGET_WX_ID,'')<>'' then c.wx_id else c.remark end
                            and b.TARGET_WX_NAME <>'' and b.TARGET_WX_NAME is not null
                        where b.SEND_CODE='1' and b.TASK_SEQ_FLAG='2' and date_format(c.add_time,'%%Y%%m%%d%%H%%i%%s')>a.create_time
                        group by b.task_id,c.wx_main_id
                    ) f on a.TASK_ID=f.task_id and a.WX_USER=f.wx_main_id
                    where a.task_state in (3,4) and c.HUILIAO_USER=%s order by a.create_time desc""" % (oper_id)
        statData = mySqlUtil.getDictData(sql)
    except :
        logger.warn(traceback.format_exc())
        statData='fail'
    return HttpResponse(json.dumps(statData))

# 获取省份城市json数据
def getCity(request):

    if (request.method == 'GET'):
        try:
            sql = "select province,city  from PROVINCE_CITY_MAPPING"
            areaDict = mySqlUtil.getData(sql)
            resultList = []
            resultList.append({'name': '不限', 'city_name': [{'name': '不限'}]})
            resultDict = {}
            for areaRel in areaDict:
                provinceName = areaRel[0]
                cityName = areaRel[1]
                if provinceName not in resultDict.keys():
                    resultDict[provinceName] = []
                else:
                    resultDict[provinceName].append(cityName)
            # [{'name': '不限', 'city_name': [{'name': '不限'}]}}]

            for provinceKey in resultDict.keys():
                standardModal = {'name': provinceKey, 'city_name': [{'name': '不限'}]}
                for citykey in resultDict[provinceKey]:
                    standardModal['city_name'].append({'name': citykey})
                resultList.append(standardModal.copy())
            # result = []
            # for i in data1:
            #     d = {}
            #     city = []
            #     d['name'] = i['province']
            #     sql = "select '不限' as city  union all select  city  from PROVINCE_CITY_MAPPING where  province ='" + i[
            #         'province'] + "'"
            #     ret = mySqlUtil.getDictData(sql)
            #     for ct in ret:
            #         c = {}
            #         c['name'] = ct['city']
            #         city.append(c)
            #     d['city_name'] = city
            #     result.append(d)
            # print(result)
            return HttpResponse(json.dumps(resultList, ensure_ascii=False))
        except Exception as e:
            logger.warn(traceback.format_exc())
            data = '获取城市失败'
            return HttpResponse(json.dumps(data, ensure_ascii=False))


def selectList (request):
    if request.method == 'GET':
        oper_id = request.session['oper_id']
        sql = """select a.FLAG_TYPE_VALUE,a.FLAG_TYPE_NAME from OKAY_PAGE_STATIC_FLAG a where state='E' GROUP BY a.FLAG_TYPE_VALUE,a.FLAG_TYPE_NAME ORDER BY a.FLAG_TYPE_VALUE """
        data = mySqlUtil.getDictData(sql)
        result = []
        for i in data:
            id = i['FLAG_TYPE_VALUE']
            sql = """select a.FLAG_VALUE_VALUE,a.FLAG_VALUE_NAME from OKAY_PAGE_STATIC_FLAG_POWER a where state='E' and a.FLAG_TYPE_VALUE='%s'"""%(id)
            r1 = mySqlUtil.getDictData(sql)
            sel = {'id': id, 'name': i['FLAG_TYPE_NAME'], 'child': r1}
            result.append(sel)
        return HttpResponse(json.dumps(result, ensure_ascii=False))


@csrf_exempt
def weixin_num(request):
    if request.method == 'POST':
        data = json.loads(request.POST.get('data'))
        request.session['condition'] = data
        province = request.POST.get('province')
        request.session['province'] = province
        city = request.POST.get('city')
        request.session['city'] = city
        condition = ''
        n = 1
        for i in data:
            try:
                id = i['id']
            except:
                continue
            m = 1
            for child in i['child']:
                tname = 't'+str(n)
                if m>=2:
                    condition = condition[:-1]
                    condition += ' or '+tname+'.FLAG_VALUE='+child['childid']+')'
                else:
                    if child['childid']=='0':
                        continue
                    else:
                        condition += ' inner join OKAY_USER_FLAG_DEF '+tname+'  on a.user_id='+tname+'.user_id and ('+tname+'.FLAG_TYPE='+id+' and '+tname+'.FLAG_VALUE='+child['childid']+')'
                        m = m+1
            n = n+1
        condition += """ where a.user_id not in (select user_id from OKAY_TASK_LIST where SUBSTRING(TASK_PRE_EXEC,1,8)> DATE_FORMAT(DATE_SUB(now(),interval 1 month),"%Y%m%d") group by user_id having count(1)>2)"""
        if province != '不限':
            condition +=" and a.province_name='" + province + "'"
        if city != '不限':
            condition += " and a.city_name='" + city + "'"
        sql = 'select count(distinct a.user_id) as num from OKAY_USER_BASE_INFO a ' + condition
        result = mySqlUtil.getDictData(sql)
        return HttpResponse(json.dumps(result, ensure_ascii=False))
#预览数据加载
@csrf_exempt
def preview(request):
    if request.method == 'POST':
        province = request.POST.get('province')
        city = request.POST.get('city')
        data = json.loads(request.POST.get('data'))
        postindex = int(request.POST.get('postindex'))
        if postindex == 0:
            postindex = 0.1
        condition = ''
        n = 1
        for i in data:
            try:
                id = i['id']
            except:
                continue
            m = 1
            for child in i['child']:
                tname = 't' + str(n)
                if m>=2:
                    condition = condition[:-1]
                    condition += ' or '+tname+'.FLAG_VALUE='+child['childid']+')'
                else:
                    if child['childid']=='0':
                        continue
                    else:
                        condition += 'inner join OKAY_USER_FLAG_DEF ' + tname + ' on a.user_id=' + tname + '.user_id and (' + tname + '.FLAG_TYPE=' + id + ' and ' + tname + '.FLAG_VALUE=' + \
                                     child['childid'] + ')'
                        m = m + 1
            n = n + 1
        condition += """ where a.user_id not in (select user_id from OKAY_TASK_LIST where TASK_SEQ_FLAG='2' and SUBSTRING(TASK_PRE_EXEC,1,8)> DATE_FORMAT(DATE_SUB(now(),interval 1 month),"%Y%m%d") group by user_id having count(1)>2)"""
        if province != '不限':
            condition += " and a.province_name='" + province + "'"
        if city != '不限':
            condition += " and a.city_name='" + city + "'"
        condition += """ limit """ + str(int(postindex * 10 - 1)) + """,10)t INNER JOIN OKAY_USER_FLAG_DEF c ON t.user_id = c.user_id  JOIN OKAY_PAGE_STATIC_FLAG e  ON c.FLAG_TYPE = e.FLAG_TYPE_VALUE  and c.FLAG_VALUE = e.FLAG_VALUE_VALUE GROUP BY  WX_CODE,PROVINCE_NAME,CITY_NAME,AGE,t.user_id """
        sql = """select concat(concat( SUBSTRING( t.WX_CODE, 1, 3 ), '*****' ),SUBSTRING( t.WX_CODE, 9, 3 )) AS WX_CODE,
                     t.PROVINCE_NAME,
                     t.CITY_NAME,
                     ifnull(cast(t.AGE as char),'-') as AGE,
                     ifnull(GROUP_CONCAT(case when e.FLAG_TYPE_VALUE=3 then e.FLAG_VALUE_NAME else null end ),'-') AS SEX,
                     ifnull(GROUP_CONCAT(case when e.FLAG_TYPE_VALUE=1 then e.FLAG_VALUE_NAME else null end ),'-') AS HANGYE,
                     ifnull(GROUP_CONCAT(case when e.FLAG_TYPE_VALUE=2 then e.FLAG_VALUE_NAME else null end ),'-') AS JOB,
                     ifnull(GROUP_CONCAT(case when e.FLAG_TYPE_VALUE=5 then e.FLAG_VALUE_NAME else null end ),'-') AS FLAG
                    from (select
                    DISTINCT
                    a.user_id,   
                    b.WX_CODE,
                    a.PROVINCE_NAME,
                    a.CITY_NAME,
                    a.AGE
                    FROM
                     OKAY_USER_BASE_INFO a
                     JOIN OKAY_USER_ADDRESS_BOOK b    ON a.USER_ID = b.USER_ID """ + condition
        result = mySqlUtil.getDictData(sql)
        return HttpResponse(json.dumps(result, ensure_ascii=False))

def friend_select(request):
    if request.method == 'GET':
        return render(request, 'friend_select.html')

def friend_add(request):
    if request.method == 'GET':
        return render(request, 'friend_add.html')

@csrf_exempt
def weixin(request):
    if request.method == 'POST':
        oper_id = request.session['oper_id']
        sql = """SELECT A.wx_id,A.wx_name,A.phone_no,A.head_picture,case when D.fri_num is null then 0 else D.fri_num end as fri_num,CASE WHEN E.add_num IS NULL THEN 0 ELSE E.add_num END AS add_num
          FROM wx_account_info A join wx_oper_wx B on (A.wx_id = B.object_id) and B.oper_id='%s'
          left JOIN (select a.wx_main_id,count(1) as fri_num from wx_friend_rela a,wx_friend_list b where a.wx_id=b.wx_id  group by a.wx_main_id) D on A.wx_id=D.wx_main_id LEFT JOIN(
          select wx_main_id,count(distinct wx_id) as add_num from wx_chat_info_his where content='我通过了你的朋友验证请求，现在我们可以开始聊天了' and send_time >=DATE_SUB(now(), INTERVAL 30 DAY)
          group by wx_main_id) E ON A.wx_id = E.wx_main_id where A.if_start=1 order by A.register_time desc""" %(oper_id)
        result = mySqlUtil.getDictData(sql)
        return HttpResponse(json.dumps(result, ensure_ascii=False))

@csrf_exempt
def getTask(request):
    if request.method == 'POST':
        request.session['task_name'] = request.POST.get('task_name')
        request.session['filter_fact'] = request.POST.get('add_num')
        request.session['tot_user'] = request.POST.get('tot_user')
        return HttpResponse(json.dumps('success', ensure_ascii=False))

#检查是否存在执行任务 --
@csrf_exempt
def taskExist(request):
    wx_id = request.POST.get('wx_id')
    try:
        sql = """select ifnull(count(1),0) as ongoing from OKAY_TASK_INFO where wx_user='%s' and task_state='1' """ % (wx_id)
        result = mySqlUtil.getDictData(sql)
        if result[0]['ongoing'] != 0:
            sql = """	select 	task_name,date_format(a.CREATE_TIME,"%%Y-%%m-%%d %%H:%%i:%%s")as create_time,format(ifnull(m_count,0)/a.filter_fact*100,0) as finish, '1' as type 
             from OKAY_TASK_INFO a left join (SELECT task_id,count(1) m_count from OKAY_TASK_LIST where send_code is not null group by task_id) b
              on a.TASK_ID=b.task_id where a.wx_user='%s' and task_state='1'"""%(wx_id)
            result = mySqlUtil.getDictData(sql)
            return HttpResponse(json.dumps(result, ensure_ascii=False))
        else:
            result =[{'type':'0'}]
            return HttpResponse(json.dumps(result, ensure_ascii=False))

    except Exception as e:
        print (e)

#任务提交
@csrf_exempt
def commitTask(request):
    try:
        if request.method == 'POST':
            oper_id = request.session['oper_id']
            wx_id = request.POST.get('wx_id') #
            type = request.POST.get('type') #1 终止任务并重新下发新任务 2 直接开始新任务
            sayHi = request.POST.get('sayHi')
            CREATE_TIME = time.strftime("%Y%m%d%H%M%S", time.localtime())
            task_id = uuid.uuid1()
            province = request.session['province']
            city = request.session['city']
            request.session['sayHi'] = sayHi
            if type == '1':
                # 终止正在进行任务
                sql1 = """update wx_task_manage set ifKill=1 where  taskSeq in (select distinct b.TASK_SEQ from OKAY_TASK_INFO a join OKAY_TASK_LIST b on a.task_id=b.task_id where WX_USER='%s' and TASK_STATE='1') and status=2""" % (
                    wx_id)
                ret = mySqlUtil.getDictData(sql1)
                # 终止等待进行任务
                sql2 = """update wx_task_manage set status=6,remarks='人工终止' where  taskSeq in (select distinct b.TASK_SEQ from OKAY_TASK_INFO a join OKAY_TASK_LIST b on a.task_id=b.task_id where WX_USER='%s' and TASK_STATE='1') and status=1""" % (
                    wx_id)
                ret = mySqlUtil.getDictData(sql2)
                # 更新显示任务列表
                sql3 = """update OKAY_TASK_INFO set task_state='3' ,remark='创建新任务终止'  where wx_user='%s' and task_state='1';""" % (wx_id)
                ret = mySqlUtil.getDictData(sql3)
                # 以上终止前任任务
            # 新增任务
            if city == '不限':
                city = ''
            sql4 = """insert into OKAY_TASK_BASE_FILTER(TASK_ID,PROVINCE_NAME,CITY_NAME) values ('%s','%s','%s');""" % (
                task_id, province, city)
            r = mySqlUtil.getDictData(sql4)
            sql5 = """insert into OKAY_TASK_INFO_INDEX(HUILIAO_USER,TASK_ID) values ('%s','%s');""" % (oper_id, task_id)
            r = mySqlUtil.getDictData(sql5)
            sql6 = """insert into OKAY_TASK_INFO(TASK_ID,TASK_NAME,WX_USER,GREETINGS_MSG,FILTER_FACT,EXEC_TYPE,CREATE_TIME,task_state) values('%s','%s','%s','%s','%s','%s','%s','%s');""" % (
                task_id, request.session['task_name'], wx_id, sayHi, request.session['filter_fact'], '1', CREATE_TIME,
                '1')
            r = mySqlUtil.getDictData(sql6)
            for i in request.session['condition']: # 获取筛选条件
                try:
                    id = i['id']
                except:
                    continue
                insertsql = """insert into OKAY_TASK_FILTER(TASK_ID,FLAG_TYPE,FLAG_VALUE) values """
                for child in i['child']:
                    insertsql += """('%s','%s','%s'),""" % (task_id, id, child['childid'])
                    # print(sql)
                r = mySqlUtil.getDictData(insertsql[:-1])
            newThreading = threading.Thread(target=taskSegement, args=(
                task_id, request.session['filter_fact'], request.session['condition'], province, city,
                request.session['sayHi'], request.session['tot_user'], request.session['oper_name']))
            newThreading.start()
            data = {'msg': 'success'}
        else:
            data = {'msg': 'fail'}
    except Exception:
        data = {'msg': 'fail'}
        logger.warn(traceback.format_exc())
    finally:
        return HttpResponse(json.dumps(data, ensure_ascii=False))

#任务详情-
@csrf_exempt
def friend_task(request):
    if request.method=="GET":
        taskid=request.GET.get('taskid')
        popup=request.GET.get('popup')
        if taskid!=None:
            taskid=taskid.strip()
        if popup==u'' or  popup is None:
            return render(request,'friend_task.html',{'taskid':taskid})
        else:
            return render(request, 'friend_task_1.html', {'taskid': taskid})

    if request.method=="POST":
        taskid=request.POST.get('taskid')
        if taskid != None:
            taskid = taskid.strip()
        sql="""select 
               ta.TASK_ID as taskid,
               ta.TASK_NAME  as task,
               concat(tb.PROVINCE_NAME,tb.CITY_NAME) as  addr,
               GREETINGS_MSG  as greet ,
               tc.wx_login_id  as addAddr,
               case when EXEC_TYPE='1'  then concat('立即 (',substring(CREATE_TIME,1,8),' ',substring(CREATE_TIME,9,2),':',substring(CREATE_TIME,11,2),':',substring(CREATE_TIME,13,2),')')  
                     when  EXEC_TYPE='2' then '定时'  
                    end as  addTime,
               td.name  as remark,
               FILTER_FACT as taskcnt,
               CONCAT(substring(CREATE_TIME,1,6),'000000')   as exectime,
               TASK_STATE as taskstate,
                tc.wx_name nicheng,
                tc.head_picture  pictureurl
               from  OKAY_TASK_INFO  ta left join wx_dictionary td on ta.remark = td.value and td.type='task_remark'
               inner join wx_account_info tc on ta.WX_USER=tc.wx_id
               left join  OKAY_TASK_BASE_FILTER tb on ta.TASK_ID=tb.TASK_ID
               where ta.TASK_ID='%s'  """  %(taskid)
        ret=mySqlUtil.getDictData(sql)
        if ret!=[]:
            dataRet=ret[0]
            data = {'task': dataRet['task'],
                    'addr': dataRet['addr'],
                    'addAddr': dataRet['addAddr'],
                    'addTime': dataRet['addTime'],
                    'greet': dataRet['greet'],
                    'remark':dataRet['remark'],
                    'taskcnt':dataRet['taskcnt'],
                    'exectime':dataRet['exectime'],
                    'taskstate': dataRet['taskstate'],
                    'pictureurl':dataRet['pictureurl'],
                    'nicheng':dataRet['nicheng']}
        else:
            data = {'task':u'','addr':u'','addAddr':u'','addTime':u'','greet':u'','remark':u'','taskcnt':u''}
            data['exectime']=u'';


        sql="""select 
                 FLAG_TYPE_NAME  as flagtype ,  
                 group_concat(FLAG_VALUE_NAME) as  flagname
                                from  OKAY_TASK_FILTER  ta 
                       ,OKAY_PAGE_STATIC_FLAG tb 
               where
                    ta.FLAG_TYPE=tb.FLAG_TYPE_VALUE
               and ta.FLAG_VALUE=tb.FLAG_VALUE_VALUE
               and  TASK_ID='%s'
               group by FLAG_TYPE_NAME     """ %(taskid)

        retlist = mySqlUtil.getDictData(sql)
        data['sex']=u'不限';data['tmt']=u'不限';data['job']=u'不限';data['consume']=u'不限';data['flag']=u'不限';data['age']=u'不限'
        if retlist!=[]:
            for res in retlist:
                if res['flagtype']==u'性别':
                    data['sex']=res['flagname']
                if res['flagtype']== u'行业':
                    data['tmt'] = res['flagname']
                if res['flagtype']== u'职业':
                    data['job'] = res['flagname']
                if res['flagtype']== u'消费':
                    data['consume']= res['flagname']
                if res['flagtype']== u'标签':
                    data['flag']=res['flagname']
        return HttpResponse(json.dumps(data, ensure_ascii=False))

@csrf_exempt
def task_schedule(request):
    if request.method == "POST":
        taskid=request.POST.get("taskid")
        querytime =request.POST.get("querytime").strip()
        passtime = request.POST.get("passtime").strip()
        sendtime = request.POST.get("sendtime").strip()
        loadcnt = request.POST.get("loadcnt").strip()
        if loadcnt=='1' :
            passtime=querytime
            sendtime=querytime
        if taskid != None:
            taskid = taskid.strip()
        sql = """select  
               sum(case when   ta.TASK_SEQ_FLAG='2'  then 1 else 0 end)  as  sendcnt 
               from OKAY_TASK_LIST ta where   ta.TASK_ID='""" + taskid + """'"""
        ret = mySqlUtil.getDictData(sql)
        data={}
        # print(ret)
        if ret!=[]:
            data['sendcnt']=str(ret[0]['sendcnt'])
        else:
            data['sendcnt']=u'0';

        sql = """select count(1) passcnt from OKAY_TASK_INFO a
                  inner join OKAY_TASK_LIST b on a.TASK_ID=b.TASK_ID
                inner join wx_friend_rela c on a.WX_USER=c.wx_main_id
	                    and case when IFNULL(b.TARGET_WX_ID,'')<>'' then b.TARGET_WX_ID else b.TARGET_WX_NAME end =
			    case when IFNULL(b.TARGET_WX_ID,'')<>'' then c.wx_id else c.remark end
                where b.task_id='%s'
                      and b.SEND_CODE='1' and b.TASK_SEQ_FLAG='2' and date_format(c.add_time,'%%Y%%m%%d%%H%%i%%s')>a.create_time
                """ % (taskid)
        ret = mySqlUtil.getDictData(sql)
        if ret != []:
            data['passcnt'] = str(ret[0]['passcnt'])
        else:
            data['passcnt'] = u'0'

        if data['sendcnt']=='None':
            data['sendcnt']=u'0';
        if data['passcnt'] == 'None':
            data['passcnt'] = u'0'


        sql= """
           select  ctype, optime,wx,msg  from 
             (
                select 
                '1'  as  ctype ,
                concat(substring(SEND_CODE_TIME,1,8),' ',substring(SEND_CODE_TIME,9,2),':',substring(SEND_CODE_TIME,11,2),':',substring(SEND_CODE_TIME,13,2)) optime,
                concat(SUBSTR(WX_CODE,1,3),'*****',SUBSTR(WX_CODE,length(WX_CODE)-2,3)) as  wx ,
                case when   SEND_CODE='1' then  '好友添加请求发送成功'
                     when   SEND_CODE='4' then  '添加成功'
                     WHEN    SEND_CODE='7' then  '对方账号异常' 
                    else '搜索不到微信号'  end  as msg
                from OKAY_TASK_LIST ta 
                where 
                     SEND_CODE  is not null
                and ta.TASK_SEQ_FLAG = '2' 
                and   ta.TASK_ID='%s'
                and   SEND_CODE_TIME>'%s'
                union all
                 select 
                           '2'  as  ctype,
                              DATE_FORMAT(c.ADD_TIME,"""  %(taskid,sendtime) \
                              +r"'%Y%m%d %H:%i:%S'"\
                              +""") optime,
                              concat(SUBSTR(b.WX_CODE,1,3),'*****',SUBSTR(b.WX_CODE,length(b.WX_CODE)-2,3)) as  wx ,
                             '添加成功' as msg
                             from OKAY_TASK_INFO a
                            inner join OKAY_TASK_LIST b on a.TASK_ID=b.TASK_ID
                            inner join wx_friend_rela c on a.WX_USER=c.wx_main_id
                            	and case when IFNULL(b.TARGET_WX_ID,'')<>'' then b.TARGET_WX_ID else b.TARGET_WX_NAME end =
                            			case when IFNULL(b.TARGET_WX_ID,'')<>'' then c.wx_id else c.remark end
                            where b.task_id='%s'
                            and   b.SEND_CODE='1' and b.TASK_SEQ_FLAG='2' and date_format(c.add_time,"""%(taskid)+r"'%Y%m%d%H%i%s'"+""")>a.create_time
                            and    DATE_FORMAT(c.ADD_TIME,"""  \
                           +r"'%Y%m%d %H:%i:%S'"\
                           +""")>'%s' 
                         ) tab 
                    order by optime ,ctype """  %(passtime)
        data['listmsg']= mySqlUtil.getDictData(sql)
        sql = """select max(SEND_CODE_TIME) as sendtime from  OKAY_TASK_LIST where TASK_ID='%s'"""  %(taskid)
        ret= mySqlUtil.getDictData(sql)
        if ret != []:
            data['sendtime']=ret[0]['sendtime']
        else:
            data['sendtime']=data['exectime']

        sql = """select max(DATE_FORMAT(c.ADD_TIME,'%%Y%%m%%d%%H%%i%%S')) passtime from OKAY_TASK_INFO a
                inner join OKAY_TASK_LIST b on a.TASK_ID=b.TASK_ID
                inner join wx_friend_rela c on a.WX_USER=c.wx_main_id
                and case when IFNULL(b.TARGET_WX_ID,'')<>'' then b.TARGET_WX_ID else b.TARGET_WX_NAME end =
                case when IFNULL(b.TARGET_WX_ID,'')<>'' then c.wx_id else c.remark end
                where b.task_id='%s'
                and   b.SEND_CODE='1' and b.TASK_SEQ_FLAG='2' and date_format(c.add_time,'%%Y%%m%%d%%H%%i%%s')>a.create_time""" % (taskid)
        ret = mySqlUtil.getDictData(sql)
        if ret != []:
            data['passtime'] = ret[0]['passtime']
        else:
            data['passtime'] = data['exectime']

        if data['sendtime']=='None':
            data['sendtime'] = data['exectime']
        if data['passtime']== 'None':
            data['passtime'] = data['exectime']


        return HttpResponse(json.dumps(data, ensure_ascii=False))
#检测任务是否下发完成
@csrf_exempt
def taskReady(request):
    if request.method == "POST":
        taskid = request.POST.get("taskid")
        try:
            sql="""select FILTER_FACT from OKAY_TASK_INFO where TASK_ID='%s'"""%(taskid)
            FILTER_FACT = mySqlUtil.getDictData(sql)
            sql="""select ifnull(count(1),0) as FACT_NUM from OKAY_TASK_LIST where TASK_ID='%s' and TASK_SEQ_FLAG !='0'"""%(taskid)
            FACT_NUM = mySqlUtil.getDictData(sql)
            if int(FILTER_FACT[0]['FILTER_FACT']) == int(FACT_NUM[0]['FACT_NUM']):
                data = {"msg": "succeess"}
            else:
                data = {"msg": "fail"}
        except Exception as e:
            print (e)
        return HttpResponse(json.dumps(data, ensure_ascii=False))
@csrf_exempt
def change_task(request):
    if request.method == "POST":

        try:
            taskid = request.POST.get("taskid").strip()
            task_state=request.POST.get("task_state").strip()
            if task_state == '1':
                reboot_sql1 = """select distinct TASK_SEQ as taskseq from OKAY_TASK_LIST where task_id='%s' union all select distinct
                 subTaskSeq as taskseq from wx_add_friend where taskSeq in (select distinct TASK_SEQ as taskseq from OKAY_TASK_LIST
                  where task_id='%s') and subTaskSeq is not null """%(taskid,taskid)
                ret = mySqlUtil.getDictData(reboot_sql1)
                reboot_seq = ''
                for param in ret:
                    reboot_seq += str(param['taskseq'])+','
                reboot_sql2 = """update wx_task_manage set status=1,remarks='人工重启',ifKill=0 where  taskSeq in (%s)""" % (reboot_seq[:-1])
                ret = mySqlUtil.getDictData(reboot_sql2)
                reboot_sql3 = """update OKAY_TASK_INFO set task_state='%s' ,remark='%s'  where TASK_ID='%s';""" % (
                task_state, '1', taskid)
                ret = mySqlUtil.getDictData(reboot_sql3)
            elif task_state == '2':
                sql = """select ta.taskseq,ta.status from wx_task_manage ta join wx_account_info tb on ta.uuid=tb.uuid  join (select WX_USER from OKAY_TASK_INFO where task_id = '%s') tc on tb.wx_id = tc.WX_USER
                            where  ta.actiontype in(30,32) and ta.status  in (1,2)""" %(taskid)
                ret = mySqlUtil.getDictData(sql)
                pause_seq = ''
                for param in ret:
                    if param['status'] == 2:
                        pause_sql1 = """update wx_task_manage set ifKill=1 where  taskSeq='%s' """ %(param['taskseq'])
                        ret = mySqlUtil.getDictData(pause_sql1)
                    else:
                        pause_seq+=str(param['taskseq'])+','
                pause_sql2 = """update wx_task_manage set status=5,remarks='人工暂停' where  taskSeq in (%s)""" % (pause_seq[:-1])
                ret = mySqlUtil.getDictData(pause_sql2)
                pause_sql3 = """update OKAY_TASK_INFO set task_state='%s' ,remark='%s'  where TASK_ID='%s';""" % (task_state, '2', taskid)
                ret = mySqlUtil.getDictData(pause_sql3)
            else:
                sql1 = """select ta.taskseq,ta.status from wx_task_manage ta join wx_account_info tb on ta.uuid=tb.uuid  join (select WX_USER from OKAY_TASK_INFO where task_id = '%s') tc on tb.wx_id = tc.WX_USER
                                        where  ta.actiontype in(30,32) and ta.status  in (1,2)""" % (taskid)
                ret = mySqlUtil.getDictData(sql1)
                stop_seq = ''
                if ret:
                    for param in ret:
                        if param['status'] == 2:
                            stop_sql1 = """update wx_task_manage set ifKill=1 where  taskSeq='%s' """ % (param['taskseq'])
                            ret = mySqlUtil.getDictData(stop_sql1)
                        else:
                            stop_seq += str(param['taskseq']) + ','
                    stop_sql2 = """update wx_task_manage set status=6,remarks='人工终止' where  taskSeq in (%s)""" % (stop_seq[:-1])
                    ret = mySqlUtil.getDictData(stop_sql2)
                stop_sql3 = """update OKAY_TASK_INFO set task_state='%s' ,remark='%s'  where TASK_ID='%s';""" % (task_state, '4', taskid)
                ret = mySqlUtil.getDictData(stop_sql3)
            data={"msg":"succeess"}
        except Exception as e:
            logger.warn(traceback.format_exc())
        return HttpResponse(json.dumps(data, ensure_ascii=False))


# 下发任务
def taskSegement(task_id, filter_fact, condition, province, city, sayHi, tot_user, oper_name):
    times = 0 #循环次数
    while True:
        times = times + 1
        if times > 5:   #超过5次下发任务失败，退出下发循环
            break
        taskSeqGroup = []
        try:
            require = ''
            n = 1
            for i in condition:
                try:
                    id = i['id']
                except:
                    continue
                m = 1
                for child in i['child']:
                    tname = 't' + str(n)
                    if m >= 2:
                        require = require[:-1]
                        require += ' or ' + tname + '.FLAG_VALUE=' + child['childid'] + ')'
                    else:
                        if child['childid'] == '0':
                            continue
                        else:
                            require += ' inner join OKAY_USER_FLAG_DEF ' + tname + ' on a.user_id=' + tname + '.user_id and (' + tname + '.FLAG_TYPE=' + id + ' and ' + tname + '.FLAG_VALUE=' + \
                                       child['childid'] + ') '
                            m = m + 1
                n = n + 1
            require += """ where a.user_id not in (select user_id from OKAY_TASK_LIST where TASK_SEQ_FLAG='2' and SUBSTRING(TASK_PRE_EXEC,1,8)> DATE_FORMAT(DATE_SUB(now(),interval 1 month),'%Y%m%d') group by user_id having count(1)>2)"""
            if province != '不限':
                require += " and a.province_name='" + province + "'"
            if city != '':
                require += " and a.city_name='" + city + "'"

            if int(filter_fact) > 50:
                number = int(math.ceil(int(filter_fact) / 50))  #执行规模总页数
                tot_number = int(math.ceil(int(tot_user) / 50))  # 数据总量总页数
                randomlist = []
                x = 0
                while x < number:
                    nexttime1 = datetime.datetime.now() +datetime.timedelta(minutes=(x*5))
                    #设定用户数和用户量相等不随机2
                    if number==tot_number:
                        offset = x*50-1
                    #偏移量随机
                    else:
                        while 1 == 1:
                            offset = random.randint(0, tot_number-2)*50-1
                            if offset in randomlist:
                                continue
                            else:
                                randomlist.append(offset)
                                break
    
                    if offset < 0:
                        offset = 0
                    if x == number-1:
                        limit = int(filter_fact)-((x)*50)
                        sql = """ SELECT t.USER_ID,b.WX_CODE FROM (select a.USER_ID  from OKAY_USER_BASE_INFO a """+require+""" limit %s,%s )t join  OKAY_USER_ADDRESS_BOOK b on t.USER_ID = b.USER_ID """%(offset,limit)
                    else:
                        sql = """SELECT t.USER_ID,b.WX_CODE FROM (select a.USER_ID  from OKAY_USER_BASE_INFO a """+require+""" limit %s,%s )t join  OKAY_USER_ADDRESS_BOOK  b on t.USER_ID = b.USER_ID """%(offset,'50')
                    result = mySqlUtil.getDictData(sql)
                    friendlist = ''
                    taskSeq = round(time.time() * 1000000 + random.randint(100000, 999999))
                    task_pre_exec1 = nexttime1.strftime("%Y%m%d%H%M%S")
                    task_pre_exec2 = nexttime1.strftime("%Y-%m-%d %H:%M:%S")
                    taskSeqGroup.append(taskSeq)
                    insert_sql = """insert into OKAY_TASK_LIST(task_id,USER_ID,WX_CODE,TASK_SEQ,TASK_SEQ_FLAG,ORDER_ID,task_pre_exec,execute_type) values"""
                    for col in result:
                        friendlist += ('#'+col['WX_CODE'])
                        insert_sql +="""('%s','%s','%s','%s','%s','%s','%s','%s'),"""%(task_id,col['USER_ID'],col['WX_CODE'],taskSeq,'0',(x+1),task_pre_exec1,'2')
                    r = mySqlUtil.getDictData(insert_sql[:-1])
                    sql1 = """insert into wx_add_friend(taskSeq,frinedIdList,sayHi,freindIdListRecover) values( '%s','%s','%s','%s'); """ % (taskSeq, friendlist[1:], sayHi, friendlist[1:])
                    r = mySqlUtil.getDictData(sql1)
                    sql2 = """insert into  wx_task_manage(taskSeq,uuid,actionType,createTime,priority,status,alarm,cronTime,operViewName) select  '%s' as taskSeq,ta.uuid,30,now() as createTime,10,1,'1', '%s' as cronTime,'%s' as operViewName from wx_account_info ta, OKAY_TASK_INFO tb where tb.wx_user=ta.wx_id and tb.task_id='%s';""" % (
                    taskSeq,task_pre_exec2, oper_name,task_id)
                    r = mySqlUtil.getDictData(sql2)
                    sql3 = """UPDATE  OKAY_TASK_LIST set  TASK_SEQ_FLAG='1' where TASK_SEQ='%s';""" % (taskSeq)
                    r = mySqlUtil.getDictData(sql3)
                    x = x+1
    
            else:
                taskSeq = round(time.time() * 1000000 + random.randint(100000, 999999))
                taskSeqGroup.append(taskSeq)
                task_pre_exec = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                i = 0
                randomlist = []
                friendlist =''
                insert_sql = """insert into OKAY_TASK_LIST(task_id,USER_ID,WX_CODE,TASK_SEQ,TASK_SEQ_FLAG,ORDER_ID,task_pre_exec,execute_type) values"""
                while i < int(filter_fact):
                    # 随机偏移量
                    while 1 == 1:
                        offset = random.randint(1, int(tot_user)) - 1
                        if offset in randomlist:
                            continue
                        else:
                            randomlist.append(offset)
                            break
                    sql = """SELECT t.USER_ID,b.WX_CODE FROM (select a.USER_ID  from OKAY_USER_BASE_INFO a """+require+""" limit %s,%s )t join  OKAY_USER_ADDRESS_BOOK   b  on t.USER_ID = b.USER_ID """% (
                    offset, 1)
                    result = mySqlUtil.getDictData(sql)
                    friendlist += ('#'+result[0]['WX_CODE'])
                    insert_sql += """('%s','%s','%s','%s','%s','%s','%s','%s'),""" %(task_id, result[0]['USER_ID'], result[0]['WX_CODE'], taskSeq, '0','0', task_pre_exec,'2')
                    i = i + 1
                r = mySqlUtil.getDictData(insert_sql[:-1])
                sql1 = """insert into wx_add_friend(taskSeq,frinedIdList,sayHi,freindIdListRecover) values( '%s','%s','%s','%s');""" % (taskSeq,friendlist[1:], sayHi, friendlist[1:])
                r = mySqlUtil.getDictData(sql1)
                sql2 = """insert into  wx_task_manage(taskSeq,uuid,actionType,createTime,priority,status,alarm,operViewName) select  '%s' as taskSeq,ta.uuid,30,now() as createTime,10,1,'1','%s' as operViewName from wx_account_info ta, OKAY_TASK_INFO tb where tb.wx_user=ta.wx_id and tb.task_id='%s';"""%(taskSeq,oper_name,task_id)
                r = mySqlUtil.getDictData(sql2)
                sql3 ="""UPDATE  OKAY_TASK_LIST set  TASK_SEQ_FLAG='1' where TASK_SEQ='%s';"""%(taskSeq)
                r = mySqlUtil.getDictData(sql3)
        except Exception as e:
            logger.error(e)
        finally:
            seqgroup =''
            for i in taskSeqGroup:
                seqgroup += str(i)+','
            sql = """select ifnull(count(1),0) as FACT_NUM from OKAY_TASK_LIST where TASK_ID='%s' and TASK_SEQ_FLAG !='0'""" % (task_id)
            FACT_NUM = mySqlUtil.getDictData(sql)
            sql1 = """select count(1) as F_LIST from wx_add_friend where taskSeq in (%s) """ % (seqgroup[:-1])
            F_LIST = mySqlUtil.getDictData(sql1)
            sql2 = """select count(1) as M_LIST from wx_task_manage where taskSeq in (%s) """ % (seqgroup[:-1])
            M_LIST = mySqlUtil.getDictData(sql2)
            group =int(math.ceil(int(filter_fact) / 50))
            if int(filter_fact) == int(FACT_NUM[0]['FACT_NUM']) and group == int(F_LIST[0]['F_LIST']) and group == int(M_LIST[0]['M_LIST']):
                break
            else:
                sql1 = """delete from wx_add_friend where taskSeq in (%s)"""%(seqgroup[:-1])
                r = mySqlUtil.getDictData(sql1)
                sql2 = """delete from wx_task_manage where taskSeq in (%s)""" % (seqgroup[:-1])
                r = mySqlUtil.getDictData(sql2)
                sql3 = """delete from OKAY_TASK_LIST where TASK_ID='%s'""" % (task_id)
                r = mySqlUtil.getDictData(sql3)

def popup(request):
    return render(request, 'popup.html', {'MSG':"哈哈" })

#检查微信是否在线
@csrf_exempt
def wxOnline(request):
    task_id = request.POST.get('task_id')
    data = {'status':'online'}
    sql = """select b.wx_status from OKAY_TASK_INFO a join wx_account_info b on b.wx_id=a.wx_user where  a.task_id='%s'"""%(task_id)
    result = mySqlUtil.getDictData(sql)
    if result[0]['wx_status']=='0':
        data ={'status': 'offline'}
    return HttpResponse(json.dumps(data, ensure_ascii=False))

#检测手机号码是否正确
def phonecheck(phone):
    # 号码前缀，如果运营商启用新的号段，只需要在此列表将新的号段加上即可。
    phoneprefix = ['130','131','132','133','134','135','136','137','138','139','150','151','152','153','155','156','157','158','159','170','183','182','185','186','188','189']
    # 检测号码是否长度是否合法。
    if len(phone)!= 11:
        return False
    else:
        # 检测输入的号码是否全部是数字。
        if phone.isdigit():
            # 检测前缀是否是正确。
            if phone[:3] in phoneprefix:
                return True
            else:
                return False
        else:
            return False


@csrf_exempt
def commitTaskByFile(request):
    data = {'status': -1}
    if request.method == "POST":
        UserPhoneGet = request.POST.get('wxIdList')
        operId = request.session['oper_id']
        operName = request.session['oper_name']
        # wxId = request.POST.get('wx_id')
        wxId = request.POST.get('createTaskValue').split(',')[1]
        sayHi = request.POST.get('sayHi')
        CREATE_TIME = time.strftime("%Y%m%d%H%M%S", time.localtime())
        taskId = uuid.uuid1()

        if not UserPhoneGet:
            data["status"] = -2
        else:
            try:
                # 获取uuid
                uuidGetSql = """select uuid,wx_name from wx_account_info
                                    where wx_id = \"%s\" or wx_login_id = \"%s\"""" % (wxId, wxId)
                uuidGet = mySqlUtil.getData(uuidGetSql)[0][0]
                wxName = mySqlUtil.getData(uuidGetSql)[0][1]
                # 按loopGap个数切分列表
                loopGap = 50
                UserPhoneList = [i for i in UserPhoneGet.split("\n") if i != ""]
                UserPhoneListExt = [UserPhoneList[i:i + loopGap] for i in range(0, len(UserPhoneList), loopGap)]

                taskName = "%s文件导入" % (wxName)
                taskInfoSql = """insert into OKAY_TASK_INFO(TASK_ID,TASK_NAME,WX_USER,GREETINGS_MSG,FILTER_FACT,EXEC_TYPE,CREATE_TIME,task_state) values('%s','%s','%s','%s','%s','%s','%s','%s');""" % (
                    taskId, taskName, wxId, sayHi, len(UserPhoneList), '1', CREATE_TIME, '0')
                mySqlUtil.excSql(taskInfoSql)
                # print(taskInfoSql)

                taskBaseFilterSql = """insert into OKAY_TASK_BASE_FILTER(TASK_ID,PROVINCE_NAME,CITY_NAME) values ('%s',"","");""" % (
                    taskId)
                mySqlUtil.excSql(taskBaseFilterSql)
                # print(taskBaseFilterSql)
                taskInfoIndexSql = """insert into OKAY_TASK_INFO_INDEX(HUILIAO_USER,TASK_ID) values ('%s','%s');""" % (
                operId, taskId)
                mySqlUtil.excSql(taskInfoIndexSql)
                # print(taskInfoIndexSql)


                taskFilterSql = """INSERT INTO `OKAY_TASK_FILTER` (`TASK_ID`, `FLAG_TYPE`, `FLAG_VALUE`)
                              VALUES (\'%s\', '1', '0'),(\'%s\', '2', '0'),(\'%s\', '3', '0'),(\'%s\', '5', '0')""" % (
                taskId, taskId, taskId, taskId)
                mySqlUtil.excSql(taskFilterSql)
                # print(taskFilterSql)

                insertTaskListSql = """insert into OKAY_TASK_LIST(task_id,USER_ID,WX_CODE,TASK_SEQ,TASK_SEQ_FLAG,ORDER_ID,task_pre_exec,execute_type) values"""
                insertAddFriendSql = """insert into wx_add_friend(taskSeq,frinedIdList,sayHi,freindIdListRecover) values"""
                insertWxTaskSql = """insert into  wx_task_manage(taskSeq,uuid,actionType,createTime,priority,status,operViewName) values"""
                updateTaskInfoSql = """ UPDATE OKAY_TASK_INFO SET TASK_STATE='1' where TASK_ID='%s'""" % (taskId)
                for seqItem, userItemList in enumerate(UserPhoneListExt):
                    taskSeq = round(time.time() * 1000000 + random.randint(100000, 999999))
                    friendlist = "#".join(userItemList)
                    insertAddFriendSql += """('%s','%s','%s','%s'),""" % (taskSeq, friendlist, sayHi, friendlist)
                    insertWxTaskSql += """('%s','%s',30,now(),10,'1','%s'),""" % (taskSeq, uuidGet, operName,)
                    for userItem in userItemList:
                        insertTaskListSql += """('%s','F_%s','%s','%s','%s','%s','%s','%s'),""" % (
                            taskId, userItem, userItem, taskSeq, '1', seqItem + 1,  (datetime.datetime.now() +datetime.timedelta(minutes=(seqItem*5))).strftime("%Y%m%d%H%M%S"),  '2')

                insertTaskListSql = insertTaskListSql[:-1]
                insertAddFriendSql = insertAddFriendSql[:-1]
                insertWxTaskSql = insertWxTaskSql[:-1]
                mySqlUtil.excSql(insertTaskListSql)
                # print(insertTaskListSql)
                mySqlUtil.excSql(insertAddFriendSql)
                # print(insertAddFriendSql)
                mySqlUtil.excSql(insertWxTaskSql)
                # print(insertWxTaskSql)
                mySqlUtil.excSql(updateTaskInfoSql)

                data = {'status': 1}
            except Exception:
                logger.warn(traceback.format_exc())
                data = {'status': -1}


    return HttpResponse(json.dumps(data, ensure_ascii=False))