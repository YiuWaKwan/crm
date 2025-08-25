import pymysql
import traceback

import time

import datetime
from DBUtils.PooledDB import PooledDB
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from lib.FinalLogger import getLogger
from lib.ModuleConfig import ConfAnalysis
import os
import mySqlUtil
import json
from lib.DateEncoder import DateEncoder
import pinyin
from lib.FinalLogger import getLogger


BASEDIR = os.getcwd()
if not os.path.exists("%s/conf"%BASEDIR) or not os.path.exists("%s/log"%BASEDIR):
    BASEDIR = os.path.dirname(os.getcwd())


# 初始化logger
logger = getLogger('./log/report.log')

# 初始化config
configFile = './conf/moduleConfig.conf'
confAllItems = ConfAnalysis(logger, configFile)

MysqlConfig = {
    'host': confAllItems.getOneOptions('database', 'host'),
    'port': int(confAllItems.getOneOptions('database', 'port')),
    'user': confAllItems.getOneOptions('database', 'user'),
    'password': confAllItems.getOneOptions('database', 'password'),
    'db': confAllItems.getOneOptions('database', 'db'),
    'charset': confAllItems.getOneOptions('database', 'charset'),
}
class MysqlDbPool(object):
    db_pool=None
    def __init__(self,mincached=1,maxcached=20):
        loggerFIle = 'log/report_mysql.log'
        self.logger = getLogger(loggerFIle)
        while True:
            try:
                self.db_pool = PooledDB(creator=pymysql,
                                        mincached=mincached,  # 启动时开启的空连接数
                                        maxcached=maxcached,  # 连接池最大可用连接数量
                                        host=MysqlConfig['host'],
                                        port=MysqlConfig['port'],
                                        user=MysqlConfig['user'],
                                        passwd=MysqlConfig['password'],
                                        db=MysqlConfig['db'],
                                        charset='utf8mb4',
                                        cursorclass=pymysql.cursors.DictCursor)
                break
            except Exception as e:
                logger.info("数据库连接失败，1分钟后重连")
                time.sleep(60)
    def getDictData(self,sql):
        # select
        executeRet = 0
        try:
            conn = self.db_pool.connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            # 获取返回结果
            executeRet = cursor.fetchall()
            conn.commit()
            conn.close()
        except(Exception) as e:
            self.logger.error(sql)
            self.logger.error(traceback.format_exc())
        return executeRet

# 初始化config
#configFile =  '%s/conf/moduleConfig.conf' % BASEDIR
#confAllItems = ConfAnalysis(logger, configFile, loggerFIle)
try:
    mySqlUtil=MysqlDbPool()
except Exception as e:
    logger.error(traceback.format_exc())

def report(request):
    if(request.method=='GET'):
        return render(request, 'report.html')

@csrf_exempt
def dreport(request):
    if (request.method == 'POST'):
        oper_id = request.session['oper_id']
        month = datetime.datetime.now().strftime("%Y%m")
        sql = """select substr(cur_date,7,2) as cur_date,cast(sum(t.add_s_person_num) as char) add_s_person_num from wechat_report_%s t
         where oper_id=%s and substr(cur_date,1,6)='%s' group by cur_date ORDER BY cur_date asc""" % (month, oper_id, month)
        data = mySqlUtil.getDictData(sql)
        return HttpResponse(json.dumps(data, ensure_ascii=False))

@csrf_exempt
def wreport(request):
    if (request.method == 'POST'):
        oper_id = request.session['oper_id']
        month = datetime.datetime.now().strftime("%Y%m")
        sql = """select substr(cur_date,7,2) as cur_date,cast(sum(t.send_num)as char) as send_num,cast(sum(t.receive_num)as char)as receive_num,cast(sum(t.chat_group_fri_num)as char)as chat_group_fri_num,
        cast(sum(t.chat_fri_num)as char) as chat_fri_num,cast(sum(t.chat_group_num) as char)as chat_group_num,cast(sum(t.chat_group_call_num)as char) as chat_group_call_num from wechat_report_%s t
         where oper_id=%s and substr(cur_date,1,6)='%s' group by cur_date ORDER BY cur_date asc""" % (month, oper_id, month)
        data = mySqlUtil.getDictData(sql)
        return HttpResponse(json.dumps(data, ensure_ascii=False))

@csrf_exempt
def wgreport(request):
    if (request.method == 'POST'):
        oper_id = request.session['oper_id']
        month = datetime.datetime.now().strftime("%Y%m")
        sql = """select substr(cur_date,7,2) as cur_date,cast(sum(t.group_num)as char) as group_num,cast(sum(t.group_fri_num)as char)as group_fri_num,cast(sum(t.send_msg_num)as char)as send_msg_num,
        cast(sum(t.receive_msg_num)as char) as receive_msg_num,cast(sum(t.chat_fri_inter_num) as char)as chat_fri_inter_num,cast(sum(t.new_chat_fri_num)as char) as new_chat_fri_num from wechatgroup_report_%s t
         where oper_id=%s and substr(cur_date,1,6)='%s' group by cur_date ORDER BY cur_date asc""" % (month, oper_id, month)
        data = mySqlUtil.getDictData(sql)
        return HttpResponse(json.dumps(data, ensure_ascii=False))

def operReport(request):
    if (request.method == 'GET'):
        return render(request, 'operReport.html')

def chatReport(request):
    if (request.method == 'GET'):
        return render(request, 'chatReport.html')

def groupReport(request):
    if (request.method == 'GET'):
        return render(request, 'groupReport.html')

