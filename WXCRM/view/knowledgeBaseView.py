import json
import traceback

from lib.DateEncoder import DateEncoder
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import mySqlUtil
import pymysql


from lib.FinalLogger import getLogger
# 初始化logger
loggerFIle = 'log/knowledegBase.log'
logger = getLogger(loggerFIle)

def knowledgeBaseEntry(request):
    if request.method == 'GET':
        oper_id = request.session['oper_id']
        oper_name = request.session['oper_name']


    creatorSql = """SELECT A.creator,B.viewName FROM `knowledge_base` A
                        join wx_system_operator B on A.creator = B.oper_id
                        GROUP BY A.creator,B.viewName"""
    creatorList = mySqlUtil.getData(creatorSql)
    return render(request, "knowledgeBase.html",{'creatorList': list(creatorList)})

@csrf_exempt
def knowledgeInfoGet(request):
    try:
        if request.method == 'GET':
            pageShowNum = int(request.GET.get('pageShowNum'))
            keyWord = request.GET.get('keyWord')
            creatorId = request.GET.get('creatorId')
            oper_id = request.session['oper_id']
            oper_name = request.session['oper_name']

            if creatorId == "0":
                creatorId = ""
            pageIndex = request.GET.get('pageIndex')
            pageNum = int(pageIndex)


        pageStart = (pageNum - 1) * pageShowNum
        pageNum = pageShowNum

        if creatorId and keyWord :
            knowledgeInfoSql = """SELECT A.classificationCode,A.classificationName, A.question, A.answer, A.creator,B.viewName FROM `knowledge_base` A
                                    join wx_system_operator B on A.creator = B.oper_id
                                    order by createTime desc
                                    limit %s,%s""" % (pageStart, pageNum)
            countSql = """select count(1) from knowledge_base A"""
        else:

            sqlConditions = """ where 1=1 """
            if creatorId != "":
                sqlConditions += "and A.creator = '%s' " % creatorId
            if keyWord != "":
                sqlConditions += "and A.question like '%%%s%%'  " % keyWord

            knowledgeInfoSql = """SELECT A.seq,A.classificationCode,A.classificationName, A.question, A.answer, A.creator,B.viewName FROM `knowledge_base` A
                                            join wx_system_operator B on A.creator = B.oper_id
                                            %s
                                            order by createTime desc
                                            limit %s,%s""" % (sqlConditions,pageStart, pageNum)
            countSql = """select count(1) from knowledge_base A %s"""%(sqlConditions)

        knowledgeInfoList = mySqlUtil.getData(knowledgeInfoSql)
        countNum = mySqlUtil.getData(countSql)


        retList = {}
        index = 0
        for info in knowledgeInfoList:
            retList[index] = {'seq': info[0],
                              'classificationCode': info[1],
                              'classificationName': info[2],
                              'question': info[3],
                              'answer': info[4],
                              'creator': info[5],
                              'viewName': info[6],
                              }
            index = index + 1

        pageCount = int((int(countNum[0][0]) / pageShowNum)) + 1
        retList['countNum'] = int(countNum[0][0])
        retList['pageCount'] = pageCount
    except Exception as e:
        logger.warn(e)
    return HttpResponse(json.dumps(retList))

def qsInsertConfirm(request):
    retList = {}
    retStatus = 1
    try:
        if request.method == 'GET':
            oper_id = request.session['oper_id']
            oper_name = request.session['oper_name']
            actType = int(request.GET.get('actType'))
            actSeq = request.GET.get('actSeq','')
            qusClass = request.GET.get('qusClass','')
            qusName = request.GET.get('qusName','')
            qusAns = request.GET.get('qusAns','')
            batchList = request.GET.get('batchList','')
    except Exception as e:
        logger.warn(e)

    if actType == 1:
        try:
            insertSql = """INSERT INTO `knowledge_base` (`classificationCode`, `classificationName`, `question`, `answer`, `creator`) 
                        VALUES ('0', '%s', '%s', '%s', '%s');"""%(qusClass, qusName, qusAns, oper_id)
            mySqlUtil.excSql(insertSql)
        except Exception as e:

            retStatus = -1
            logger.warn(e)

        retList['retStatus'] = retStatus
        return HttpResponse(json.dumps(retList))
    elif actType == 2:
        try:
            updateSql = """UPDATE `wxAuto`.`knowledge_base` SET  `classificationName`='%s', `question`='%s', `answer`='%s'
                              WHERE (`seq`='%s')""" % (qusClass, qusName, qusAns, actSeq)
            mySqlUtil.excSql(updateSql)
        except Exception as e:
            logger.warn(e)
            retStatus = -1
            logger.warn(e)

        retList['retStatus'] = retStatus
        return HttpResponse(json.dumps(retList))
    elif actType == 3:
        try:
            retList = {}
            retStatus = 1
            insertValue = ""
            # batchList = batchList.decode('GBK').encode('utf-8')
            batchProcessList = batchList.split(',')

            for item in batchProcessList:
                itemSplit = item.split('|')
                classificationName = pymysql.escape_string(itemSplit[0])
                question = pymysql.escape_string(itemSplit[1])
                answer = pymysql.escape_string(itemSplit[2])
                insertValue += "('0', '%s', '%s', '%s', '%s'),"%(classificationName, question, answer, oper_id)

            insertValue = insertValue[:-1]
            # if ',' in batchList:
            #     actList = batchList[:-1]
            # else:
            #     actList = batchList

            insertSql = """INSERT INTO `knowledge_base` (`classificationCode`, `classificationName`, `question`, `answer`, `creator`)
                            VALUES %s"""%(insertValue)
            #
            mySqlUtil.excSql(insertSql)

        except Exception as e:
            retStatus = -1
            logger.warn(e)

        retList['retStatus'] = retStatus
        return HttpResponse(json.dumps(retList))


def qsdel(request):
    try:
        retList = {}
        retStatus = 1
        if request.method == 'GET':
            oper_id = request.session['oper_id']
            oper_name = request.session['oper_name']
            delSeqList = str(request.GET.get('delSeqList'))

        if ',' in delSeqList:
            delSeq = delSeqList[:-1]
        else:
            delSeq = delSeqList

        insertSql = """DELETE FROM  knowledge_base  where seq in (%s)"""%(delSeq)

        mySqlUtil.excSql(insertSql)
    except Exception as e:

        retStatus = -1
        logger.warn(e)

    retList['retStatus'] = retStatus
    return HttpResponse(json.dumps(retList))

def knowledgeGet(request):
    try:
        retList = {}
        status = False
        remark = ""
        info = {}

        if request.method == 'GET':
            oper_id = request.session['oper_id']
            keyWord = str(request.GET.get('keyWord'))

        operExistSql = """select count(1) from wx_system_operator where oper_id = '%s'"""%(oper_id)

        operExist = mySqlUtil.getData(operExistSql)[0][0]
        if operExist > 0:
            infoGetSql = """select classificationName, question, answer from knowledge_base
                            where question like '%%%s%%'""" %(keyWord)
            infoGet = mySqlUtil.getData(infoGetSql)

            for infoItem in infoGet:
                className = infoItem[0]
                question = infoItem[1]
                answer = infoItem[2]
                if className not in info:
                    info[className] = []
                info[className].append( {
                    "question" : question,
                    "answer" : answer
                })
            status = True
            remark = "success"
        else:
            remark = "fail : operator not exists"

    except Exception as e:
        remark = "fail : process error"
        logger.warn(traceback.format_exc())

    retList['status'] = status
    retList['remark'] = remark
    retList['info'] = info
    return HttpResponse(json.dumps(retList))