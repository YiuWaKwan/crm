import time
import traceback

import pymysql

from lib.FinalLogger import getLogger
from lib.ModuleConfig import ConfAnalysis
import os
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB


BASEDIR = os.getcwd()
if not os.path.exists("%s/conf"%BASEDIR) or not os.path.exists("%s/log"%BASEDIR):
    BASEDIR = os.path.dirname(os.getcwd())

# 初始化logger
loggerFIle = './log/mysqlAction.log'
logger = getLogger(loggerFIle)
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
        # print("创建连接池！")
        loggerFIle = 'log/mysql.log'
        self.logger = getLogger(loggerFIle)
        # self.db_pool=PooledDB(creator=pymysql,
        #                               mincached=mincached,  #启动时开启的空连接数
        #                               maxcached=maxcached,#连接池最大可用连接数量
        #                               host=MysqlConfig['host'],
        #                               port=MysqlConfig['port'],
        #                               user=MysqlConfig['user'],
        #                               passwd=MysqlConfig['password'],
        #                               db=MysqlConfig['db'],
        #                               charset='utf8')
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
                                        charset='utf8mb4')
                break
            except Exception as e:
                logger.info("数据库连接失败，1分钟后重连")
                time.sleep(60)
    def excSql(self,sql):
        # insert update delete
        executeRet = False
        try:
            conn = self.db_pool.connection()
            cursor=conn.cursor()
            cursor.execute(sql)
            executeRet = cursor.fetchall()
            # executeRet = dict2list(executeRet)
            conn.commit()
        except(Exception) as e:
            self.logger.error(sql)
            self.logger.error(traceback.format_exc())
        return executeRet


    def getData(self,sql):
        # select
        executeRet = 0
        try:
            conn = self.db_pool.connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            # 获取返回结果
            executeRet = cursor.fetchall()
            # executeRet = dict2list(executeRet)
            conn.commit()
            conn.close()
        except(Exception) as e:
            self.logger.error(sql)
            self.logger.error(traceback.format_exc())
            raise Exception("这里报错了")
        return executeRet


    def query_data(self,query_sql):
        results=False
        try:
            conn = self.db_pool.connection()
            cursor = conn.cursor()
            cursor.execute(query_sql)
            results = cursor.fetchall()
            # keys = map(lambda k: k[0].lower(), cursor.description)
            # results = [dict(zip(keys, row)) for row in executeRet if row is not None]
            conn.commit()
        except (Exception) as error:
            self.logger.error(query_sql)
            self.logger.error(traceback.format_exc())
        return results


    def getDataByPage(self,query_sql, pageIndex, pageSize):
        ret = {}
        try:
            count_sql = "select count(*) from (" + query_sql + ") A"
            count = self.getData(count_sql)[0]

            page_sql = query_sql + " limit %s,%s" % ((int(pageIndex) - 1) * int(pageSize), pageSize)
            pageList = self.getData(page_sql)
            ret["count"] = count[0]
            ret["pageList"] = pageList
        except (Exception) as error:
            self.logger.error(query_sql)
            self.logger.error(traceback.format_exc())
        return ret

    def fetchData(self,sql):
        # self.logger.info("fetchSql : %s" %sql)
        # 连接数据库
        status = 0
        executeRet = ()
        try:
            conn = self.db_pool.connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            executeRet = cursor.fetchall()
            # executeRet=dict2list(executeRet)
            status = 1
        except(Exception) as e:
            self.logger.error(sql)
            self.logger.error(traceback.format_exc())
        return (status,executeRet)
    # def dict2list(dictObjlist):
    #     listObjlist=[]
    #     for dictObj in dictObjlist:
    #         listObj=[]
    #         for item in dictObj:
    #             if type(dictObj[item])==bytes:
    #                 listObj.append(str(dictObj[item],encoding = "utf8"))
    #             else:
    #                 listObj.append(dictObj[item])
    #         listObjlist.append(listObj)
    #     return listObjlist
    def execSql(self,sql):
        # self.logger.info("execSql : %s" % sql)
        # 连接数据库
        status = 0
        executeRet = ()
        try:
            conn = self.db_pool.connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            status = 1
        except(Exception) as e:
            self.logger.error(sql)
            self.logger.error(traceback.format_exc())
        return (status,executeRet)


    def excBLOB(self,sql,img):
        # 连接数据库
        executeRet = ()
        try:
            conn = self.db_pool.connection()
            cursor = conn.cursor()
            cursor.execute(sql, img)
            conn.commit()
        except(Exception) as e:
            self.logger.error(sql)
            self.logger.error(traceback.format_exc())
        return executeRet

    def transfer_string(self,tmp):
        result = pymysql.escape_string(tmp)
        return result

    def statusRecordAction(self,taskSeq, status):
        '''
        进行状态记录
        :param taskSeq:
        :param status:
        :return:
        '''

        self.logger.info("状态记录 by taskSeq: %s, status: %s" % (taskSeq, status))
        startTimeCheckSql = """SELECT startTime from wx_task_manage
            where taskSeq = \'%s\'""" % (taskSeq)
        # print(startTimeCheckSql)

        try:
            conn = self.db_pool.connection()
            cursor = conn.cursor()
            cursor.execute(startTimeCheckSql)
            startTimeCheckRet = cursor.fetchall()
            if startTimeCheckRet[0][0] is None:
                sql = """UPDATE wx_task_manage
                    set status = %s,startTime = now()
                    where taskSeq = %s""" % (status, taskSeq)
            else:
                sql = """UPDATE wx_task_manage
                    set status = %s,endTime = now()
                    where taskSeq = %s""" % (status, taskSeq)
            cursor.execute(sql)
            conn.commit()
        except (Exception) as e:
            self.logger.warn(e)

    def executeMany(self,sql,dataList):
        excCount=0
        try:
            conn = self.db_pool.connection()
            cursor = conn.cursor()
            excCount=cursor.executemany(sql, dataList)
            conn.commit()
        except Exception as e:
            logger.info(traceback.format_exc())
            logger.error(sql)
        return excCount
# if __name__ == '__main__':
#     BASEDIR = os.path.dirname(os.getcwd())
#
#     # 初始化logger
#     loggerFIle = '%s/conf/mysqlAction.conf' % BASEDIR
#     logger = FinalLogger().getConfLogger(confDir=loggerFIle)
#     # 初始化config
#     configFile = '%s/conf/moduleConfig.conf' % BASEDIR
#     confAllItems = ConfAnalysis(logger, configFile)
#
#     # 生产数据库
#     MysqlConfig = {
#         'host': confAllItems.getOneOptions('database', 'host'),
#         'port': int(confAllItems.getOneOptions('database', 'port')),
#         'user': confAllItems.getOneOptions('database', 'user'),
#         'password': confAllItems.getOneOptions('database', 'password'),
#         'db': confAllItems.getOneOptions('database', 'db'),
#         'charset': confAllItems.getOneOptions('database', 'charset'),
#     }
#
#     print(MysqlConfig)