@csrf_exempt
def get_operReport(request):
    if (request.method == 'POST'):
        oper_id = request.session['oper_id']
        pageSize = json.loads(request.body.decode('utf-8')).get('pageSize')
        offset = json.loads(request.body.decode('utf-8')).get('offset')
        starttime = json.loads(request.body.decode('utf-8')).get('start')
        endtime = json.loads(request.body.decode('utf-8')).get('end')
        start = datetime.datetime.strptime(starttime, '%Y%m%d')
        end = datetime.datetime.strptime(endtime, '%Y%m%d')
        if(start.month==end.month):
            month = datetime.datetime.strftime(start, '%Y%m')
            sql = """select t1.name,t.fri_num,t.group_num,t.actgroup_num,t.chat_group_fri_num,t.add_s_person_num,
            t.send_num,t.chat_group_call_num,0 as overtime_num ,t.new_chat_fri_num from wechat_report_sum_%s t join wx_system_operator t1 on t.oper_id=t1.oper_id
                         where t.cur_date>='%s' and t.cur_date<='%s' and t.oper_id= %s limit %s,%s""" % (
            month, starttime, endtime, oper_id,offset,pageSize)
            data = mySqlUtil.getDictData(sql)
            sql = """select count(1) as total from wechat_report_sum_%s t join wx_system_operator t1 on t.oper_id=t1.oper_id
                        where t.cur_date>='%s' and t.cur_date<='%s' and t.oper_id= %s""" % (
            month, starttime, endtime, oper_id)
            total = mySqlUtil.getDictData(sql)
            ret = {'rows': data, 'total': total[0].get('total')}
        else:
            month = datetime.datetime.strftime(start, '%Y%m')
            interval = end.month - start.month
            i = 1
            sql1 = """select t1.name,t.fri_num,t.group_num,t.actgroup_num,t.chat_group_fri_num,t.add_s_person_num,t.send_num,t.chat_group_call_num,0 as overtime_num ,t.new_chat_fri_num  from
                                (select * from wechat_report_sum_%s""" % (month)
            sql2 = """select count(1) as total  from (select * from wechat_report_sum_%s""" % (month)
            while i <= interval:
                mon = str(int(month) + i)
                sql1 += """ union all select * from wechat_report_%s""" % (mon)
                sql2 += """ union all select * from wechat_report_%s""" % (mon)
                i = i + 1
            sql1 += """) t join wx_system_operator t1 on t.oper_id=t1.oper_id where t.cur_date>='%s' and t.cur_date<='%s' and t.oper_id= %s limit %s,$s""" % (
            starttime, endtime, oper_id,offset,pageSize)
            sql2 += """) t where t.cur_date>='%s' and t.cur_date<='%s' and t.oper_id= %s""" % (
            starttime, endtime, oper_id)
            data = mySqlUtil.getDictData(sql1)
            total = mySqlUtil.getDictData(sql2)
            ret = {'rows': data, 'total': total[0].get('total')}
        return HttpResponse(json.dumps(ret, ensure_ascii=False))

@csrf_exempt
def get_chatReport(request):
    if (request.method == 'POST'):
        oper_id = request.session['oper_id']
        param = json.loads(request.body.decode('utf-8'))
        pageSize = param.get('pageSize')
        offset = param.get('offset')
        starttime = param.get('start')
        endtime = param.get('end')
        start = datetime.datetime.strptime(starttime, '%Y%m%d')
        end = datetime.datetime.strptime(endtime, '%Y%m%d')
        if (start.month == end.month):
            month = datetime.datetime.strftime(start, '%Y%m')
            sql = """select t.wx_name,cast(sum(t.chat_fri_num)as char) chat_fri_num,cast(sum(t.chat_group_num)as char) chat_group_num,
            cast(sum(t.add_s_person_num)as char) add_s_person_num,cast(sum(t.send_num)as char) send_num,cast(sum(t.chat_group_fri_num)as char)chat_group_fri_num,
            cast(sum(t.chat_group_call_num)as char) chat_group_call_num from wechat_report_%s t 
             where t.cur_date>='%s' and t.cur_date<='%s' and oper_id= %s group by t.wx_name limit %s,%s""" % (month, starttime, endtime, oper_id,offset,pageSize)
            data = mySqlUtil.getDictData(sql)
            sql = """select count(1) as total from(select count(1) from wechat_report_%s t
            where t.cur_date>='%s' and t.cur_date<='%s' and oper_id= %s group by t.wx_name) a""" % (month, starttime, endtime, oper_id)
            total = mySqlUtil.getDictData(sql)
            ret = {'rows': data, 'total': total[0].get('total')}
        else:
            month = datetime.datetime.strftime(start, '%Y%m')
            interval = end.month - start.month
            i = 1
            sql1 = """select t.wx_name,cast(sum(t.chat_fri_num)as char) chat_fri_num,cast(sum(t.chat_group_num)as char) chat_group_num,
            cast(sum(t.add_s_person_num)as char) add_s_person_num,cast(sum(t.send_num)as char) send_num,cast(sum(t.chat_group_fri_num)as char)chat_group_fri_num,
            cast(sum(t.chat_group_call_num)as char) chat_group_call_num  from
                    (select * from wechat_report_%s"""%(month)
            sql2 = """select count(1) as total from(select count(1)  from (select * from wechat_report_%s""" % (month)
            while i <= interval:
                mon = str(int(month)+i)
                sql1 += """ union all select * from wechat_report_%s"""%(mon)
                sql2 += """ union all select * from wechat_report_%s""" % (mon)
                i = i + 1
            sql1 += """) t where t.cur_date>='%s' and t.cur_date<='%s' and oper_id= %s group by t.wx_name limit %s,%s""" % (starttime, endtime, oper_id,offset,pageSize)
            sql2 += """) t where t.cur_date>='%s' and t.cur_date<='%s' and oper_id= %s group by t.wx_name) a""" % (starttime, endtime, oper_id)
            data = mySqlUtil.getDictData(sql1)
            total = mySqlUtil.getDictData(sql2)
            ret = {'rows': data, 'total': total[0].get('total')}
        return HttpResponse(json.dumps(ret, ensure_ascii=False))

