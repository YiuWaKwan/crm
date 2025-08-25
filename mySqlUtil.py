import traceback

import pymysql

from lib.FinalLogger import getLogger
from lib.ModuleConfig import ConfAnalysis
import os

BASEDIR = os.getcwd()

# 初始化logger
logger = getLogger('./log/mySqlUtil.log')
# 初始化config
configFile = '%s/conf/moduleConfig.conf' % BASEDIR
confAllItems = ConfAnalysis(logger, configFile)

# 生产数据库
MysqlConfig = {
    'host': confAllItems.getOneOptions('database', 'host'),
    'port': int(confAllItems.getOneOptions('database', 'port')),
    'user': confAllItems.getOneOptions('database', 'user'),
    'password': confAllItems.getOneOptions('database', 'password'),
    'db': confAllItems.getOneOptions('database', 'db'),
    'charset': confAllItems.getOneOptions('database', 'charset'),
}


def excSql(sql):
    # 连接数据库
    # logger.info(sql)
    executeRet = 0
    connection = pymysql.connect(**MysqlConfig)
    mysqlCur=connection.cursor()
    try:
        executeRet=mysqlCur.execute(sql)
        connection.commit()
    except(Exception) as e:
        logger.error(sql)
        logger.error(traceback.format_exc())
        raise Exception("哪里来的报错，回哪里去！")
    finally:
        mysqlCur.close()
        connection.close()
    return executeRet

def insert(sql):
    # 插入单行数据，返回主键
    executeRet = 0
    connection = pymysql.connect(**MysqlConfig)
    mysqlCur = connection.cursor()
    try:
        executeRet = mysqlCur.execute(sql)
        insertId = connection.insert_id()
        connection.commit()
    except(Exception) as e:
        logger.error(traceback.format_exc())
        raise Exception("哪里来的报错，回哪里去！")
    finally:
        mysqlCur.close()
        connection.close()

    if executeRet > 0:
        return insertId
    else:
        return False


def excBLOB(sql,img):
    # 连接数据库
    logger.info(sql)
    executeRet = ()
    connection = pymysql.connect(**MysqlConfig)
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, img)
            connection.commit()
    except(Exception) as e:
        logger.error(sql)
        logger.error(e)
    finally:
        connection.close()
    return executeRet

def getData(sql):
    # 连接数据库
    #logger.info(sql)
    executeRet = ()
    connection = pymysql.connect(**MysqlConfig)
    mysqlCur = connection.cursor()
    try:
        mysqlCur.execute(sql)
        executeRet = mysqlCur.fetchall()
    except(Exception) as e:
        logger.error(sql)
        logger.error(traceback.format_exc())
    finally:
        mysqlCur.close()
        connection.close()
    return executeRet


def query_data(query_sql):
    logger.info(query_sql)
    connection = pymysql.connect(**MysqlConfig)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query_sql)
            executeRet = cursor.fetchall()
            keys = map(lambda k: k[0].lower(), cursor.description)
            results = [dict(zip(keys, row)) for row in executeRet if row is not None]
            connection.commit()
    except (Exception) as error:
        logger.error(query_sql)
        logger.error(error)
    finally:
        connection.close()
    return results

def queryByPage(query_sql, pageIndex, pageSize, totalCount):
    ret = {}
    try:
        count = []
        if not totalCount:
            count_sql = "select count(*) from (" + query_sql + ") A"
            count = getData(count_sql)[0]
        else:
            count.append(totalCount)

        page_sql = query_sql + " limit %s,%s" % ((int(pageIndex) - 1) * int(pageSize), pageSize)
        pageList = getData(page_sql)
        ret["count"] = count[0]
        ret["pageList"] = pageList
    except (Exception) as error:
        logger.error(error)
    return ret

def getDataByPage(query_sql, pageIndex, pageSize):
    ret = {}
    try:
        count_sql = "select count(*) from (" + query_sql + ") A"
        count = getData(count_sql)[0]

        page_sql = query_sql + " limit %s,%s" % ((int(pageIndex) - 1) * int(pageSize), pageSize)
        pageList = getData(page_sql)
        ret["count"] = count[0]
        ret["pageList"] = pageList
    except (Exception) as error:
        logger.error(query_sql)
        logger.error(error)
    return ret

def getDictData(sql):
    # 连接数据库
    #logger.info(sql)
    executeRet = ()
    connection = pymysql.connect(host=MysqlConfig['host'], user=MysqlConfig['user'], password=MysqlConfig['password'],
                           db=MysqlConfig['db'], port=MysqlConfig['port'],
                           charset=MysqlConfig['charset'],
                           cursorclass=pymysql.cursors.DictCursor)
    try:
        cursor = connection.cursor()
        cursor.execute(sql)

        # 获取返回结果
        executeRet = cursor.fetchall()
        connection.commit()
    except(Exception) as e:
        logger.error(sql)
        logger.error(e)
    finally:
        connection.close()
    return executeRet