"""WXCRM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import static
from django.conf.urls import url

from WXCRM import views
from WXCRM.view import HeartState, chatKeywordView, groupMemberView, phoneOperation
from WXCRM.view import clientView
from WXCRM.view import friendView, dictView, loginWxView, friend_onekey, operView, chatHistoryView, announceView, \
    report, quickReplyView, childMenuView, transpondView, wxChat, groupSent, knowledgeBaseView
from WXCRM.view import groupView
from WXCRM.view import taskManagerView
from WXCRM.view import wxInfoView

urlpatterns = [
    url(r'^hl/', views.login, name='login'),
    url(r'^sessionLost/', views.sessionLost, name='sessionLost'),
    url(r'^loginLost/', views.loginLost, name='loginLost'),
    url(r'^WXCRM/index/', views.index, name='index'),
    url(r'^WXCRM/main/', views.main, name='main'),
    url(r'^WXCRM/wxAccount/', views.wxAccount, name='wxAccount'),
    url(r'^WXCRM/wxFriendAdd/', views.wxFriendAdd, name='wxFriendAdd'),
    url(r'^WXCRM/friend/', friendView.friend, name='friend'),
    url(r'^WXCRM/friendMainIdList/', friendView.friendMainIdList, name='friendMainIdList'),
    url(r'^WXCRM/friendData/', friendView.friendData, name='friendData'),
    url(r'^WXCRM/client/', clientView.client, name='client'),
    url(r'^WXCRM/getMachineDic/', clientView.getMachineDic, name='getMachineDic'),
    url(r'^WXCRM/machineEdit/', clientView.machineEdit, name='machineEdit'),
    url(r'^WXCRM/machineDel/', clientView.machineDel, name='machineDel'),
    url(r'^WXCRM/group/', groupView.group, name='group'),
    url(r'^WXCRM/groupInfo/', groupView.groupInfo, name='groupInfo'),
    url(r'^WXCRM/groupSchedule/', groupView.groupSchedule, name='groupSchedule'),
    url(r'^WXCRM/groupScheduleCheck/', groupView.groupScheduleCheck, name='groupScheduleCheck'),
    url(r'^WXCRM/groupAuthCheck/', groupView.authCheck, name='authCheck'),
    url(r'^WXCRM/chat/', views.chat, name='chat'),
    url(r'^WXCRM/wxAccount/', views.wxAccount, name='wxAccount'),
    url(r'^WXCRM/wxTaskManager/', taskManagerView.wxTaskManager, name='wxTaskManager'),
    url(r'queryWxInfo/', wxInfoView.queryWxInfo, name='queryWxInfo'),
    url(r'createWxInfo/', wxInfoView.createWxInfo, name='createWxInfo'),
    url(r'editWxInfo/', wxInfoView.editWxInfo, name='editWxInfo'),
    url(r'delWxInfo/', wxInfoView.delWxInfo, name='delWxInfo'),
    url(r'refreshWxInfo/', wxInfoView.refreshWxInfo, name='refreshWxInfo'),
    url(r'queryWxTask/', taskManagerView.queryWxTask, name='queryWxTask'),
    url(r'createWxTask/', taskManagerView.createWxTask, name='createWxTask'),
    url(r'startWxTask/', taskManagerView.startWxTask, name='startWxTask'),
    url(r'stopWxTask/', taskManagerView.stopWxTask, name='stopWxTask'),
    url(r'delWxTask/', taskManagerView.delWxTask, name='delWxTask'),
    url(r'createGetIp/', wxInfoView.createGetIp, name='createGetIp'),
    url(r'wxAccountInfoQuery/', taskManagerView.wxAccountInfoQuery, name='wxAccountInfoQuery'),
    url(r'addFriendTaskCreate/', taskManagerView.addFriendTaskCreate, name='addFriendTaskCreate'),
    url(r'randomChatTaskCreate/', taskManagerView.randomChatTaskCreate, name='randomChatTaskCreate'),
    url(r'commentTaskCreate/', taskManagerView.commentTaskCreate, name='commentTaskCreate'),
    url(r'bootTask/', taskManagerView.bootTask, name='bootTask'),
    url(r'^WXCRM/wxChatInfo/', wxChat.wxChatInfo, name='wxChatInfo'),
    url(r'^WXCRM/getNotice/', views.getNotice, name='getNotice'),
    url(r'^WXCRM/dict/', dictView.dict, name='dict'),
    url(r'^WXCRM/knowledgeBaseEntry/', knowledgeBaseView.knowledgeBaseEntry, name='knowledgeBaseEntry'),
    url(r'^WXCRM/dictData/', dictView.dictData, name='dictData'),
    # url(r'^WXCRM/announce/', dictView.announce, name='announce'),
    url(r'^WXCRM/operData/', operView.operData, name='operData'),
    url(r'^WXCRM/operManage_ban/', operView.operManage_ban, name='operManage_ban'),
    # url(r'^WXCRM/operManage_start/', operView.operManage_start, name='operManage_start'),
    url(r'^WXCRM/menuAuthModify/', operView.menuAuthModify, name='menuAuthModify'),
    url(r'^WXCRM/queryWxAuthInfo/', operView.queryWxAuthInfo, name='queryWxAuthInfo'),
    url(r'^WXCRM/wxAccountAuthModify/', operView.wxAccountAuthModify, name='wxAccountAuthModify'),
    url(r'^WXCRM/operManageStart/', operView.operManageStart, name='operManageStart'),
    url(r'^WXCRM/operMenuInfo/', operView.operMenuInfo, name='operMenuInfo'),
    url(r'fileupload/', taskManagerView.fileupload, name='fileupload'),
    url(r'loginSystem/', views.loginSystem, name='loginSystem'),
    url(r'logout/', views.logout, name='logout'),
    url(r'total/', views.total, name='total'),
    url(r'getWxId/', groupView.getWxId, name='getWxId'),
    url(r'getWxFriend/', groupView.getWxFriend, name="getWxFriend"),
    url(r'saveGroupInfo/', groupView.saveGroupInfo, name="saveGroupInfo"),
    url(r'getMember/', groupView.getMember, name='getMember'),
    url(r'^WXCRM/loginWx/', loginWxView.loginWx, name='loginWx'),
    url(r'^WXCRM/loginData/', loginWxView.loginData, name='loginData'),
    url(r'^WXCRM/logoutTaskCheck/', loginWxView.logoutTaskCheck, name='logoutTaskCheck'),
    url(r'^WXCRM/loginLog/', loginWxView.login_log, name='loginLog'),
    url(r'^WXCRM/stopTaskBySeq/', loginWxView.stopTaskBySeq, name='stopTaskBySeq'),
    url(r'newcount/', views.newcount, name='newcount'),
    # url(r'getWxFlag', views.getWxFlag, name='getWxFlag'),
    url(r'^WXCRM/infoModifyMain/', views.infoModifyMain, name='infoModifyMain'),
    url(r'^WXCRM/infoCheck/', views.infoCheck, name='infoCheck'),
    url(r'^WXCRM/pwChangeConfirm/', views.pwChangeConfirm, name='pwChangeConfirm'),
    url(r'^WXCRM/friend_onekey/', friend_onekey.friend_onekey, name='friend_onekey'),
    url(r'^WXCRM/friend_sum/', friend_onekey.friend_sum, name='friend_sum'),
    url(r'^WXCRM/get_tasklist_ing/', friend_onekey.get_tasklist_ing, name='get_tasklist_ing'),
    url(r'^WXCRM/get_tasklist_pause/', friend_onekey.get_tasklist_pause, name='get_tasklist_pause'),
    url(r'^WXCRM/get_tasklist_com/', friend_onekey.get_tasklist_com, name='get_tasklist_com'),
    url(r'^friend_select/', friend_onekey.friend_select),
    url(r'^citydata/', friend_onekey.getCity),
    url(r'^get_list/', friend_onekey.selectList),
    url(r'^get_weixin_num/', friend_onekey.weixin_num),
    url(r'^get_weixin/', friend_onekey.weixin),
    url(r'^friend_add/', friend_onekey.friend_add),
    url(r'^put_task/', friend_onekey.getTask),
    url(r'^commit_task/', friend_onekey.commitTask),
    url(r'^friend_task/', friend_onekey.friend_task, name='friend_task'),
    url(r'^task_schedule/', friend_onekey.task_schedule, name='task_schedule'),
    url(r'^change_task/', friend_onekey.change_task, name='change_task'),
    url(r'^preview/', friend_onekey.preview),
    url(r'^taskReady/', friend_onekey.taskReady),
    url(r'^task_exist/', friend_onekey.taskExist),
    url(r'^wx_online/', friend_onekey.wxOnline),
    url(r'^commitTaskByFile',friend_onekey.commitTaskByFile,name='commitTaskByFile'),
    # ..................................................#
    url(r'^user_assign/', views.AccountManage, name='AccountManage'),
    url(r'^user_tracker/', views.user_time_manage, name='userTimeManage'),
    url(r'passwordChange/', views.passwordChange, name='passwordChange'),
    url(r'login_data/', views.login_data, name='login_data'),
    url(r'Menu_Data_Ban/', operView.Menu_Data_Ban, name='Menu_Ban'),
    url(r'Menu_Data_Start/', operView.Menu_Data_Start, name='Menu_start'),
    url(r'To_Creat_Task/', operView.To_Creat_Task, name='To_creat_task'),
    url(r'To_Create_Group/', operView.To_Create_Group, name='To_Create_Group'),
    # ...................................................#
    url(r'getWxFlag/', views.getWxFlag, name='getWxFlag'),
    url(r'file_download/', views.file_download, name='file_download'),
    url(r'^WXCRM/accept_img/', loginWxView.accept_img, name='accept_img'),
    url(r'^WXCRM/getGroupTaskInfo/', groupView.getGroupTaskInfo, name='getGroupTaskInfo'),
    url(r'^WXCRM/scheduleTaskAction/', groupView.scheduleTaskAction, name='scheduleTaskAction'),
    url(r'^WXCRM/scheduleByTaskSeqMian/', groupView.scheduleByTaskSeqMian, name='scheduleByTaskSeqMian'),
    url(r'^register/', loginWxView.Register, name='Register'),
    url(r'^reg_submit/', loginWxView.reg_submit, name='reg_submit'),
    url(r'^accountCreate/', loginWxView.accountCreate, name='accountCreate'),
    url(r'^WXCRM/accout_manage/', operView.oper, name='account_manage'),
    url(r'^examine/', operView.examine, name='examine'),

    url(r'^WXCRM/chatHistory/', chatHistoryView.chatHistory, name='chatHistory'),
    url(r'^WXCRM/chatHistoryData/', chatHistoryView.chatHistoryData, name='chatHistoryData'),
    url(r'^WXCRM/exportChatHistoryData/', chatHistoryView.exportChatHistoryData, name='exportChatHistoryData'),

    url(r'^WXCRM/appHeartBeat/', HeartState.appHeartBeat, name='appHeartBeat'),
    url(r'^setManager/', operView.setManager, name='setManager'),

    # ........................群发................... #
    url(r'^WXCRM/groupSentMain/', groupSent.groupSentMain, name='groupSentMain'),
    url(r'^WXCRM/groupSentIndex/', groupSent.groupSentIndex, name='groupSentIndex'),
    url(r'^WXCRM/groupSentCreate/', groupSent.groupSentCreate, name='groupSentCreate'),
    url(r'^WXCRM/chooseFriends/', groupSent.chooseFriends, name='chooseFriends'),
    url(r'^WXCRM/sentDetails/', groupSent.sentDetails, name='sentDetails'),
    url(r'^WXCRM/getGroupSentInfo/', groupSent.getGroupSentInfo, name='getGroupSentInfo'),
    url(r'^WXCRM/queryZone/', groupSent.queryZone, name='queryZone'),
    url(r'^WXCRM/queryFriends/', groupSent.queryFriends, name='queryFriends'),
    url(r'^WXCRM/addGroupSentTask/', groupSent.addGroupSentTask, name='addGroupSentTask'),
    url(r'^WXCRM/deleteSent/', groupSent.deleteSent, name='deleteSent'),
    url(r'^WXCRM/sentAgain/', groupSent.sentAgain, name='sentAgain'),
    url(r'^WXCRM/resend/', groupSent.resend, name='resend'),
    # ........................群发................... #

    # 报表新增接口
    url(r'^WXCRM/report/', report.report),
    url(r'^WXCRM/get_data_report/', report.dreport),
    url(r'^WXCRM/get_wechat_report/', report.wreport),
    url(r'^WXCRM/get_wg_report/', report.wgreport),
    url(r'^WXCRM/operReport/', report.operReport),
    url(r'^WXCRM/get_operReport/', report.get_operReport),
    url(r'^WXCRM/chatReport/', report.chatReport),
    url(r'^WXCRM/get_chatReport/', report.get_chatReport),
    url(r'^WXCRM/groupReport/', report.groupReport),
    url(r'^WXCRM/get_groupReport/', report.get_groupReport),
    url(r'^WXCRM/announce/', announceView.announce, name='announce'),
    url(r'^WXCRM/announceData/', announceView.announceData, name='announceData'),
    url(r'^WXCRM/quickReply/', quickReplyView.quickReply, name='quickReply'),
    url(r'^WXCRM/quickReplyData/', quickReplyView.quickReplyData, name='quickReplyData'),
    url(r'^WXCRM/childMenuData/', childMenuView.childMenuData, name='childMenuData'),
    url(r'^WXCRM/sysManageMenu/', childMenuView.sysManageMenu, name='sysManageMenu'),
    url(r'^WXCRM/transpond/', transpondView.transpond, name='transpond'),
    url(r'^WXCRM/transpondData/', transpondView.transpondData, name='transpondData'),
    url(r'^WXCRM/chatKeyword/', chatKeywordView.chatKeyword, name='chatKeyword'),
    url(r'^WXCRM/chatKeywordData/', chatKeywordView.chatKeywordData, name='chatKeywordData'),
    url(r'^WXCRM/chatKeywordData/', chatKeywordView.chatKeywordData, name='chatKeywordData'),

    url(r'^WXCRM/census/', report.census),
    url(r'^WXCRM/second_census/', report.second_census),
    url(r'^WXCRM/get_data_sum/',report.get_data_sum),
    url(r'^WXCRM/get_group_change/',report.get_group_change),
    url(r'^WXCRM/get_group_spread/',report.get_group_spread),
    url(r'^WXCRM/get_sdata_sum/',report.get_sdata_sum),
    url(r'^WXCRM/group_num_change/',report.group_num_change),
    url(r'^WXCRM/active_change/',report.active_change),
    url(r'^WXCRM/group_sdetail/',report.group_sdetail),
    url(r'^WXCRM/group_sdetail_report/',report.group_sdetail_report),
    url(r'^WXCRM/group_mdetail/', report.group_mdetail),
    url(r'^WXCRM/group_mdetail_report/', report.group_mdetail_report),
    url(r'^WXCRM/group_omdetail/', report.group_omdetail),
    url(r'^WXCRM/group_omdetail_report/', report.group_omdetail_report),
    url(r'^WXCRM/group_imdetail/', report.group_imdetail),
    url(r'^WXCRM/group_imdetail_report/', report.group_imdetail_report),
    url(r'^WXCRM/get_report_group/', report.get_group, name='getReportGroup'),
    url(r'^WXCRM/group_num/', report.group_num),
    # 知识库
    url(r'WXCRM/knowledgeInfoGet/', knowledgeBaseView.knowledgeInfoGet, name='knowledgeInfoGet'),
    url(r'qsInsertConfirm/', knowledgeBaseView.qsInsertConfirm, name='qsInsertConfirm'),
    url(r'qsdel/', knowledgeBaseView.qsdel, name='qsdel'),
    url(r'knowledgeGet/', knowledgeBaseView.knowledgeGet, name='knowledgeGet'),

    #群成员操作
    url(r'^WXCRM/groupMember/', groupMemberView.groupMember, name='groupMember'),
    #用户校验
    url(r'^WXCRM/phone_oper/', phoneOperation.phone_oper, name='phone_oper'),
]  # + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)

urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATICFILES_DIR)