@csrf_exempt
def get_groupReport(request):
    if (request.method == 'POST'):
        oper_id = request.session['oper_id']
        pageSize = json.loads(request.body.decode('utf-8')).get('pageSize')
        offset = json.loads(request.body.decode('utf-8')).get('offset')
        starttime = json.loads(request.body.decode('utf-8')).get('start')
        endtime = json.loads(request.body.decode('utf-8')).get('end')
        start = datetime.datetime.strptime(starttime, '%Y%m%d')
        end = datetime.datetime.strptime(endtime, '%Y%m%d')
        if (start.month == end.month):
            month = datetime.datetime.strftime(start, '%Y%m')
            sql="""select t.wx_name,cast(sum(t.group_num)as char) group_num,cast(sum(t.actgroup_num)as char) actgroup_num,
            cast(sum(t.add_s_person_num)as char)add_s_person_num ,cast(sum(t.send_msg_num)as char) send_msg_num,
            cast(sum(t.chat_fri_inter_num)as char) chat_fri_inter_num,0 as overtime_num,cast(sum(t.new_chat_fri_num)as char) new_chat_fri_num from wechatgroup_report_%s t
            where t.cur_date>='%s' and t.cur_date<='%s' and oper_id= %s group by wx_main_id,wx_name limit %s,%s""" % (month, starttime, endtime, oper_id,offset,pageSize)
            data = mySqlUtil.getDictData(sql)
            sql = """select count(1) as total from(select count(1) from wechatgroup_report_%s t
            where t.cur_date>='%s' and t.cur_date<='%s' and oper_id= %s group by wx_main_id,wx_name)a""" % (month, starttime, endtime, oper_id)
            total = mySqlUtil.getDictData(sql)
            ret = {'rows': data, 'total': total[0].get('total')}
        else:
            month = datetime.datetime.strftime(start, '%Y%m')
            interval = end.month - start.month
            i = 1
            sql1 = """select t.wx_name,cast(sum(t.group_num)as char) group_num,cast(sum(t.actgroup_num)as char) actgroup_num,
            cast(sum(t.add_s_person_num)as char)add_s_person_num ,cast(sum(t.send_msg_num)as char) send_msg_num,
            cast(sum(t.chat_fri_inter_num)as char) chat_fri_inter_num,0 as overtime_num,cast(sum(t.new_chat_fri_num)as char) new_chat_fri_num  from
             ( select * from wechatgroup_report_%s""" % (month)
            sql2 = """select count(1) as total from(select count(1) from ( select * from wechatgroup_report_%s""" % (month)
            while i < interval:
                mon = str(int(month) + i)
                sql1 += """ union all select * from wechatgroup_report_%s"""%(mon)
                sql2 += """ union all select * from wechatgroup_report_%s"""%(mon)
                i = i + 1
            sql1 += """) t where t.cur_date>='%s' and t.cur_date<='%s' and oper_id= %s group by wx_main_id,wx_name limit %s,%s""" % (starttime, endtime, oper_id,offset,pageSize)
            sql2 += """) t where t.cur_date>='%s' and t.cur_date<='%s' and oper_id= %s group by wx_main_id,wx_name) a""" % (starttime, endtime, oper_id)
            data = mySqlUtil.getDictData(sql1)
            total = mySqlUtil.getDictData(sql2)
            ret = {'rows': data, 'total': total[0].get('total')}
        return HttpResponse(json.dumps(ret, ensure_ascii=False))

def census(request):
    if(request.method=='GET'):
        return render(request, 'cencus.html')
def second_census(request):
    if(request.method=='GET'):
        return render(request, 'second_census.html')
def group_sdetail(request):
    if(request.method=='GET'):
        return render(request, 'group_sdetail.html')
def group_mdetail(request):
    if(request.method=='GET'):
        return render(request, 'group_mdetail.html')
def group_omdetail(request):
    if(request.method=='GET'):
        return render(request, 'group_omdetail.html')
def group_imdetail(request):
    if(request.method=='GET'):
        return render(request, 'group_imdetail.html')
@csrf_exempt
def get_data_sum(request):
    if(request.method == 'POST'):
        try:
            oper_id = request.session['oper_id']
            wx_id = request.POST.get('wx_id')
            group_list = request.POST.get('group_list')
            starttime = request.POST.get('start')
            endtime = request.POST.get('end')
            start = datetime.datetime.strptime(starttime, '%Y%m%d')
            end = datetime.datetime.strptime(endtime, '%Y%m%d')
            month = datetime.datetime.strftime(start, '%Y%m')
            yesterday = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y%m%d")
            if (start.month == end.month):
                sql = """select cast(sum(case when a.datetime='%s' then a.group_num else 0 end)as char) group_num,cast(sum(a.active_num)as char) active_num, cast(sum(a.total_num)as char) total_num,cast(sum(a.reply_num)as char) reply_num,
                cast(sum(a.consult_avg_num)as char)consult_avg_num,cast(round(sum(a.service_people)/sum(group_num)*100,2)as char) active_percent from (select distinct group_id,datetime,group_num,active_num,total_num,reply_num,service_people,consult_avg_num from group_dim_base_%s a join wx_oper_wx b on a.wx_id=b.object_id and b.oper_id='%s' where a.datetime>='%s' and a.datetime<='%s'"""\
                      %(yesterday,month,oper_id,starttime,endtime)
                if wx_id != '':
                    wx_id_list = ''
                    for i in wx_id.split(','):
                        wx_id_list += i + "','"
                    sql += """ and a.wx_id in ('%s')""" % (wx_id_list[:-3])
                if group_list != '':
                    group_id =''
                    for i in group_list.split(','):
                        group_id += i+ "','"
                    sql+= """ and a.group_id in ('%s')"""%(group_id[:-3])
            else:
                interval = end.month - start.month
                i = 0
                sql = """select cast(sum(case when datetime='%s' then group_num else 0 end)as char) group_num,cast(sum(active_num)as char) active_num, cast(sum(total_num)as char) total_num,cast(sum(reply_num)as char) reply_num,
                                cast(sum(a.consult_avg_num)as char)consult_avg_num,cast(round(sum(a.service_people)/sum(group_num)*100,2)as char) active_percent from (select distinct group_id,datetime,group_num,active_num,total_num,reply_num,service_people,consult_avg_num from (select * from group_dim_base_%s """ \
                      % (yesterday, month)
                while i < interval:
                    mon = str(int(month) + i+1)
                    sql += """ union all select * from group_dim_base_%s""" % (mon)
                    i = i + 1
                sql += """) a join wx_oper_wx b on a.wx_id=b.object_id and b.oper_id='%s' where datetime>='%s' and datetime<='%s'"""%(oper_id,starttime, endtime)
                if wx_id != '':
                    wx_id_list = ''
                    for i in wx_id.split(','):
                        wx_id_list += i + "','"
                    sql += """ and wx_id in ('%s')""" % (wx_id_list[:-3])
                if group_list != '':
                    group_id = ''
                    for i in group_list.split(','):
                        group_id += i + "','"
                    sql += """ and group_id in ('%s')""" % (group_id[:-3])
            sql += ') a'
            result = mySqlUtil.getDictData(sql)
            return HttpResponse(json.dumps(result, ensure_ascii=False))
        except Exception as e:
            logger.error(e)

