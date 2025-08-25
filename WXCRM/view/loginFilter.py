from django.shortcuts import render,HttpResponse,redirect,HttpResponseRedirect
import mySqlUtil, json
import MysqlDbPool
from lib.FinalLogger import getLogger
import traceback

loggerFIle = 'log/AppHeartState.log'
logger = getLogger(loggerFIle)

try:
    mySqlUtil=MysqlDbPool.MysqlDbPool()
except Exception as e:
    logger.info(traceback.format_exc())

try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object  # Django 1.4.x - Django 1.9.x

class SimpleMiddleware(MiddlewareMixin):
    def process_request(self, request):

        if request.path in ['/WXCRM/appHeartBeat/', '/favicon.ico', '/reg_submit/', '/examine/', '/register/', '/WXCRM/accept_img/',
                            '/file_download/', '/loginLost/', '/sessionLost/', '/WXCRM/phone_oper/']:
            pass
        elif request.path == '/':
            return HttpResponseRedirect('/hl/')
        elif request.path != '/loginSystem/' and request.path != '/loginSystem' and request.path != '/hl/':
            if request.session.get('oper_id',None):
                log_id = request.COOKIES.get("LOG_ID")
                if log_id is not None and log_id != "":  # 清除登录信息

                    sql = "select log_id from wx_oper_logtime where log_id='%s' and logout_time is not null" % log_id
                    login_info = mySqlUtil.getData(sql)
                    if login_info is not None and len(login_info) > 0:
                        #清理session
                        del request.session['oper_id']
                        if request.session.get('oper_name', None) is not None:
                            del request.session['oper_name']
                        if request.session.get('oper_main_wx', None) is not None:
                            del request.session['oper_main_wx']

                        respone = HttpResponseRedirect('/loginLost/')
                        #清理cookie
                        respone.delete_cookie("LOG_ID")
                        return respone
                else:
                    # 清理session
                    del request.session['oper_id']
                    if request.session.get('oper_name', None) is not None:
                        del request.session['oper_name']
                    if request.session.get('oper_main_wx', None) is not None:
                        del request.session['oper_main_wx']

                    return HttpResponseRedirect('/loginLost/')
            else:
                return HttpResponseRedirect('/sessionLost/')

        else:
            pass

    def process_response(self, request, response):
        return response