@csrf_exempt
def get_group_change(request):
    try:
        oper_id = request.session['oper_id']
        wx_id = request.POST.get('wx_id')
        group_list = request.POST.get('group_list')
        starttime = request.POST.get('start')
        endtime = request.POST.get('end')
        start = datetime.datetime.strptime(starttime, '%Y%m%d')
        end = datetime.datetime.strptime(endtime, '%Y%m%d')
        month = datetime.datetime.strftime(start, '%Y%m')
        if (start.month == end.month):
            sql = """select substr(datetime,5,4) as cur_date,cast(sum(reply_num)as char)reply_num,cast(sum(total_num)as char) total_num,cast(sum(active_people)as char) active_people,
            cast(sum(service_people)as char) service_people from (select distinct datetime,group_id,reply_num,total_num,active_people,service_people from group_dim_base_%s  a join wx_oper_wx b on a.wx_id=b.object_id and b.oper_id='%s' where datetime>='%s' and datetime<='%s' """%(month,oper_id,starttime,endtime)
            if wx_id != '':
                wx_id_list=''
                for i in wx_id.split(','):
                    wx_id_list += i + "','"
                sql += """ and wx_id in ('%s')""" % (wx_id_list[:-3])
            if group_list != '':
                group_id = ''
                for i in group_list.split(','):
                    group_id += i + "','"
                sql += """ and group_id in ('%s')""" % (group_id[:-3])
        else:
            interval = end.month - start.month
            i = 0
            sql = """select substr(datetime,5,4) as cur_date,cast(sum(reply_num)as char)reply_num,cast(sum(total_num)as char) total_num,cast(sum(active_people)as char) active_people,
                        cast(sum(service_people)as char) service_people from(select distinct datetime,group_id,reply_num,total_num,active_people,service_people from (select * from group_dim_base_%s""" % (
            month)
            while i < interval:
                mon = str(int(month) + i+1)
                sql += """ union all select * from group_dim_base_%s""" % (mon)
                i = i + 1
            sql += """)  a join wx_oper_wx b on a.wx_id=b.object_id and b.oper_id='%s' where datetime>='%s' and datetime<='%s'""" % (oper_id,starttime, endtime)
            if wx_id != '':
                wx_id_list = ''
                for i in wx_id.split(','):
                    wx_id_list += i + "','"
                sql += """ and wx_id in ('%s')""" % (wx_id_list[:-3])
            if group_list != '':
                group_id = ''
                for i in group_list.split(','):
                    group_id += i + "','"
                sql += """ and group_id in ('%s')""" % (group_id[:-3])
        sql += """) a group by datetime order by datetime asc"""
        result = mySqlUtil.getDictData(sql)
        return HttpResponse(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        logger.error(e)

@csrf_exempt
def get_group_spread(request):
    try:
        oper_id = request.session['oper_id']
        wx_id = request.POST.get('wx_id')
        group_list = request.POST.get('group_list')
        starttime = request.POST.get('start')
        endtime = request.POST.get('end')
        start = datetime.datetime.strptime(starttime, '%Y%m%d')
        end = datetime.datetime.strptime(endtime, '%Y%m%d')
        month = datetime.datetime.strftime(start, '%Y%m')
        if (start.month == end.month):
            sql = """select cast(sum(words_msg_num)as char)words_msg_num,cast(sum(picture_msg_num)as char)picture_msg_num,cast(sum(file_msg_num)as char) file_msg_num,
            cast(sum(sys_msg_num)as char) sys_msg_num,cast(sum(voice_msg_num)as char)voice_msg_num,cast(sum(video_msg_num)as char)video_msg_num ,cast(sum(link_msg_num)as char)link_msg_num,cast(sum(other_msg_num)as char)other_msg_num
             from(select distinct group_id,words_msg_num,picture_msg_num,file_msg_num,sys_msg_num,voice_msg_num,video_msg_num,link_msg_num,other_msg_num from group_dim_base_%s  a join wx_oper_wx b on a.wx_id=b.object_id and b.oper_id='%s' where datetime>='%s' and datetime<='%s' """ % (
            month, oper_id,starttime, endtime)
            if wx_id != '':
                wx_id_list = ''
                for i in wx_id.split(','):
                    wx_id_list += i + "','"
                sql += """ and wx_id in ('%s')""" % (wx_id_list[:-3])
            if group_list != '':
                group_id = ''
                for i in group_list.split(','):
                    group_id += i + "','"
                sql += """ and group_id in ('%s')""" % (group_id[:-3])
        else:
            interval = end.month - start.month
            i = 0
            sql = """select cast(sum(words_msg_num)as char)words_msg_num,cast(sum(picture_msg_num)as char)picture_msg_num,cast(sum(file_msg_num)as char) file_msg_num,
                        cast(sum(sys_msg_num)as char) sys_msg_num,cast(sum(voice_msg_num)as char)voice_msg_num,cast(sum(video_msg_num)as char)video_msg_num ,cast(sum(link_msg_num)as char)link_msg_num,cast(sum(other_msg_num)as char)other_msg_num
                      from(select distinct group_id,words_msg_num,picture_msg_num,file_msg_num,sys_msg_num,voice_msg_num,video_msg_num,link_msg_num,other_msg_num  from (select *  from group_dim_base_%s """ % (month)
            while i < interval:
                mon = str(int(month) + i+1)
                sql += """ union all select * from group_dim_base_%s""" % (mon)
                i = i + 1
            sql += """)  a join wx_oper_wx b on a.wx_id=b.object_id and b.oper_id='%s' where datetime>='%s' and datetime<='%s'""" % (oper_id,starttime, endtime)
            if wx_id != '':
                wx_id_list = ''
                for i in wx_id.split(','):
                    wx_id_list += i + "','"
                sql += """ and wx_id in ('%s')""" % (wx_id_list[:-3])
            if group_list != '':
                group_id = ''
                for i in group_list.split(','):
                    group_id += i + "','"
                sql += """ and group_id in ('%s')""" % (group_id[:-3])
        sql +=') a'
        result = mySqlUtil.getDictData(sql)
        return HttpResponse(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        logger.error(e)

@csrf_exempt
def get_sdata_sum(request):
    if(request.method == 'POST'):
        try:
            oper_id = request.session['oper_id']
            group_list = request.POST.get('group_list')
            wx_id = request.POST.get('wx_id')
            starttime = request.POST.get('start')
            endtime = request.POST.get('end')
            start = datetime.datetime.strptime(starttime, '%Y%m%d')
            end = datetime.datetime.strptime(endtime, '%Y%m%d')
            yesterday = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y%m%d")
            month = datetime.datetime.strftime(start, '%Y%m')
            if (start.month == end.month):
                sql = """select cast(sum(case when datetime='%s' then group_num else 0 end)as char) group_num,cast(sum(active_num)as char) active_num, cast(sum(not_active_num)as char) not_active_num,cast(sum(out_group_num)as char) out_group_num,
                cast(sum(in_group_num)as char) in_group_num,cast(round(sum(a.service_people)/sum(group_num)*100,2)as char) active_percent
                 from (select distinct group_id,datetime,group_num,active_num,not_active_num,out_group_num,in_group_num,service_people from group_dim_base_%s  a join wx_oper_wx b on a.wx_id=b.object_id and b.oper_id='%s'  where datetime>='%s' and datetime<='%s'"""\
                      %(yesterday,month,oper_id,starttime,endtime)
                if wx_id != '':
                    wx_id_list = ''
                    for i in wx_id.split(','):
                        wx_id_list += i + "','"
                    sql += """ and wx_id in ('%s')""" % (wx_id_list[:-3])
                if group_list != '':
                    group_id = ''
                    for i in group_list.split(','):
                        group_id += i + "','"
                    sql += """ and group_id in ('%s')""" % (group_id[:-3])
            else:
                interval = end.month - start.month
                i = 0
                sql = """select cast(sum(case when datetime='%s' then group_num else 0 end)as char) group_num,cast(sum(active_num)as char) active_num, cast(sum(not_active_num)as char) not_active_num,cast(sum(out_group_num)as char) out_group_num,
                                cast(sum(in_group_num)as char) in_group_num,cast(round(sum(a.service_people)/sum(group_num)*100,2)as char) active_percent
                                 from (select distinct group_id,datetime,group_num,active_num,not_active_num,out_group_num,in_group_num,service_people from (select * from group_dim_base_%s""" \
                      % (yesterday, month)
                while i < interval:
                    mon = str(int(month) + i+1)
                    sql += """ union all select * from group_dim_base_%s""" % (mon)
                    i = i + 1
                sql += """) a join wx_oper_wx b on a.wx_id=b.object_id and b.oper_id='%s'  where datetime>='%s' and datetime<='%s'""" % (oper_id,starttime, endtime)
                if wx_id != '':
                    wx_id_list = ''
                    for i in wx_id.split(','):
                        wx_id_list += i + "','"
                    sql += """ and wx_id in ('%s')""" % (wx_id_list[:-3])
                if group_list != '':
                    group_id = ''
                    for i in group_list.split(','):
                        group_id += i + "','"
                    sql += """ and group_id in ('%s')""" % (group_id[:-3])
            sql += ') a'
            result = mySqlUtil.getDictData(sql)
            return HttpResponse(json.dumps(result, ensure_ascii=False))
        except Exception as e:
            logger.error(e)

@csrf_exempt
def group_num_change(request):
    try:
        oper_id = request.session['oper_id']
        group_list = request.POST.get('group_list')
        wx_id = request.POST.get('wx_id')
        starttime = request.POST.get('start')
        endtime = request.POST.get('end')
        start = datetime.datetime.strptime(starttime, '%Y%m%d')
        end = datetime.datetime.strptime(endtime, '%Y%m%d')
        month = datetime.datetime.strftime(start, '%Y%m')
        if (start.month == end.month):
            sql = """select substr(datetime,5,4) as cur_date,cast(sum(group_num)as char)group_num,cast(sum(in_group_num)as char) in_group_num,cast(sum(out_group_num)as char) out_group_num
             from (select distinct group_id,datetime,group_num,in_group_num,out_group_num from group_dim_base_%s  a join wx_oper_wx b on a.wx_id=b.object_id and b.oper_id='%s'  where datetime>='%s' and datetime<='%s' """%(month,oper_id,starttime,endtime)
            if wx_id != '':
                wx_id_list = ''
                for i in wx_id.split(','):
                    wx_id_list += i + "','"
                sql += """ and wx_id in ('%s')""" % (wx_id_list[:-3])
            if group_list != '':
                group_id = ''
                for i in group_list.split(','):
                    group_id += i + "','"
                sql += """ and group_id in ('%s')""" % (group_id[:-3])
        else:
            interval = end.month - start.month
            i = 0
            sql = """select substr(datetime,5,4) as cur_date,cast(sum(group_num)as char)group_num,cast(sum(in_group_num)as char) in_group_num,cast(sum(out_group_num)as char) out_group_num
                      from (select distinct group_id,datetime,group_num,in_group_num,out_group_num from (select *  from group_dim_base_%s """ % (month)
            while i < interval:
                mon = str(int(month) + i+1)
                sql += """ union all select * from group_dim_base_%s""" % (mon)
                i = i + 1
            sql += """)  a join wx_oper_wx b on a.wx_id=b.object_id and b.oper_id='%s'  where datetime>='%s' and datetime<='%s'""" % (oper_id,starttime, endtime)
            if wx_id != '':
                wx_id_list = ''
                for i in wx_id.split(','):
                    wx_id_list += i + "','"
                sql += """ and wx_id in ('%s')""" % (wx_id_list[:-3])
            if group_list != '':
                group_id = ''
                for i in group_list.split(','):
                    group_id += i + "','"
                sql += """ and group_id in ('%s')""" % (group_id[:-3])
        sql += """) a group by datetime order by datetime asc"""
        result = mySqlUtil.getDictData(sql)
        return HttpResponse(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        logger.error(e)

@csrf_exempt
def active_change(request):
    try:
        oper_id = request.session['oper_id']
        group_list = request.POST.get('group_list')
        wx_id = request.POST.get('wx_id')
        starttime = request.POST.get('start')
        endtime = request.POST.get('end')
        start = datetime.datetime.strptime(starttime, '%Y%m%d')
        end = datetime.datetime.strptime(endtime, '%Y%m%d')
        month = datetime.datetime.strftime(start, '%Y%m')
        if (start.month == end.month):
            sql = """select substr(datetime,5,4) as cur_date,cast(sum(active_num)as char)active_num,cast(round(sum(a.service_people)/sum(group_num)*100,2)as char) active_percent
             from (select distinct group_id,datetime,active_num,service_people,group_num from group_dim_base_%s  a join wx_oper_wx b on a.wx_id=b.object_id and b.oper_id='%s'  where datetime>='%s' and datetime<='%s' """%(month,oper_id,starttime,endtime)
            if wx_id != '':
                wx_id_list = ''
                for i in wx_id.split(','):
                    wx_id_list += i + "','"
                sql += """ and wx_id in ('%s')""" % (wx_id_list[:-3])
            if group_list != '':
                group_id = ''
                for i in group_list.split(','):
                    group_id += i + "','"
                sql += """ and group_id in ('%s')""" % (group_id[:-3])
        else:
            interval = end.month - start.month
            i = 0
            sql = """select substr(datetime,5,4) as cur_date,cast(sum(active_num)as char)active_num,cast(round(sum(a.service_people)/sum(group_num)*100,2)as char) active_percent
                        from (select distinct group_id,datetime,active_num,service_people,group_num  from (select * from group_dim_base_%s """ % (month)
            while i < interval:
                mon = str(int(month) + i+1)
                sql += """ union all select * from group_dim_base_%s""" % (mon)
                i = i + 1
            sql += """)   a join wx_oper_wx b on a.wx_id=b.object_id and b.oper_id='%s'  where datetime>='%s' and datetime<='%s'""" % (oper_id,starttime, endtime)
            if wx_id != '':
                wx_id_list = ''
                for i in wx_id.split(','):
                    wx_id_list += i + "','"
                sql += """ and wx_id in ('%s')""" % (wx_id_list[:-3])
            if group_list != '':
                group_id = ''
                for i in group_list.split(','):
                    group_id += i + "','"
                sql += """ and group_id in ('%s')""" % (group_id[:-3])
        sql += """) a group by datetime order by datetime asc"""
        result = mySqlUtil.getDictData(sql)
        return HttpResponse(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        logger.error(e)

@csrf_exempt
def group_sdetail_report(request):
    try:
        oper_id = request.session['oper_id']
        wx_id = json.loads(request.body.decode('utf-8')).get('wx_id')
        group_list = json.loads(request.body.decode('utf-8')).get('group_list')
        starttime = json.loads(request.body.decode('utf-8')).get('start')
        endtime = json.loads(request.body.decode('utf-8')).get('end')
        pageSize = json.loads(request.body.decode('utf-8')).get('pageSize')
        offset = json.loads(request.body.decode('utf-8')).get('offset')
        start = datetime.datetime.strptime(starttime, '%Y%m%d')
        end = datetime.datetime.strptime(endtime, '%Y%m%d')
        month = datetime.datetime.strftime(start, '%Y%m')
        if (start.month == end.month):
            sql1 = """select datetime,group_name,wx_login_id,cast(group_num as char) group_num,cast(service_people as char)service_people,cast(at_member_num as char)at_member_num,
            cast(total_num as char)total_num,cast(reply_num as char)reply_num,cast(active_people as char)active_people,concat(cast(round(active_percent*100,2) as char),'%%')active_percent from group_dim_base_%s   a join wx_oper_wx b on a.wx_id=b.object_id and b.oper_id='%s' 
            where datetime>='%s' and datetime<='%s' """%(month,oper_id,starttime,endtime)
            sql2 = """select count(1) as total from group_dim_base_%s  a join wx_oper_wx b on a.wx_id=b.object_id and b.oper_id='%s'  
            where datetime>='%s' and datetime<='%s' """%(month,oper_id,starttime,endtime)
            if wx_id != '' and wx_id!=None:
                wx_id_list = ''
                for i in wx_id.split(','):
                    wx_id_list += i + "','"
                sql1 += """ and wx_id in ('%s')""" % (wx_id_list[:-3])
                sql2 += """ and wx_id in ('%s')""" % (wx_id_list[:-3])
            if group_list != '' and group_list!=None:
                group_id = ''
                for i in group_list.split(','):
                    group_id += i + "','"
                sql1 += """ and group_id in ('%s')""" % (group_id[:-3])
                sql2 += """ and group_id in ('%s')""" % (group_id[:-3])
            if pageSize != None:
                sql1 += """ limit %s,%s"""%(offset,pageSize)
            else:
                sql1 += """ limit 50000"""
        else:
            interval = end.month - start.month
            i = 0
            sql1 = """select datetime,group_name,wx_login_id,cast(group_num as char) group_num,cast(service_people as char)service_people,cast(at_member_num as char)at_member_num,
                        cast(total_num as char)total_num,cast(reply_num as char)reply_num,cast(active_people as char)active_people,
                        cast(active_percent as char)active_percent from (select * from group_dim_base_%s """ % (month)
            sql2 = """select count(1) as total from (select * from group_dim_base_%s  """ % (month)
            while i < interval:
                mon = str(int(month) + i)
                sql1 += """ union all select * from group_dim_base_%s""" % (mon)
                sql2 += """ union all select * from group_dim_base_%s""" % (mon)
                i = i + 1
            sql1 += """)  a join wx_oper_wx b on a.wx_id=b.object_id and b.oper_id='%s'  where datetime>='%s' and datetime<='%s'""" % (oper_id,starttime, endtime)
            sql2 += """)  a join wx_oper_wx b on a.wx_id=b.object_id and b.oper_id='%s'  where datetime>='%s' and datetime<='%s'""" % (oper_id,starttime, endtime)
            if wx_id != '' and wx_id!=None:
                wx_id_list = ''
                for i in wx_id.split(','):
                    wx_id_list += i + "','"
                sql1 += """ and wx_id in ('%s')""" % (wx_id_list[:-3])
                sql2 += """ and wx_id in ('%s')""" % (wx_id_list[:-3])
            if group_list != '' and group_list!=None:
                group_id = ''
                for i in group_list.split(','):
                    group_id += i + "','"
                sql1 += """ and group_id in ('%s')""" % (group_id[:-3])
                sql2 += """ and group_id in ('%s')""" % (group_id[:-3])
            if pageSize != None:
                sql1 += """ limit %s,%s""" % (offset, pageSize)
            else:
                sql1 += """ limit 50000"""
        result = mySqlUtil.getDictData(sql1)
        total = mySqlUtil.getDictData(sql2)
        print(sql1)
        ret = {'rows': result, 'total': total[0].get('total')}
        return HttpResponse(json.dumps(ret, ensure_ascii=False))
    except Exception as e:
        logger.error(e)

@csrf_exempt
def group_mdetail_report(request):
    try:
        oper_id = request.session['oper_id']
        wx_id = json.loads(request.body.decode('utf-8')).get('wx_id')
        group_list = json.loads(request.body.decode('utf-8')).get('group_list')
        pageSize = json.loads(request.body.decode('utf-8')).get('pageSize')
        offset = json.loads(request.body.decode('utf-8')).get('offset')
        sql1 = """select group_member_name,group_member_id,group_name,wx_login_id,DATE_FORMAT(in_group_time,'%%Y%%m%%d')  last_chat_time,
        DATE_FORMAT(in_group_time,'%%Y%%m%%d') in_group_time,invite_name from group_member_base_info a join wx_oper_wx b on a.wx_id=b.object_id
         and b.oper_id='%s'  where 1=1 """ %(oper_id)
        sql2 = """select count(1)as total from group_member_base_info  a join wx_oper_wx b on a.wx_id=b.object_id and b.oper_id='%s'  where 1=1 """ %(oper_id)
        if wx_id != '' and wx_id!= None:
            wx_id_list = ''
            for i in wx_id.split(','):
                wx_id_list += i + "','"
            sql1 += """ and wx_id in ('%s')""" % (wx_id_list[:-3])
            sql2 += """ and wx_id in ('%s')""" % (wx_id_list[:-3])
        if group_list != None and group_list!='':
            group_id = ''
            for i in group_list.split(','):
                group_id += i + "','"
            sql1 += """ and group_id in ('%s')""" % (group_id[:-3])
            sql2 += """ and group_id in ('%s')""" % (group_id[:-3])
        if pageSize != None:
            sql1 += """ limit %s,%s""" % (offset, pageSize)
        else:
            sql1 += """ limit 50000"""
        result = mySqlUtil.getDictData(sql1)
        total = mySqlUtil.getDictData(sql2)
        ret = {'rows': result, 'total': total[0].get('total')}
        return HttpResponse(json.dumps(ret, ensure_ascii=False))
    except Exception as e:
        logger.error(e)

@csrf_exempt
def group_omdetail_report(request):
    try:
        oper_id = request.session['oper_id']
        wx_id = json.loads(request.body.decode('utf-8')).get('wx_id')
        group_list = json.loads(request.body.decode('utf-8')).get('group_list')
        starttime = json.loads(request.body.decode('utf-8')).get('start')
        endtime = json.loads(request.body.decode('utf-8')).get('end')
        pageSize = json.loads(request.body.decode('utf-8')).get('pageSize')
        offset = json.loads(request.body.decode('utf-8')).get('offset')
        sql1 = """select DATE_FORMAT(out_group_time,'%%Y%%m%%d') out_group_time,group_member_name,group_member_id,group_name,wx_login_id,DATE_FORMAT(in_group_time,'%%Y%%m%%d')  last_chat_time,
        DATE_FORMAT(out_group_time,'%%Y%%m%%d') out_group_time,DATE_FORMAT(in_group_time,'%%Y%%m%%d')  in_group_time,
        invite_name from group_member_base_info  a join wx_oper_wx b on a.wx_id=b.object_id and b.oper_id='%s'  where out_group_time is not null and DATE_FORMAT(out_group_time,'%%Y%%m%%d')>='%s' and DATE_FORMAT(out_group_time,'%%Y%%m%%d')<='%s'  """ % (
            oper_id,starttime,endtime)
        sql2 = """select count(1) as total from group_member_base_info  a join wx_oper_wx b on a.wx_id=b.object_id and b.oper_id='%s'
          where out_group_time is not null and DATE_FORMAT(out_group_time,'%%Y%%m%%d')>='%s' and DATE_FORMAT(out_group_time,'%%Y%%m%%d')<='%s'""" % (oper_id,starttime,endtime)
        if wx_id != '' and wx_id!=None:
            wx_id_list = ''
            for i in wx_id.split(','):
                wx_id_list += i + "','"
            sql1 += """ and wx_id in ('%s')""" % (wx_id_list[:-3])
            sql2 += """ and wx_id in ('%s')""" % (wx_id_list[:-3])
        if group_list != None and group_list!='':
            group_id = ''
            for i in group_list.split(','):
                group_id += i + "','"
            sql1 += """ and group_id in ('%s')""" % (group_id[:-3])
            sql2 += """ and group_id in ('%s')""" % (group_id[:-3])
        if pageSize != None:
            sql1 += """ limit %s,%s""" % (offset, pageSize)
        else:
            sql1 += """ limit 50000"""
        result = mySqlUtil.getDictData(sql1)
        total = mySqlUtil.getDictData(sql2)
        ret = {'rows': result, 'total': total[0].get('total')}
        return HttpResponse(json.dumps(ret, ensure_ascii=False))
    except Exception as e:
        logger.error(e)

@csrf_exempt
def group_imdetail_report(request):
    try:
        oper_id = request.session['oper_id']
        wx_id = json.loads(request.body.decode('utf-8')).get('wx_id')
        group_list = json.loads(request.body.decode('utf-8')).get('group_list')
        starttime = json.loads(request.body.decode('utf-8')).get('start')
        endtime = json.loads(request.body.decode('utf-8')).get('end')
        pageSize = json.loads(request.body.decode('utf-8')).get('pageSize')
        offset = json.loads(request.body.decode('utf-8')).get('offset')
        sql1 = """select DATE_FORMAT(in_group_time,'%%Y%%m%%d') in_group_time,group_member_name,group_member_id,group_name,wx_login_id,DATE_FORMAT(in_group_time,'%%Y%%m%%d')  last_chat_time,
        invite_name from group_member_base_info  a join wx_oper_wx b on a.wx_id=b.object_id and b.oper_id='%s'  where DATE_FORMAT(in_group_time,'%%Y%%m%%d')>='%s' and DATE_FORMAT(in_group_time,'%%Y%%m%%d')<='%s'""" % (
            oper_id,starttime,endtime)
        sql2 = """select count(1)as total from group_member_base_info  a join wx_oper_wx b on a.wx_id=b.object_id and b.oper_id='%s'
          where DATE_FORMAT(in_group_time,'%%Y%%m%%d')>='%s' and DATE_FORMAT(in_group_time,'%%Y%%m%%d')<='%s' """ % (oper_id,starttime,endtime)
        if wx_id != None and wx_id!='':
            wx_id_list = ''
            for i in wx_id.split(','):
                wx_id_list += i + "','"
            sql1 += """ and wx_id in ('%s')""" % (wx_id_list[:-3])
            sql2 += """ and wx_id in ('%s')""" % (wx_id_list[:-3])
        if group_list != None and group_list!='':
            group_id = ''
            for i in group_list.split(','):
                group_id += i + "','"
            sql1 += """ and group_id in ('%s')""" % (group_id[:-3])
            sql2 += """ and group_id in ('%s')""" % (group_id[:-3])
        if pageSize != None:
            sql1 += """ limit %s,%s""" % (offset, pageSize)
        else:
            sql1 += """ limit 50000"""
        result = mySqlUtil.getDictData(sql1)
        total = mySqlUtil.getDictData(sql2)
        ret = {'rows': result, 'total': total[0].get('total')}
        return HttpResponse(json.dumps(ret, ensure_ascii=False))
    except Exception as e:
        logger.error(e)

@csrf_exempt
def get_group(request):
    ret_data={}
    try:
        oper_id = request.session['oper_id']
        search = request.POST.get('search')
        wx_id = request.POST.get('wx_id')
        sql = """select distinct tb.group_id,tb.group_name from wx_friend_rela ta join wx_group_info tb on ta.wx_id=tb.group_id join wx_oper_wx tc on ta.wx_main_id=tc.object_id and tc.oper_id='%s'  where  1=1 """%(oper_id)
        if wx_id != '':
            wx_id_list = ''
            for i in wx_id.split(','):
                wx_id_list += i + "','"
            sql += """ and ta.wx_main_id in ('%s')""" % (wx_id_list[:-3])
        if search != '':
            sql += " and tb.group_name like '%"+search+"%'"
        result = mySqlUtil.getDictData(sql)
        jsonData = {}
        for item in result:
            first_letter=str.upper(pinyin.get(item['group_name']," ")[:1])
            key_word = '#'
            if first_letter.isalpha() or first_letter.isdigit():
                key_word=first_letter
            if key_word not in jsonData:
                jsonData[key_word] = {}
            jsonData[key_word][item['group_id']] = item['group_name']
        ret_data_temp={}
        for key in sorted(jsonData.keys()):
            if key!='#':
                ret_data_temp[key]=jsonData[key]
        if '#' in jsonData.keys():
            ret_data_temp['#'] = jsonData['#']
        ret_data=json.dumps(ret_data_temp, ensure_ascii=False)
    except Exception as e:
        logger.info(traceback.format_exc())
    return HttpResponse(ret_data)

@csrf_exempt
def group_num(request):
    result ={}
    try:
        oper_id = request.session['oper_id']
        wx_id = request.POST.get('wx_id')
        sql = """select count(distinct tb.group_id) group_num from wx_friend_rela ta join wx_group_info tb on ta.wx_id=tb.group_id join wx_oper_wx tc on ta.wx_main_id=tc.object_id and tc.oper_id='%s'  where  1=1 """%(oper_id)
        if wx_id != '':
            wx_id_list = ''
            for i in wx_id.split(','):
                wx_id_list += i + "','"
            sql += """ and ta.wx_main_id in ('%s')""" % (wx_id_list[:-3])
        result = mySqlUtil.getDictData(sql)
    except Exception as e:
        logger.info(traceback.format_exc())
    return HttpResponse(json.dumps(result, ensure_ascii=False))