var appWx = angular.module("appWx", ["ui.router", "ngSanitize", "ngAnimate", "ngWebSocket"]);
appWx.factory('NoticeData', function ($websocket) {
    var ws = $websocket("ws://" + location.host + "/WXCRM/getNotice/");
    //var groupNotice = [];
    var wxMainNotice = [];
    var wxNotice = [];
    var groupChatNoticeAtResult = [];
    var lastChartTime = [];
    var lastChartContent = [];
    var announceNotice = [];
    ws.onMessage(function (event) {
        //console.log('NoticeData: ', event);
        var res;
        try {
            res = JSON.parse(event.data);
            //groupNotice=res.groupNotice;
            wxMainNotice = res.wxMainNotice;
            wxNotice = res.wxNotice;
            groupChatNoticeAtResult = res.groupChatNoticeAtResult;
            lastChartTime = res.lastChartTimeNotice;
            lastChartContent = res.lastChartContentNotice;
            announceNotice = res.announceNotice
            ws.send('Hello');
        } catch (e) {
        }
    });

    window.onbeforeunload = function () {
        ws.close();
    };

    ws.onError(function (event) {
        console.log('connection Error', event);
        alert("通讯网络已中断（影响消息接收），请刷新网页重连！");
    });

    ws.onClose(function (event) {
        console.log('connection closed', event);
        alert("通讯网络已中断（影响消息接收），请刷新网页重连！");
    });

    ws.onOpen(function () {
        console.log('connection open');
        ws.send('Hello');
    });

    return {
        getMain: function () {
            return wxMainNotice;
        },
        getwx: function () {
            return wxNotice;
        },
        status: function () {
            return ws.readyState;
        },
        send: function (message) {
            if (angular.isString(message)) {
                ws.send(message);
            }
            else if (angular.isObject(message)) {
                ws.send(JSON.stringify(message));
            }
        },
        getGroupChatNoticeAtResult: function () {
            return groupChatNoticeAtResult;
        },
        getLastChartTime: function () {
            return lastChartTime;
        },
        getLastChartContent: function () {
            return lastChartContent;
        },
        getAnnounceNotice: function () {
            return announceNotice
        }
    };
});

/*配置路由信息 $stateProvider: Ui路由中的状态服务提供者*/
appWx.config(function ($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise("/contentChat");
    $stateProvider.state('contentContact', {
        url: '/contentContact',
        views: {
            'contentView': {
                templateUrl: "/static/template/contentContact.html"
            }
        }
    }).state('contentChat', {
        url: '/contentChat',
        views: {
            'contentView': {
                templateUrl: "/static/template/contentChat-2.0.html"
            }
        }
    }).state('searchList', {
        url: '/searchList',
        views: {
            'searchList': {
                templateUrl: "/static/template/searchList.html"
            },
            'contentView': {
                templateUrl: "/static/template/contentChat-2.0.html"
            }
        }
    }).state('profile', {
        url: '/profile',
        views: {
            'contentView': {
                templateUrl: "/static/template/contentChat-2.0.html"
            },
            'profile': {
                templateUrl: "/static/template/profile_mini.html"
            }
        }
    }).state('noShow', {
        url: '/noShow',
        views: {
            'contentView': {
                templateUrl: "/static/template/contentChat-2.0.html"
            }
        }
    });
});

appWx.config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});

//angularjs 中a标签中href属性带有unsafe:javascript解决方案
appWx.config(['$compileProvider', function ($compileProvider) {
    $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|tel|file|sms|javascript):/);//此处是正则表达式
}]);
appWx.filter('to_trusted', ['$sce', function ($sce) {
    return function (text) {
        return $sce.trustAsHtml(text);
    };
}]);


appWx.controller('appController', function($scope, $state, $interval,$http,NoticeData,$timeout, $templateCache) {
    //未读消息通知服务
    $scope.NoticeData=NoticeData;
    $scope.profileStyle={"top": "0px","left":"0px"};
    //当前面板内容
    $scope.state_current_name = 'chat';
    $scope.groups=[];

    //当前主号列表
    $scope.wxInfos=[];
    $scope.wxInfosAt=[];//用于展示@信息的微信列表
    //当前主号资料
    $scope.account = {pic:'\\static\\img\\header_none.png', pic_big:'\\static\\img\\header_none.png'};
    $scope.accountAt = {pic:'\\static\\img\\header_none.png', pic_big:'\\static\\img\\header_none.png'};//用于记录艾特的主号
    //聊天记录列表
    $scope.chatList = [{NickName:'暂无列表', pic:'', pic_big:'', isTop:false, SendMin:'', NoticeCount:0, LastChart:''}];
    $scope.chatListAt = [{NickName:'暂无列表', pic:'', pic_big:'', isTop:false, SendMin:'', NoticeCount:0, LastChart:''}];
    //通信录
    $scope.allContacts = [];
    //当前联系人
    $scope.currentContact={show:false,UserName:''};
    $scope.profileContact={};
    $scope.chatContent=[];//单次聊天记录数据，每次10条
    $scope.chatContentDB=[];//存放全量数据
    //新消息数量
    $scope.newsCount=0;
    //是否显示下来菜单
    $scope.contextMenuFlag={};
    $scope.selectList=[];//选择微信列表
    $scope.chooseWxId="";//当前点击微信
    $scope.memberList=[];//群成员列表
    $scope.friendFlagList=[];
    $scope.showPanel="panel_wx";//显示群成员列表模块 panel_wx 或者 @我的消息模块 panel_at
    $scope.groupChatNoticeAtCtrls={};
    $scope.groupChatAtCount=0;
    $scope.totalCount=0;
    $scope.dialog_notice=false;
    $scope.noticeList=[];
    $scope.isClickAt = "";
    $scope.quickReplyList=[];//快捷回复列表
    $scope.dialog_quickReply=false;//是否显示快捷回复对话框
    $scope.chatKeywordList=[];//关键字列表
    $scope.mainWxMenuFlag={};//微信主号列表中的点击…显示的功能列表
    $scope.choose_at_index = 0; //全部聊天默认选择第一个主号
    $scope.choose_wx_index  = 0;  //艾特会话默认选择第一个主号

    $scope.groupMemberInfoExt={"headPic":"","group_member_name":""};//用于群聊界面展示群成员信息（基础信息）
    $scope.groupMemberFlags=[];//用于群聊界面展示群成员信息（标签信息）
    $scope.ifEditMemberInfo=false;//用于标识是否修改群成员信息
    $scope.sexList=[];//用于存储字典表中的性别数据

    $scope.customInfo = {}; //客户信息

    //初始化默认设置
    $scope.contextMenuFlag.transpond = false;
    $scope.welcomeMask = false;

    //好友标签字段
    $.ajax({
        type: 'get',
        url: '/WXCRM/friendData',
        data: {"type":"getFlagData"},
        success: function (res) {
            severcheck(res);
            res = parseJson(res);
            var list = res.flagList;
            if (list != null && list.length > 0) {
                for(var i=0;i<list.length;i++){
                    $scope.friendFlagList.push({dic_value:list[i][0],dic_name:list[i][1]})
                }
            }
        }
    });

    //临时策略 500毫秒执行一次
    $scope.flushDate = function () {
        try {
            $scope.totalCount = 0;
            angular.forEach($scope.wxInfos, function (wxInfo, key) {
                var mainNotice = $scope.NoticeData.getMain();
                if (wxInfo.wx_id in mainNotice) {
                    if (mainNotice[wxInfo.wx_id] > wxInfo.NoticeCount) {
                        if ($("#msgNoticePlayer")[0]) {
                            //播放声音
                            $("#msgNoticePlayer")[0].play();
                        }
                    }
                    wxInfo.NoticeCount = mainNotice[wxInfo.wx_id];
                    $scope.totalCount += wxInfo.NoticeCount;
                } else {//若微信通知数量大于0，且不在最新通知中有，则置0
                    if (wxInfo.NoticeCount > 0) {
                        wxInfo.NoticeCount = 0;
                    }
                }
            });
            //只关心当前主号的
            if ($scope.NoticeData.getwx()[$scope.account.wx_id] != undefined) {
                var wxNotice = $scope.NoticeData.getwx()[$scope.account.wx_id];
                var lastChartTimeList = $scope.NoticeData.getLastChartTime()[$scope.account.wx_id];
                var lastChartContentList = $scope.NoticeData.getLastChartContent()[$scope.account.wx_id];
                var check = [];
                angular.forEach($scope.chatList, function (chat, key) {
                    if (wxNotice[chat.wx_id] != undefined) {
                        chat["NoticeCount"] = wxNotice[chat.wx_id];
                        if (chat.SendMin != null && chat.SendMin != '' && lastChartTimeList[chat.wx_id] != null) {
                            chat["SendMin"] = new Date(Date.parse(lastChartTimeList[chat.wx_id].replace(/-/g, "/"))).format('yyyy-MM-dd hh:mm');
                        }
                        chat["LastChart"] = lastChartContentList[chat.wx_id];
                        check.push(chat.wx_id);  //匹配过就丢掉
                        if ($scope.currentContact.wx_id == chat.wx_id && !$scope.currentContact.isAtSession) {
                            //$scope.modifyWx('flush_chat',$scope.currentContact.wx_id);//切换时先清空微信本地数据库记录，从数据库重新获取，避免前一微信号窗口接收消息时快速切换到新微信号窗口时，导致前一微信号接收消息遗漏的问题
                            $scope.currentContact["NoticeCount"] = chat["NoticeCount"];
                            $scope.chatNoticeShowing();
                        }
                    } else {
                        chat["NoticeCount"] = 0;
                    }
                });

                for (var item in wxNotice) {//新聊天人员添加
                    if (check.indexOf(item) == -1) {
                        angular.forEach($scope.allContacts, function (chat, key) {
                            if (chat.wx_id == item) {
                                $scope.chatList.push({
                                    NickName: chat.NickName,
                                    pic: chat.pic,
                                    pic_big: chat.pic_big,
                                    isTop: chat.isTop,
                                    SendMin: new Date(Date.parse(lastChartTimeList[chat.wx_id].replace(/-/g, "/"))).format('yyyy-MM-dd hh:mm'),
                                    NoticeCount: wxNotice[item],
                                    LastChart: lastChartContentList[chat.wx_id],
                                    RemarkName: chat.RemarkName,
                                    wx_id: chat.wx_id,
                                    show: true
                                });
                            }
                        });
                    }
                }
            } else {
                angular.forEach($scope.chatList, function (chat, key) {//清理聊天列表的未读数量
                    if (chat.NoticeCount > 0) {
                        chat.NoticeCount = 0;
                    }
                });
            }

            //@我的消息数据提醒
            $scope.groupChatNoticeAtCtrls = $scope.NoticeData.getGroupChatNoticeAtResult();
            $scope.groupChatAtCount = 0;
            angular.forEach($scope.wxInfosAt, function (wxInfo, key) {
                var mainNotice = $scope.groupChatNoticeAtCtrls.wxMainNotice;
                if (mainNotice != undefined && mainNotice[wxInfo.wx_id] != undefined) {
                    wxInfo.NoticeCount = mainNotice[wxInfo.wx_id];
                    $scope.groupChatAtCount += wxInfo.NoticeCount;
                } else {//若微信通知数量大于0，且不在最新通知中有，则置0
                    if (wxInfo.NoticeCount > 0) {
                        wxInfo.NoticeCount = 0;
                    }
                }
            });
            //只关心当前主号的
            if ($scope.groupChatNoticeAtCtrls.wxNotice != undefined && $scope.groupChatNoticeAtCtrls.wxNotice[$scope.accountAt.wx_id] != undefined) {
                var wxNotice = $scope.groupChatNoticeAtCtrls.wxNotice[$scope.accountAt.wx_id];
                var lastChartTimeList = $scope.groupChatNoticeAtCtrls.lastChartTimeNotice[$scope.accountAt.wx_id];
                var lastChartContentList = $scope.groupChatNoticeAtCtrls.lastChartContentNotice[$scope.accountAt.wx_id];
                var check = [];
                angular.forEach($scope.chatListAt, function (chat, key) {
                    var key = chat.memberId + "__" + chat.wx_id;
                    if (wxNotice[key] != undefined && wxNotice[key] > 0) {
                        chat["NoticeCount"] = wxNotice[key];
                        if (chat.SendMin != null && chat.SendMin != '' && lastChartTimeList[key] != null) {
                            chat["SendMin"] = new Date(Date.parse(lastChartTimeList[key].replace(/-/g, "/"))).format('yyyy-MM-dd hh:mm');
                        }
                        chat["LastChart"] = lastChartContentList[key];
                        check.push(key);  //匹配过就丢掉
                        if ($scope.currentContact.wx_id == chat.wx_id && $scope.currentContact.isAtSession && $scope.currentContact.memberId == chat.memberId) {
                            //$scope.modifyWx('flush_chat',$scope.currentContact.wx_id);//切换时先清空微信本地数据库记录，从数据库重新获取，避免前一微信号窗口接收消息时快速切换到新微信号窗口时，导致前一微信号接收消息遗漏的问题
                            $scope.currentContact["NoticeCount"] = chat["NoticeCount"];
                            $scope.chatNoticeShowing();
                        }
                    } else {
                        chat["NoticeCount"] = 0;
                    }
                });

                if ($scope.groupChatNoticeAtCtrls.chatListAt && $scope.groupChatNoticeAtCtrls.chatListAt.length > 0) {
                    var chatListAt_temp = $scope.groupChatNoticeAtCtrls.chatListAt;
                    var newAt = [];
                    angular.forEach(chatListAt_temp, function (tchat, tkey) {
                        if (tchat.wx_main_id == $scope.accountAt.wx_id) {
                            var flag = true;
                            angular.forEach($scope.chatListAt, function (chat, key) {
                                if (chat.seq_id == tchat.seq_id) {
                                    flag = false;
                                    return false;
                                }
                            });
                            if (flag) {
                                newAt.push(tchat);
                            }
                        }
                    });
                    if (newAt.length > 0) {
                        $scope.chatListAt = $scope.chatListAt.concat(newAt);
                    }
                }
            } else {
                angular.forEach($scope.chatListAt, function (chat, key) {//清理聊天列表的未读数量
                    if (chat.NoticeCount > 0) {
                        chat.NoticeCount = 0;
                    }
                });
            }

            //处理公告信息
            //$scope.handleAnnounceData();
        } catch (ex) {
            console.log(ex);
        }
    };
    $interval($scope.flushDate, 500);
    //$scope.timer=$timeout(function(){ $scope.flushDate();}, 2000);//使用timeout才可以避免主号新消息数量提示不消除的问题，用interval会导致数据库还未清理，notice又获取了数量

    //处理公告开始
    $scope.announceMapLength=0;
    $scope.announceMap = {
		set : function(key,value){this[key] = value;$scope.announceMapLength++},
		get : function(key){return this[key]},
		contains : function(key){return this.get(key) == null?false:true},
		remove : function(key){delete this[key];$scope.announceMapLength--}
	};
    $scope.indexAnnounceMap = {
		set : function(key,value){this[key] = value;},
		get : function(key){return this[key]},
		contains : function(key){return this.get(key) == null?false:true},
		remove : function(key){delete this[key];}
	};
    $scope.handleAnnounceData=function() {
       //var announceData = $scope.NoticeData.getAnnounceNotice();
        var announceData = $scope.getAnnounceData();
       if (announceData != null) {
           for (var i = 0; i < announceData.length; i++) {
               var aSeqId = announceData[i][0];
               if (!$scope.announceMap.contains(aSeqId)) {//如果当前没有弹出当前公告，则新弹窗口
                   var announceContent = announceData[i][3];
                   var index = layer.open({
                       title: '公告'
                       , area: ['300px', '240px']//宽高
                       , type: 1
                       , offset: 'rb' //具体配置参考：http://www.layui.com/doc/modules/layer.html#offset
                       , id: 'layer'+$scope.announceMapLength //防止重复弹出 第一个弹出层不能用index，否则为undefined，因此用map的长度
                       , content: announceContent
                       //,btn: '关闭全部'
                       //,btnAlign: 'c' //按钮居中
                       , shade: 0 //不显示遮罩
                       , cancel: function (index, layero) {
                               //alert(aSeqId);
                               layer.close(index);
                               $scope.writeAnnounceViewHis(index);
                               //$scope.announceMap.remove(aSeqId);

                       }
                   });
                   $scope.indexAnnounceMap.set(index, aSeqId);
                   $scope.announceMap.set(aSeqId, index);
               }
           }
       }
    };
    $scope.getAnnounceData=function(){//回调函数中只能传index,传aSeqId则会传全局变量覆盖每个关闭层的aSeqId,都是一样的值导致写浏览记录不正常
       var noticeData;
       $.ajax({
            type: "GET",
            async:false,
            url: "http://"+window.location.host+"/WXCRM/wxChatInfo/",
            data: {"oper":"getAnnounceNotice"},
            success: function (result) {
                severcheck(result);
                result = parseJson(result);
                noticeData=result;
            },
            error: function (XMLHttpRequest, textStatus, errorThrown, data) {
                alert(JSON.stringify(data));// 请求失败执行代码
            }
        });
       return noticeData;
    };
    $scope.writeAnnounceViewHis=function(index){//回调函数中只能传index,传aSeqId则会传全局变量覆盖每个关闭层的aSeqId,都是一样的值导致写浏览记录不正常
        $.ajax({
            type: "GET",
            url: "http://"+window.location.host+"/WXCRM/wxChatInfo/",
            data: {"oper":"writeAnnounceViewHis","seqId":$scope.indexAnnounceMap.get(index)},
            success: function (result) {
                severcheck(result);
            },
            error: function (XMLHttpRequest, textStatus, errorThrown, data) {
                alert(JSON.stringify(data));// 请求失败执行代码
            }
        });
    };//处理公告结束
    //处理公告信息 
    $interval($scope.handleAnnounceData, 1000*60*5);

    //获取主号
    $.ajax({
        type: "GET",
        url: "http://"+window.location.host+"/WXCRM/wxChatInfo/",
        async: true,
        data: {"oper":"getGroupInfo"},
        success: function (result) {
            severcheck(result);
            result = parseJson(result);
            //$scope.groups=result.retGroup;
            $scope.wxInfos=result.retList;
            $scope.wxInfosAt = JSON.parse(JSON.stringify($scope.wxInfos))
        },
        error: function (XMLHttpRequest, textStatus, errorThrown, data) {
            alert(JSON.stringify(data));// 请求失败执行代码
        }
    });

    //查看客户信息
    $scope.showCustomInfo = function () {
        $.ajax({
            type: "GET",
            url: "http://" + window.location.host + "/WXCRM/wxChatInfo/",
            data: {
                "oper": "getWxInfo",
                "wx_id": $scope.currentContact.wx_id,
                "wx_main_id": $scope.account.wx_id,
                'member_id': $scope.currentContact.memberId
            },
            success: function (result) {
                severcheck(result);
                result = parseJson(result);
                if (result.customInfo) {
                    $scope.customInfo = result.customInfo;
                    $scope.groupInfo = {};
                }
                else if (result.groupInfo) {
                    $scope.groupInfo = result.groupInfo;
                    $scope.customInfo = {}
                }
            },
            error: function (XMLHttpRequest, textStatus, errorThrown, data) {
                alert(JSON.stringify(data));// 请求失败执行代码
            }
        });
    };

    //监控当前群成员人变化
    $scope.$watch('groupMemberInfoExt', function (nVal, oVal) {
        if(nVal.member_wx_id) {
            $scope.customInfo = {
                pic: nVal.headPic,
                pic_big: nVal.headPic,
                NickName: nVal.group_member_name,
                remarkName: nVal.real_name,
                phone: nVal.phone,
                sex: nVal.sexName,
                birthday: nVal.birthday,
                zone: nVal.areaFullName,
                address: nVal.address,
                flags:$scope.groupMemberFlags
            }
            $scope.groupInfo = {};
        }
    });

    $scope.clearAtMsg=function(wxMainId,wxGroupId,wxId){
        $.ajax({
            type: "GET",
            url: "http://" + window.location.host + "/WXCRM/wxChatInfo/",
            async: true,
            data: {
                "oper": "clearAtMsg",
                "wxMainId": wxMainId,
                "wxGroupId": wxGroupId,
                "wxId": wxId
            },
            success: function (result) {
                severcheck(result);
            },
            error: function (XMLHttpRequest, textStatus, errorThrown, data) {
            }
        })
    };
    $scope.chooseWx=function(wx,index){
        $scope.choose_wx_index = index;
        $scope.currentContact={show:false,UserName:''}; //切换时清理当前聊天界面
        $scope.account=wx;
        $scope.allContacts=[];
        $scope.chatList=[];
        //从后台查询
        $http({
            method: 'GET',
            url: 'http://'+window.location.host+'/WXCRM/wxChatInfo/?oper=getFriendInfo&wx_main_id='+$scope.account.wx_id,
            data:{}
        }).then(function successCallback(response) {
                severcheck(response.data);
                $scope.allContacts=response.data.allContacts;
                $scope.chatList=response.data.chatList;
                //console.log(typeof($scope.chatList[0].SendMin))
                if($scope.chatList.length==0){
                    $scope.chatList = [{NickName:'暂无列表', pic:'', pic_big:'', isTop:false, SendMin:'', NoticeCount:0, LastChart:'',RemarkName:'暂无列表'}];
                }else{
                    angular.forEach($scope.chatList, function(chat, key) {
                         if (chat.SendMin!=null&&chat.SendMin!='') {
                             chat.SendMin = new Date(Date.parse(chat.SendMin.replace(/-/g, "/"))).format('yyyy-MM-dd hh:mm')
                         }
                    })
                }
            }, function errorCallback(response) {
                alert(JSON.stringify(response));//请求失败执行代码
                $scope.chatList = [{NickName:'暂无列表', pic:'', pic_big:'', isTop:false, SendMin:'', NoticeCount:0, LastChart:'',RemarkName:'暂无列表'}];
        });
    };
    $scope.chooseWxAt=function(wx,index){
        $scope.state_current_name = "chat"; //切换到聊天列表
        $scope.choose_at_index = index;
        $scope.currentContact={show:false,UserName:''}; //切换时清理当前聊天界面
        $scope.account=wx;
        $scope.accountAt=wx;
        $scope.chatListAt=[];
        //从后台查询
        $http({
            method: 'GET',
            url: 'http://'+window.location.host+'/WXCRM/wxChatInfo/?oper=getChatAtInfo&wx_main_id='+$scope.account.wx_id,
            data:{}
        }).then(function successCallback(response) {
                severcheck(response.data);
                $scope.chatListAt=response.data.chatList;
                //console.log(typeof($scope.chatList[0].SendMin))
                if($scope.chatListAt.length==0){
                    $scope.chatListAt = [{NickName:'暂无列表', pic:'', pic_big:'', isTop:false, SendMin:'', NoticeCount:0, LastChart:'',RemarkName:'暂无列表'}];
                }else{
                    angular.forEach($scope.chatListAt, function(chat, key) {
                        chat.isAtSession = true;
                         if (chat.SendMin!=null&&chat.SendMin!='') {
                             chat.SendMin = new Date(Date.parse(chat.SendMin.replace(/-/g, "/"))).format('yyyy-MM-dd hh:mm')
                         }
                    })
                }
            }, function errorCallback(response) {
                alert(JSON.stringify(response));//请求失败执行代码
                $scope.chatListAt = [{NickName:'暂无列表', pic:'', pic_big:'', isTop:false, SendMin:'', NoticeCount:0, LastChart:'',RemarkName:'暂无列表'}];
        });
    };

    //聊天和联系人切换
    $scope.clickChat=function(current_name){
        $scope.state_current_name=current_name;
    };
    //联系人详细信息显示
    $scope.contactShow=function(contactItem){
        $scope.currentContact=contactItem;
        $state.go('contentContact');
    };

    //关闭艾特会话
    $scope.closeMessage = function(){
        if ($scope.currentContact.seq_id) {
            var at_id = $scope.currentContact.seq_id;
            $.ajax({
                type: 'get',
                async: false,
                url: "http://" + window.location.host + "/WXCRM/wxChatInfo/",
                data: {
                    "at_id": at_id,
                    "oper":"closeAtSession"
                },
                success: function (data) {
                    severcheck(data);
                    data = parseJson(data);
                    if (data && data.flag) {
                        $scope.currentContact={show:false,UserName:''}; //关闭时清理当前聊天界面
                        for(var j = 0,len = $scope.chatListAt.length; j < len; j++){
                            var v = $scope.chatListAt[j];
                            if(v.seq_id == at_id){
                                $scope.chatListAt.splice(j, 1);
                                if($scope.chatListAt.length <= 0){
                                    $scope.chatListAt = [{NickName:'暂无列表', pic:'', pic_big:'', isTop:false, SendMin:'', NoticeCount:0, LastChart:'',RemarkName:'暂无列表'}];
                                }
                                break;
                            }
                        }
                    }else{
                        console.log("后台删除失败")
                    }
                }
            });
        }
    };

    //聊天信息显示
    $scope.chatShow=function(contactItem,index){
        // $scope.modifyWx('flush_chat',contactItem.wx_id);//切换时先清空微信本地数据库记录，从数据库重新获取，避免前一微信号窗口接收消息时快速切换到新微信号窗口时，导致前一微信号接收消息遗漏的问题
        $scope.state_current_name='chat';
        $scope.noticeList=[];
        $scope.memberList=[];
        //debugger;
        $scope.currentContact=contactItem;
        setTimeout(function () {
            if($scope.currentContact.isAtSession && $scope.currentContact.memberId){//获取群成员资料
                getMemberInfo($scope.currentContact.memberId,$scope.currentContact.pic,$scope.currentContact.memberName);
            }else {
                $scope.showCustomInfo();
            }
        }, 1000); //刷新客户信息


        //先获取聊天记录，如果有则直接读取前台(并跟数据库做对比，如果不同步，则直接全量同步--暂不做)，如果没有则从数据库加载,直接加载上限 max_store_list
        if(useIndexedDB) { //放开本地数据库 by JMing 20190426
            myIndexedDb.getDataByKey("wx_table", $scope.account.wx_id + "_" + $scope.currentContact.wx_id);
        }else{
            $scope.chatShowing([]); //每次切换都已经清除了聊天记录，因此不再本地获取
        }
    };

    $scope.showFace=function(content){
        if(content){
            var reg = /\[([^\]]+)\]/g;
            content = content.replace(reg, function($1){
                face=$1.replace('[','').replace(']','');
                if($scope.QQFaceMap.hasOwnProperty(face)){
                    return "<img class='qqemoji qqemoji"+$scope.QQFaceMap[face]+"' src='/static/img/wx/spacer.gif'>";
                }else if($scope.QQFaceMap.hasOwnProperty("<"+face+">")){
                    return "<img class='emoji emoji"+$scope.QQFaceMap["<"+face+">"]+"' src='/static/img/wx/spacer.gif'>";
                }
                return $1;
            });
        }
        return content;
    };

    $scope.chatShowing=function (messageList) {
        //debugger;
        var contactItem=$scope.currentContact;
        var first_time_load = false;
        if(messageList.length == 0){
            //查询数据库获取100条记录，往上滚动时再加载100条(滚动的后续实现，先实现显示)
            //如果存在记录则，将记录写入本地数据库
            $.ajax({
                type: 'get',
                async: false,
                url: "http://"+window.location.host+"/WXCRM/wxChatInfo/",
                data: {"wx_id":contactItem.wx_id,"wx_main_id":$scope.account.wx_id,"limit_num":myIndexedDb.max_store_list,"oper":"loadChatHis"},
                success: function(data){
                    severcheck(data);
                    data = parseJson(data);
                    if(data && data.chatList){
                        messageList=data.chatList.reverse();
                        first_time_load=true;
                    }
                }
            });
        }

        var newChatList=[];
        if (contactItem.NoticeCount && contactItem.NoticeCount > 0) {
            //服务器清零通知,并读取消息
            $.ajax({
                type: "GET",
                url: "http://"+window.location.host+"/WXCRM/wxChatInfo/",
                async: false,
                data: {"oper":"loadChat",
                    "wx_id":$scope.currentContact.wx_id,
                    "wx_main_id":$scope.account.wx_id,
                    "member_id":$scope.currentContact.memberId,
                    "chatAt":$scope.currentContact.chatAt
                },
                success: function (result) {
                    severcheck(result);
                    result = parseJson(result);
                    if(result.chatList.length >0){
                        //聊天通知信息
                        angular.forEach(result.chatList, function(item, key) {
                            item["pic"]=contactItem.pic;
                            item["NickName"]=contactItem.NickName;
                            newChatList.push(item);
                            if(item["content"].indexOf("@") != -1){
                                $scope.clearAtMsg($scope.account.wx_id, $scope.currentContact.wx_id,item["group_member_id"]);
                            }
                        });
                    }
                },
                error: function (XMLHttpRequest, textStatus, errorThrown, data) {}
            });
        }

        $scope.chatContent=[];
        $scope.chatContentDB=[];
        //初始化(读数据库或缓存消息)

        if(messageList && messageList.length>0){
            angular.forEach(messageList, function(item, key){
                $scope.chatContentDB.push(item);
            });
            //还需要合并未读消息
            if(newChatList.length > 0){
                angular.forEach(newChatList, function(item, key) {
                    $scope.chatContentDB.push(item);
                });
            }
            if(first_time_load){
                var tempChatContentDB=[];
                angular.forEach($scope.chatContentDB, function(item, key){
                    tempChatContentDB.push(item);
                });
                $scope.saveChatList(tempChatContentDB);
            }else{
                $scope.saveChatList(newChatList);
            }
        }else{
            if(newChatList.length > 0){
                $scope.chatContentDB = newChatList;
                $scope.saveChatList(newChatList);
            }
        }

        $scope.formatTimeShow();
        //获取前面10条记录先显示，后续滚动到最顶端加载更多
        var loopFlag=10;
        if($scope.isClickAt != ""){
            var atShow=false;//用于标识at的消息是否 已经被弹出展示，若已弹出且当前窗口未满10条，则继续弹出其他消息
            for(var i=0; i<$scope.chatContentDB.length; i++){
                if($scope.chatContentDB.length > 0){
                    var chatItem = $scope.chatContentDB.pop();
                    $scope.chatContent.unshift(chatItem);
                    if(chatItem.msgId == $scope.isClickAt){
                        //break;
                        atShow=true; //找到艾特消息为止
                    }
                }
                if(atShow&&(i>9||i==$scope.chatContentDB.length-1)){
                    //
                      //$scope.scroollWindows("chat_main");//滚动条滚到窗口的底端
                      $scope.scroollWindows($scope.isClickAt);
                    break;
                }

            }
        }else{
            for(var i=0; i<25; i++){
                if($scope.chatContentDB.length > 0){
                    $scope.chatContent.unshift($scope.chatContentDB.pop());
                }
            }
            $scope.scroollWindows("chat_main");
        }

        $state.go('contentChat');
        $scope.isClickAt = "";

    };//end for chatshowing

    $scope.chatNoticeShowing=function () {
        var contactItem=$scope.currentContact;

        var newChatList=[];
        if (contactItem.NoticeCount && contactItem.NoticeCount > 0) {
            //服务器清零通知,并读取消息
            $.ajax({
                type: "GET",
                url: "http://"+window.location.host+"/WXCRM/wxChatInfo/",
                async: false,
                data: {"oper":"loadChat",
                    "wx_id":$scope.currentContact.wx_id,
                    "wx_main_id":$scope.account.wx_id,
                    "isCurrent":1,
                    "member_id":$scope.currentContact.memberId,
                    "chatAt":$scope.currentContact.chatAt
                }, //#isCurrent:如果是当前聊天界面加载消息，为避免消息遗漏，删除时根据msgID删
                success: function (result) {
                    severcheck(result);
                    result = parseJson(result);
                    if(result.chatList&&result.chatList.length >0){
                        //聊天通知信息
                        angular.forEach(result.chatList, function(item, key) {
                            item["pic"]=contactItem.pic;
                            item["NickName"]=contactItem.NickName;
                            newChatList.push(item);
                            if(item["content"].indexOf("@") != -1){
                                $scope.clearAtMsg($scope.account.wx_id, $scope.currentContact.wx_id,item["group_member_id"]);
                            }
                            //console.log($scope.currentContact.RemarkName+", 读出消息："+item.content);
                        });
                    }
                },
                error: function (XMLHttpRequest, textStatus, errorThrown, data) {}
            });
        }

        //console.log("————————批次分隔符————————");
        angular.forEach(newChatList, function(item, key) {
            item.MMActualContent=$scope.showFace(item.content);
            $scope.chatContent.push(item);
            //console.log("newChatListc插入时间："+new Date()+"->"+$scope.currentContact.RemarkName+", chatNoticeShowing读出消息2："+item.content);
        });
        if(newChatList && newChatList.length > 0){
            $scope.saveChatList(newChatList);
            $scope.scroollWindows("chat_main",1);
        }
    };


    //时间相同的记录只显示一个
    $scope.formatTimeShow=function () {
        if($scope.chatContentDB.length > 0){
            var tmpTime="-";
            for(var i=0;i< $scope.chatContentDB.length;i++){
                $scope.chatContentDB[i].showTime = true;
                $scope.chatContentDB[i].MMActualContent=$scope.showFace($scope.chatContentDB[i].content);
                if(tmpTime == $scope.timeShow($scope.chatContentDB[i].SendMin)){
                    $scope.chatContentDB[i].showTime = false;
                }
                else{
                    tmpTime=$scope.timeShow($scope.chatContentDB[i].SendMin);
                }
            }
        }
    };

    $scope.searchMsg = function(){
        $scope.keywordQuickReplyFilter = $scope.keywordQuickReply;
    };

    $scope.draftTextMessage=function(){

        $scope.currentContact.draft = $("#editArea").html();
    };
    //发送聊天信息
    $scope.sendTextMessage=function(fileObject){
        if($("#editArea").html().trim().replace(/[\r\n]/g, "") == '' && !fileObject && $scope.noticeList.length==0){
            return false;
        }
        $scope.currentContact.draft = '';//清除草稿
        var group_member_name = "",group_member_id="";
        // 艾特会话时记录成员信息
        if($scope.currentContact.isAtSession){
            group_member_name = $scope.currentContact.memberName;
            group_member_id = $scope.currentContact.memberId;
        }

        var myDate = new Date();
        var sendmin = myDate.getHours() + ":" + myDate.getMinutes();
        var sendMinFull=myDate.format("yyyy-MM-dd hh:mm");
        var message={};
        var content="";
        var noticeName="";
        var noticeIdList="";
        var notice="";
        if($scope.noticeList.length>0){
            angular.forEach($scope.noticeList, function(item, key) {
                if(noticeName == ""){
                    noticeName=item.name.replace(' ','').replace('@','');
                    noticeIdList=item.wx_id;
                }
                else{
                    noticeName=noticeName+"|"+item.name.replace(' ','').replace('@','');
                    noticeIdList=noticeIdList+","+item.wx_id;
                }
                notice=notice+item.name;
            });
        }
        var msgId=(new Date()).valueOf() * 1000 + Math.round(Math.random() * 1000);
        if(fileObject){
            message={MsgType:fileObject.MsgType,MMIsSend:true,SendMin:sendMinFull,pic:$scope.account.pic,NickName:$scope.account.NickName,
                filename:fileObject.filename,filesize:fileObject.filesize,
                FileExt:fileObject.FileExt,FileStatus:1,content:fileObject.content, "msgId":msgId};
            content=fileObject.filename+"|"+fileObject.FileExt+"|"+fileObject.filesize+"|"+fileObject.totallen+"|1|"+fileObject.content;
        }
        else{
            content=$("#editArea").html();
            var subStr=new RegExp('<img.*?text="', 'gm');//创建正则表达式对象<*> </>
            var content=content.replace(subStr,"");//替换为空字符串
            subStr = new RegExp('" src=".*?">', 'gm');
            content=content.replace(subStr,"");//替换为空字符串
            subStr = new RegExp(' style=".*?"', 'gm');
            content=content.replace(subStr,"");//替换为空字符串

            content= content.replace(/<[^>]+>/g,"");//去掉所有的html标记
            if(content.length>2048){
                alert("聊天内容过长，最多不能超过2048字！")
                return false;
            }
            if(content.length<=0 && $scope.noticeList.length <= 0){
                return false;
            }
            message={MsgType:1,MMIsSend:true,SendMin:sendMinFull,pic:$scope.account.pic,NickName:$scope.account.NickName,
                MMActualContent:notice + $("#editArea").html(),content:notice+content, "msgId":msgId};
        }
        message.group_member_name = group_member_name;
        message.group_member_id = group_member_id;
        $scope.chatContent.push(message);
        //往后台写任务
        message.LastChart = chatTypeTranslate(message.MMActualContent, message.MsgType)

        //客户端更新聊天
        var update = false;
        angular.forEach($scope.chatList, function(item, key) {
            if ($scope.currentContact.wx_id == item.wx_id) {
                item.LastChart=message.LastChart;
                item.SendMin=sendMinFull;
                update=true;
            }
        });

        if(!update){
            if($scope.chatList.length == 1 && $scope.chatList[0].NickName == '暂无列表'){
                $scope.chatList=[];
            }
            chatItem={'show':true,'MMIsSend':true,'NickName':$scope.currentContact.NickName,'wx_id':$scope.currentContact.wx_id,
                'pic':$scope.currentContact.pic, 'pic_big':$scope.currentContact.pic, 'isTop':$scope.currentContact.isTop,
                'SendMin':sendMinFull, 'NoticeCount':0, 'LastChart':message.LastChart,RemarkName:$scope.currentContact.RemarkName};
            $scope.chatList.push(chatItem);
        }
        //服务器写入聊天记录和聊天任务
        $.ajax({
            type: "GET",
            url: "http://"+window.location.host+"/WXCRM/wxChatInfo/",
            async: true,
            data: {
                "oper":"saveChat",
                "wx_id":$scope.currentContact.wx_id,
                "wx_main_id":$scope.account.wx_id,
                'content':content,
                "type":message.MsgType,
                "noticeName":noticeName,
                "noticeIdList":noticeIdList,
                "msgId":msgId,
                "group_member_name":group_member_name,
                "group_member_id":group_member_id
            },
            success: function (result) {
                severcheck(result);
            },
            error: function (XMLHttpRequest, textStatus, errorThrown, data) {
                var errorTips=showAjaxError("发送消息",XMLHttpRequest,errorThrown);
                message={MsgType:5,MMIsSend:false,SendMin:sendMinFull,pic:$scope.account.pic,NickName:$scope.account.NickName,
                MMActualContent:errorTips,content:errorTips, "msgId":msgId+"0"};
                $scope.chatContent.push(message);
                $scope.saveChat(message);
                $timeout($scope.scroollWindows("chat_main"), 500);
            }
        });
        angular.element("#editArea").html('');
        $scope.noticeList=[];//清理@
        //记录本地缓存
        $scope.saveChat(message);
        $scope.scroollWindows("chat_main");
    };

    $scope.saveChat=function(message){
        if(useIndexedDB){
            myIndexedDb.updateDataByKey("wx_table", $scope.account.wx_id+"_"+$scope.currentContact.wx_id ,message ,myIndexedDb.store_param.object);
        }
    };
    $scope.saveChatList=function(messageList){
        if(useIndexedDB){
            myIndexedDb.updateDataByKey("wx_table", $scope.account.wx_id+"_"+$scope.currentContact.wx_id ,messageList ,myIndexedDb.store_param.list);
        }
    };

    //语音播放控制
    $scope.playVoice=function(message){
        if(!message.MMPlaying){//语音播放
            message.MMPlaying=true;
            message.isNext=false;
            if(message.voiceUnRead == 1){
                message.isNext=true;
                message.voiceUnRead=0;
                $scope.saveContent(message, "voiceRead", message.content+"|"+message.VoiceLength+"|0" , myIndexedDb.update_param.voice);
            }
            $("#voiceMsgPlayer source").attr("src", message.content);
            $("#voiceMsgPlayer")[0].load();
            $("#voiceMsgPlayer").on('pause',message, function(){if(message.MMPlaying){message.MMPlaying=false;$scope.playVoiceNext(message);}});
            $("#voiceMsgPlayer").on('ended',message, function(){if(message.MMPlaying){message.MMPlaying=false;$scope.playVoiceNext(message);}});
            $("#voiceMsgPlayer")[0].play();
        }
        else {//播放暂停  一定要先设置message.MMPlaying=false 才能调用pause函数
            if($("#voiceMsgPlayer")){message.MMPlaying=false;$("#voiceMsgPlayer")[0].pause();}
        }
    };
    //播放下一个没被播放的语音
    $scope.playVoiceNext=function(message){
        if(message.isNext){
            //下一个语音准备
            var nextFlag = false;
            for(var i=0; i<$scope.chatContent.length; i++){
                var chatItem = $scope.chatContent[i];
                if(!nextFlag){
                    if(chatItem.msgId == message.msgId && chatItem.MsgType == message.MsgType){
                        nextFlag=true;
                    }
                }
                else{
                    if(chatItem.MsgType == 6 && chatItem.voiceUnRead == 1){
                        $scope.playVoice(chatItem);
                        break;
                    }
                }
            }
        }
    };
    //保存页面更改过的content数据
    $scope.saveContent=function (message, oper, content, type) {
        //本地库表更新
        myIndexedDb.updateContentByKey("wx_table", $scope.account.wx_id+"_"+$scope.currentContact.wx_id ,message, type);

        var wx_name_tmp = $scope.currentContact.RemarkName;
        if($scope.currentContact.isAtSession){
            wx_name_tmp = $scope.currentContact.NickName; //艾特会话时取群名称
        }

        //服务器库表更新
        $.ajax({
            type: "GET",
            url: "http://"+window.location.host+"/WXCRM/wxChatInfo/",
            async: true,
            data: {
                "oper":oper,
                "wx_id":$scope.currentContact.wx_id,
                "wx_name":wx_name_tmp,
                "wx_main_id":$scope.account.wx_id,
                'content':content,
                "msgid":message.msgId
            },
            success: function (result) {
                severcheck(result);
                result = parseJson(result);
                if(result){
                   if(result.code == -1) {
                       if (myIndexedDb.update_param.filestate == type) {
                           message.FileStatus = 3;
                           myIndexedDb.updateContentByKey("wx_table", $scope.account.wx_id + "_" + $scope.currentContact.wx_id, message, type);
                       }
                   }
                   else if(result.code == 0 && result.taskSeq){//6秒获取一下结果
                       taskSeq = result.taskSeq;
                       $interval($scope.getTaskResult, 1000, 10, true, message, taskSeq, type);
                   }
                   else if(result.code == 1){//已下载成功
                       message.FileStatus = 1;
                       message.content = result.content;
                       message.taskResult = "成功";
                       myIndexedDb.updateContentByKey("wx_table", $scope.account.wx_id+"_"+$scope.currentContact.wx_id ,message, type);
                       if(message.MsgType == 7){
                           $scope.startVideo(message.content);
                       }
                   }
                }
            },
            error: function (XMLHttpRequest, textStatus, errorThrown, data) {
                    if(myIndexedDb.update_param.filestate == type){
                        message.FileStatus = 3;
                        myIndexedDb.updateContentByKey("wx_table", $scope.account.wx_id+"_"+$scope.currentContact.wx_id ,message, type);
                    }
            }
        });
    };

    $scope.downloadFile= function (message) {
        if(message.FileStatus == 1 && message.content.indexOf("http") != -1){//视频
            $scope.startVideo(message.content);
            return true;
        }

        message.FileStatus = 2;
        message.taskResult = "排队中...";
        var content = message.filename+"|"+message.FileExt+"|"+message.filesize+"|"+message.totallen+"|2|"+message.content;
        $scope.saveContent(message, "downloadFile", content, myIndexedDb.update_param.filestate);
    };

    $scope.downloadPicture= function () {
        //alert("任务已提交，约需要耗时30秒！");//打开这个会时，不点确认就不会开始下载
        $scope.picMessage.taskResult="下载中...";
        $scope.saveContent($scope.picMessage, 'downloadFile', '', myIndexedDb.update_param.filestate);
    };

    $scope.joinNewFriend=function (message, oper, desc) {
        if(confirm("确定"+desc+"吗？")){
            //服务器库表更新
            $.ajax({
                type: "GET",
                url: "http://"+window.location.host+"/WXCRM/wxChatInfo/",
                async: true,
                data: {
                    "oper": oper,
                    "wx_id": $scope.currentContact.wx_id,
                    "wx_name": $scope.currentContact.RemarkName,
                    "wx_main_id": $scope.account.wx_id,
                    "des": message.des,
                    "title": message.title,
                    "msgid": message.msgId
                },
                success: function (result) {
                    severcheck(result);
                    result = parseJson(result);
                    if(result){
                       if(result.code == 0) {
                           alert("已经添加任务，请耐心等待，不要频繁操作！");
                       }
                    }
                }
            });
        }
    };

    $scope.startVideo= function (content) {
        $("#videoPlayer source").attr("src", content);
        $("#videoPlayer")[0].load();
        $scope.showVideo=true;
        document.getElementById("videoPlayer").play();
    };
    $scope.stopVideo= function () {
        document.getElementById('videoPlayer').pause();
        $scope.showVideo=false;
    };

    //5秒钟执行一次，直到超时，有结果就终止调
    $scope.getTaskResult= function (message, taskSeq, type) {
        $.ajax({
            type: "GET",
            url: "http://"+window.location.host+"/WXCRM/wxChatInfo/",
            async: true,
            data: {
                "oper":"getTaskResult",
                "taskSeq":taskSeq,
                "wx_id":$scope.currentContact.wx_id,
                "wx_main_id":$scope.account.wx_id,
                "msgid":message.msgId
            },
            success: function (result) {
                severcheck(result);
                result = parseJson(result);
                //console.log("http://"+window.location.host+"/WXCRM/wxChatInfo/?oper=getTaskResult&&taskSeq="+taskSeq);
                if(result){
                   if(result.code == -1) {
                        message.FileStatus = 3;
                   }
                   else if(result.code == 0 && result.status){
                       if(result.status == "1"){
                            message.taskResult = "排队中...";
                       }else if(result.status == "2"){
                            message.taskResult = "下载中...";
                       }else if(result.status == "3"){
                            message.FileStatus = 3;
                            message.taskResult = "下载失败";
                            myIndexedDb.updateContentByKey("wx_table", $scope.account.wx_id+"_"+$scope.currentContact.wx_id ,message, type);
                       }else if(result.status == "4"){
                            message.FileStatus = 1;
                            message.content = result.content;
                            message.taskResult = "成功";
                            myIndexedDb.updateContentByKey("wx_table", $scope.account.wx_id+"_"+$scope.currentContact.wx_id ,message, type);
                       }else if(result.status == "5"){
                            message.taskResult = "下载失败";
                            message.FileStatus = 3;
                            myIndexedDb.updateContentByKey("wx_table", $scope.account.wx_id+"_"+$scope.currentContact.wx_id ,message, type);
                       }
                   }
                }
            },
            error: function (XMLHttpRequest, textStatus, errorThrown, data) {
            }
        });
    };
    //显示图片
    $scope.showPig=function(src){
        var pic_height = 0;
        var pic_width = 0;
        $scope.prePic = "";
        $scope.nextPic = "";
        $scope.picMessage = {};//消息体
        $("img[name='msg_pic']").each(function(){
            if(this.src == src){
                pic_height = this.height;
                pic_width = this.width;
                $scope.downloadPic = "0";
                if(this.getAttribute("file-state") != "" && this.getAttribute("file-state") != "1"){
                    $scope.downloadPic = "1";
                }
                var msgId = this.getAttribute("msgId");
                angular.forEach($scope.chatContent, function(item, key) {if(item.msgId == msgId) { $scope.picMessage = item}});
            }
            else if (pic_height == 0){
                $scope.prePic = this.src;
            }
            else if($scope.nextPic == ""){
                $scope.nextPic = this.src;
            }
        });

        var targetWidth = window.innerWidth * 0.8;
        var targetHeight = window.innerHeight * 0.8;
        if(pic_width * targetHeight/pic_height <=  targetWidth){
            targetWidth = pic_width * targetHeight/pic_height;
        }
        else if(pic_height * targetWidth/pic_width <=  targetHeight){
            targetWidth = pic_height * targetWidth/pic_width;
        }

        //如果放大超过了3倍，就按3倍来显示
        if(targetHeight / pic_height > 3){
            targetWidth = pic_width * 3;
            targetHeight = pic_height * 3;
        }
        if(targetWidth / pic_width > 3){
            targetWidth = pic_width * 3;
            targetHeight = pic_height * 3;
        }

        var top = (window.innerHeight - targetHeight) / 5;
        var left = (window.innerWidth - targetWidth) / 2;

        $scope.picSrc=src;
        $scope.showPic=true;
        if (! $scope.picMessage.taskResult){
            $scope.picMessage.taskResult="查看原图";
        }
        $scope.showPicStyle="width: " + targetWidth + "px; height: " + targetHeight + "px; top: " + top + "px; left: " + left + "px;";
    };

    $scope.closePig=function(src){
        $scope.showPic=false;
    };

    $scope.scroollWindows=function(id,notClearEditArea){
        var afterSend = function () {
            //滚动条自动滚动
            var t;
            if(id=='chat_main'){
               t=$('#'+id)[0].scrollHeight;//用于聊天对话框滚动条在最底端，展示最新消息
            }else{
               t = $('#'+id).offset().top;//用于@消息的某一条距chat_main顶端的高度，便于定位
            }
            $('#chat_main').scrollTop(t);
            if(notClearEditArea!=1){
                angular.element("#editArea").html('');
            }
            if($scope.currentContact.draft){
                $("#editArea").html($scope.currentContact.draft);

                var noticeList = [];
                angular.forEach($("input.content_at"),function (item, key) {
                var v = $(item).val();
                var item_id=$(item).attr("wx_id");
                if(v) {
                    noticeList.push({"name": v,"item_id":item_id})
                }
        });
        $scope.noticeList = noticeList;
            }
        };
        $interval(afterSend, 50, 1);
    };
    //账户资料浮动页面
    $scope.showProfile=function(event,contactItem,message){
        if(message&&message.group_member_id!=null){//获取群成员资料
                getMemberInfo(message.group_member_id,message.headpic,message.group_member_name);
        }
        $scope.profileContact=contactItem;
        var e = event || window.event;
        var profileX = e.clientX;
        var profileY = e.clientY;
        if(window.innerWidth-profileX < 220) {profileX=profileX-220}
        if(window.innerHeight-profileY < 334) {profileY=profileY-334}
        // $scope.profileStyle={"top": profileY,"left": profileX};
        // $state.go('profile');
        event=event||window.event;
        event.stopPropagation();//阻止事件冒泡,防止隐藏
    };
    //微信好友查找
    $scope.searchKeyup=function(){
        if($scope.keyword == ''){
            $state.go('noShow');
            return false;
        }
        $state.go('searchList');
    };

    $scope.showExpression=function(event){
        $scope.showBiaoQing=1;
        $scope.biaoQingIndex=1;
        event=event||window.event;
        event.stopPropagation();//阻止事件冒泡,防止隐藏
    };
    //关闭弹窗窗
    document.addEventListener("click",function(){
        if((!$scope.foucus && $("#profile").html() != '') || $("#mmpop_search").html() != ''){
            $state.go('noShow');
        }
        if($scope.showBiaoQing==1) {
            $scope.showBiaoQing=0;
        }
        $scope.contextMenuFlag.isShowContextMenu=false;
        $scope.dialog_notice=false;
        $scope.dialog_quickReply=false;
        $scope.mainWxMenuFlag.isShowMainWxMenu=false;

    });

    document.getElementById("search_bar").addEventListener("click",function(event){//搜索栏
        var e=event||window.event;
        e.stopPropagation();//阻止事件冒泡,防止隐藏
    });
    document.getElementById("profile_show").addEventListener("click",function(event){//名片
        var e=event||window.event;
        e.stopPropagation();//阻止事件冒泡,防止隐藏
    });
    document.getElementById("contextMenu").addEventListener("click",function(event){//右键件菜单
        var e=event||window.event;
        e.stopPropagation();//阻止事件冒泡,防止隐藏
    });
    document.getElementById("ngdialog_notice").addEventListener("click",function(event){//邮件菜单
        var e=event||window.event;
        e.stopPropagation();//阻止事件冒泡,防止隐藏
    });
    document.getElementById("ngdialog_quickReply").addEventListener("click",function(event){//邮件菜单
        var e=event||window.event;
        e.stopPropagation();//阻止事件冒泡,防止隐藏
    });
    document.getElementById("ngdialogInfo").addEventListener("click",function(event){
        var e=event||window.event;
        e.stopPropagation();//阻止事件冒泡,防止隐藏
    });
    //选择表情
    $scope.selectEmoticon=function(event){
        var obj=event.target;
        var type=obj.getAttribute("type");
        var text=obj.innerText;
        var face="";
        var classStr="";
        if(type == "qq"){
            face=text;
            classStr="qqemoji qqemoji";
            text="["+text+"]";
        }else if(type == "emoji"){
            face="<"+text+">";
            text="["+text+"]";
            classStr="emoji emoji";
        }
        if($scope.QQFaceMap.hasOwnProperty(face)){
            classStr=classStr+$scope.QQFaceMap[face];
            var targetHtml="<img class='"+classStr+"' text='"+text+"' src='/static/img/wx/spacer.gif'>";
            angular.element("#editArea").append(targetHtml);
        }
    }
    $scope.editAreaKeydown=function(event){
        if(!$("#editArea").html()){
            return true;
        }
        if (event.ctrlKey && event.keyCode == 13){
            return true;
        }
        else if(event.keyCode == 13){
            if($scope.currentContact.state != 3) {
                $scope.sendTextMessage();
                return false;
            }else {
                return true;
            }
        }
    };

    //资料修改
    $scope.showDialog=function(flag){
        if("transpond" == flag){//转发对话框
            if(($scope.contextMenuFlag.content_type == "3" || $scope.contextMenuFlag.content_type == "7") && $scope.contextMenuFlag.FileStatus != 1){
                alert("需要先把文件下载下来才能转发！");
                return false;
            }
        	$scope.contextMenuFlag.transpond=true;
        	return true;
        }
        else if("dialog_notice" == flag){//@的对话框
            $scope.contextMenuFlag.menu_wx_id=$scope.currentContact.wx_id;
            $("#loading").show();
        }
        else if("dialog_quickReply" == flag){//@的对话框
            //$scope.contextMenuFlag.menu_wx_id=$scope.currentContact.wx_id;
            $("#loading").show();
        }
        else{//右键对话框
            $scope.contextMenuFlag.dialog_show=true;
            $scope.contextMenuFlag.dialog_flag=flag;
            $scope.contextMenuFlag.isShowContextMenu=false;
        }

        if("remark_dialog" == flag){
            $scope.contextMenuFlag.dialog_name="修改备注";
            $scope.contextMenuFlag.dialog_value=$scope.contextMenuFlag.remark_dialog;
        }
        else if("setflag" == flag){
            $scope.contextMenuFlag.dialog_name="客户标注";
        }
        else if("group_notice" == flag){
            $scope.contextMenuFlag.dialog_name="修改群公告";
            $scope.contextMenuFlag.dialog_value=$scope.contextMenuFlag.group_notice_dialog;
        }
        else if("group_wx_name" == flag){
            $scope.contextMenuFlag.dialog_name="修改我在群里的昵称";
            $scope.contextMenuFlag.dialog_value="";
        }
        else if("add_member" == flag){
            $scope.contextMenuFlag.dialog_name="增加成员";
            $("#add_member_div").html("");
        }
        else if("del_member" == flag){
            $scope.contextMenuFlag.dialog_name="删除成员";
            $("#delete_member_div").html("");
        }
        if(flag == 'setflag'){
            $("select[name='setflag']").select2('val', '');
            $.ajax({
                type: 'get',
                url: "http://"+window.location.host+"/getWxFlag/",
                data: {"wx_id":$scope.contextMenuFlag.group_id_dialog,"wx_main_id":$scope.account.wx_id},
                success: function (res) {
                    severcheck(res);
                    res = parseJson(res);
                    if(res.flag && res.flag.length > 0){
                        $("select[name='setflag']").select2('val',res.flag.split(','));
                    }
                }
            });
        }
        if("add_member" == flag || "del_member" == flag || "dialog_notice" == flag){
            if("add_member" == flag || "del_member" == flag){
                $scope.memberList = [];
            }

            if($scope.memberList.length == 0){
                $.ajax({
                    type: 'get',
                    url: "http://"+window.location.host+"/WXCRM/wxChatInfo/",
                    data: {"groupId":$scope.contextMenuFlag.menu_wx_id,"wx_main_id": $scope.account.wx_id, "oper":"getGroupMember"},
                    success: function (res) {
                        severcheck(res);
                        res = parseJson(res);
                        if(res.memberList && res.memberList.length > 0){
                            $scope.memberList=res.memberList;
                            $scope.memberListUpdate();
                        }
                    }
                });
            }

            if("dialog_notice" == flag) {//@的对话框
                $scope.memberListUpdate();
                $scope.dialog_notice = true;
                $("#loading").hide();
                var e = event||window.event;
                var profileX = e.clientX;
                var profileY = e.clientY;
                $("#ngdialog_notice").attr("style","top:" + (profileY-273)+";left:"+profileX);
                e.stopPropagation();//阻止事件冒泡,防止隐藏
            }
        }

         if("dialog_quickReply" == flag) {//快捷回复的对话框
            $scope.dialog_quickReply = true;
            $("#loading").hide();
            var e = event||window.event;
            var profileX = e.clientX;
            var profileY = e.clientY;
            $("#ngdialog_quickReply").attr("style","top:" + (profileY-273)+";left:"+profileX);
            e.stopPropagation();//阻止事件冒泡,防止隐藏
        }
    };

    $scope.openSelectMemeber=function(e){
        angular.forEach($scope.allContacts, function(contact, key0) {
            contact.memberflag=0;
            angular.forEach($scope.memberList, function(member, key1) {
                if(member.wx_id == contact.wx_id){
                    contact.memberflag=1;
                }
            });

            $("#add_member_div").children('div').each(function(){
                data = $(this).attr("data");
                if(data.indexOf(contact.wx_id) != -1)
                {
                    contact.memberflag=1;
                }
            });
        });
        $scope.contextMenuFlag.dialog_add_friend=true;
    };

    $scope.addMember=function(){
        var htmlcontent="";
        $.each($('input:checkbox:checked') ,function() {
            var imgurl="";
            var wx_id="";
            var wx_name="";
            var dataValue=$(this).attr("data");
            if(dataValue != ""){
                imgurl=dataValue.split('|')[2];
                wx_id=dataValue.split('|')[0];
                wx_name=dataValue.split('|')[1];
                dataValue=wx_id+"|"+wx_name;
            }
            if(imgurl == ""){
                imgurl="\\static\\img\\qun.jpg"
            }
            var deleteFun="<i class='icon web_wechat_delete' style='top: -65px;' onclick='$(event.target.parentElement).remove();'></i>";
            htmlcontent+="<div class='img_show_div' name='imgvalue' data='"+dataValue+"'>" +
                "<img style='width:40px; height:40px; border: 1px solid #ddd;' src='"+imgurl+"' >" +
                "<span title='"+wx_name +"' style='display:inline-block;width:40px;overflow: hidden;white-space: nowrap;text-overflow: ellipsis;font-size: 11px'>"+wx_name+"</span>" +
                deleteFun+"</div>";
        });
        $("#add_member_div").append(htmlcontent);
        $scope.contextMenuFlag.dialog_add_friend=false;
    };

    //用户资料修改
    $scope.modifyWx=function(modify_type, wx_id){
        $scope.contextMenuFlag.isShowContextMenu=false;
        $scope.contextMenuFlag.dialog_show=false;

        if(modify_type == "flush_chat"){
            myIndexedDb.deleteDataByKey(myIndexedDb.store_name, $scope.account.wx_id+"_"+wx_id);
            return false;
        }
        else if(modify_type == "head"){
            var flag=false;
            angular.forEach($scope.noticeList, function(notice, key1) {
                if(notice.name == $scope.contextMenuFlag.headname){
                    flag=true;
                }
            });
            if(!flag){
                $scope.noticeList.push({"name":$scope.contextMenuFlag.headname,"wx_id":$scope.contextMenuFlag.cur_msg_wx_id})
                $("#editArea").append("<input type='button' value='"+$scope.contextMenuFlag.headname+"' wx_id='"+$scope.contextMenuFlag.cur_msg_wx_id+"' disabled  class='content_at'>");
            };
            $scope.memberListUpdate();
            return false;
        }
        else if(modify_type == "notice"){
            var tmpList=[];
            angular.forEach($scope.noticeList, function(notice, key1) {
                if(notice.wx_id != $scope.contextMenuFlag.cur_msg_wx_id){
                    tmpList.push(notice);
                }
            });
            $scope.noticeList=tmpList;
            $scope.contextMenuFlag.isShowContextMenu=false;
            $scope.memberListUpdate();
            return false;
        }
        var content="";
        var flag="";
        var group_id="";
        if(modify_type == "remark"){
            content=$(event.target).html();
            if(content=="<br>"){content="";}
            if(content){content=content.replace("<br>","");}
            if($scope.currentContact.RemarkName!=content && content!=""){
                $scope.currentContact.RemarkName=content;
            }
            else if(content==""){
                $scope.currentContact.RemarkName=$scope.currentContact.NickName;
            }
        }
        else if(modify_type == "remark_dialog"){
            modify_type="remark";
            content=$("#remark_dialog").html();
            if(content){content=content.replace("<br>","");}
            angular.forEach($scope.chatList, function(chat, key) {
                if(chat.wx_id == wx_id){
                    if(chat.RemarkName!=content && content!=""){
                        chat.RemarkName=content;
                    }
                    else if(content==""){
                        chat.RemarkName=$scope.currentContact.NickName;
                    }
                }
            });
            angular.forEach($scope.allContacts, function(chat, key) {
                if(chat.wx_id == wx_id){
                    if(chat.RemarkName!=content && content!=""){
                        chat.RemarkName=content;
                    }
                    else if(content==""){
                        chat.RemarkName=$scope.currentContact.NickName;
                    }
                }
            });
        }
        else if(modify_type == "group_notice"){
            group_id=wx_id
            wx_id=$scope.account.wx_id
            content=$("#group_notice").html();
            if(content){content=content.replace("<br>","");}
        }
        else if(modify_type == "group_wx_name"){
            group_id=wx_id
            wx_id=$scope.account.wx_id
            content=$("#group_wx_name").html();
            if(content){content=content.replace("<br>","");}
        }
        else if(modify_type == "del_member"){
            group_id=wx_id
            wx_id=$scope.account.wx_id
            content="";
            $("#delete_member_div").children('div').each(function(){
                if(content==""){
                   content=$(this).attr("data");
                }
                else{
                    content=content+"#"+$(this).attr("data");
                }
            });

            if(content==""){
                alert("请选择要删除的成员");
                $scope.dialog_show=true;
                return false;
            }
        }
        else if(modify_type == "add_member"){
            group_id=wx_id;
            wx_id=$scope.account.wx_id;
            content="";
            $("#add_member_div").children('div').each(function(){
                if(content==""){
                   content=$(this).attr("data");
                }
                else{
                    content=content+"#"+$(this).attr("data");
                }
            });

            if(content==""){
                alert("请选择要加入的成员");
                $scope.dialog_show=true;
                return false;
            }
        }
        else if(modify_type == "setTop" || modify_type == "cancelTop"){
            angular.forEach($scope.chatList, function(chat, key) {
                if(chat.wx_id == wx_id){
                    if(modify_type == "setTop"){chat.isTop=true;}
                    if(modify_type == "cancelTop"){chat.isTop=false;}
                }
            });
        }
        else if(modify_type == "closeChat"){
            var chatListTmp=[];
            angular.forEach($scope.chatList, function(chat, key) {
                if(chat.wx_id != wx_id){
                    chatListTmp.push(chat);
                }
            });
            $scope.chatList=chatListTmp;
        }
        else if(modify_type == "setflag"){
            var selectValue=$("select[name='setflag']").select2("val");
            if(!selectValue){
                return false;
            }

            flag = selectValue.join(",");
        }
        else if(modify_type == "hide_group"){

        }

        $.ajax({
            method: 'POST',
            url: 'http://'+window.location.host+'/WXCRM/wxChatInfo/',
            data:{"oper": "modifyWx", "wx_main_id":$scope.account.wx_id, "wx_id":wx_id, "modify_type":modify_type, "content":content,"flag":flag,"group_id":group_id},
            success: function (ret) {
                severcheck(ret);
                ret = parseJson(ret);
                if(ret.code != 1){
                    alert(ret.msg);
                }
                else{
                    if(modify_type == "hide_group"){
                        alert("已经隐藏，刷新页面后群信息将不再显示。");
                    }
                    else if(modify_type != "setflag" && modify_type != "closeChat" && modify_type != "setTop" && modify_type != "cancelTop"){
                        alert("本次操作已经提交，需要耐心等待后台执行完成。");
                    }

                }
            }
        });
    };

    $scope.transpond=function(){
        $scope.contextMenuFlag.transpond=false;
        if($scope.selectList.length == 0){
            return false;
        }
        if($scope.selectList.length > 9){
            alert("每次转发不能超过9位好友，请重新选择！");
            return false;
        }
        /*
        if($scope.selectList.length > 18){
            if(!confirm("在短时间内转发过多会存在封号风险，请谨慎操作，确定需要转发？")){
                return false;
            }
        }

        if($scope.selectList.length > 50){
            alert("本次转发超过50位好友，为预防封号，禁止此操作！");
            return false;
        }
*/
        var target_wx_list = "";
        angular.forEach($scope.selectList, function(selectItem, key) {
            if(target_wx_list == ""){
                target_wx_list=selectItem.wx_id;
            }
            else{
                target_wx_list=target_wx_list+","+selectItem.wx_id;
            }
        });

        // 艾特会话时记录成员信息
        var group_member_name = '',group_member_id='';
        if($scope.currentContact.isAtSession){
            group_member_name = $scope.currentContact.memberName;
            group_member_id = $scope.currentContact.memberId;
        }
        $.ajax({
            method: 'POST',
            url: 'http://'+window.location.host+'/WXCRM/wxChatInfo/',
            data:{'wx_main_id':$scope.account.wx_id,
                'wx_id':$scope.currentContact.wx_id,
                'target_wx_list': target_wx_list,
                'content':$scope.contextMenuFlag.transpond_content,
                'type' : $scope.contextMenuFlag.content_type,
                'oper':'transpond',
                'group_member_name' : group_member_name,
                'group_member_id' : group_member_id
            },
            success: function (ret) {
                severcheck(ret);
                //alert("已提交转发任务");
                ret = parseJson(ret);
                if(ret.lastChartContentNotice){//更新最后聊天内容
                    var lastChartContent = ret.lastChartContentNotice[$scope.account.wx_id];
                    var lastChartTime = ret.lastChartTimeNotice[$scope.account.wx_id];
                    angular.forEach($scope.chatList, function (chat, key) {
                        if (lastChartContent[chat.wx_id] != undefined) {
                            if (chat.SendMin!=null && chat.SendMin!='' && lastChartTime[chat.wx_id] != null) {
                                chat["SendMin"] = new Date(Date.parse(lastChartTime[chat.wx_id].replace(/-/g, "/"))).format('yyyy-MM-dd hh:mm');
                            }
                            chat["LastChart"] = lastChartContent[chat.wx_id];
                        }
                    });
                }

            },
            error: function (XMLHttpRequest, textStatus, errorThrown, data) {
                alert(JSON.stringify(data));// 请求失败执行代码
            }
        });
    };

    $scope.addNoticeName=function(headname,wx_id){
        var flag=false;
        headname="@"+headname+" ";
        angular.forEach($scope.noticeList, function(notice, key1) {
            if(notice.wx_id == wx_id){
                flag=true;
            }
        });
        if(!flag){
            $scope.noticeList.push({"name":headname,"wx_id":wx_id})
            $("#editArea").append("<input type='button' value='"+headname+"' wx_id='"+wx_id+"' disabled  class='content_at'>");
        };
        $scope.memberListUpdate();
        $scope.draftTextMessage();
    };
    //艾特列表变化同步
    $scope.changeNoticeName=function(event){
        if (!(event.keyCode == 46 || event.keyCode == 12 || event.keyCode == 8 || event.type == "paste")){
            return true;
        }

        var noticeList = [];
        angular.forEach($("input.content_at"),function (item, key) {
            var v = $(item).val();
            var item_id = $(item).attr("wx_id");
            if(v) {
                noticeList.push({"name": v,"wx_id":item_id})
            }
        });
        $scope.noticeList = noticeList;
        // console.log($scope.noticeList);
    };

    $scope.selectWx=function(item){
        $scope.chooseWxId=item.wx_id;
        if($scope.isCheck(item.wx_id)){
            var newList=[];
            angular.forEach($scope.selectList, function(selectItem, key) {
                if(selectItem.wx_id != item.wx_id){
                    newList.push(selectItem);
                }
            });
            $scope.selectList=newList;
        }
        else{
            $scope.selectList.push({'wx_id':item.wx_id, 'pic':item.pic, 'RemarkName':item.RemarkName});
        }
    };

    $scope.delUser=function(wx_id){
        var newList=[];
        angular.forEach($scope.selectList, function(selectItem, key) {
            if(selectItem.wx_id != wx_id){
                newList.push(selectItem);
            }
        });
        $scope.selectList=newList;
    };

    $scope.memberListUpdate=function(){
        angular.forEach($scope.memberList, function (member, key0) {
            member.isselect=false;
            angular.forEach($scope.noticeList, function (selectItem, key1) {
                if("@"+member.wx_name+" " == selectItem.name){
                    member.isselect = true;
                }
            });
        });
    };

    $scope.isCheck=function(wx_id) {
        var flag=false;
        angular.forEach($scope.selectList, function(selectItem, key) {
            if(selectItem.wx_id == wx_id){
                flag=true;
            }
        });

        return flag;
    };

    //消息通知部分内容
    $scope.time=1;
    $scope.titleRunId=0;
    $scope.setTitle=function(){
        $scope.newsCount=0;
        $scope.titleRunId=$interval(function(){
            $scope.time=$scope.time+1;
            if ($scope.time % 2 == 0 && $scope.newsCount > 0) {
                document.title = "新消息("+$scope.newsCount+")";
            }
            else {
                document.title = "慧聊客服聊天";
            };
        }, 2000);
    };

    $scope.clearRun=function(){
        if($scope.titleRunId != 0){
            $interval.cancel($scope.titleRunId);
        }
        $scope.titleRunId=0;
        $scope.newsCount=0;
        document.title = "慧聊客服聊天";
        return false;
    };

    window.parent.onblur=$scope.setTitle;
    window.parent.onfocus=$scope.clearRun;

    //右键菜单
    $scope.contextmenu=function(chatContact, flag, name, message){
        $scope.contextMenuFlag={'is_top':false, 'is_group':false, 'is_chat': false,'is_head':false , 'is_friend':false,'isShowContextMenu':true,'is_notice':false,
            'remark_dialog':chatContact.RemarkName,'group_wx_name_dialog':chatContact.group_wx_name,'group_notice_dialog':chatContact.notice,
            'menu_wx_id':chatContact.wx_id,'group_id_dialog':chatContact.wx_id,'headname':'', transpond:false ,transpond_content:'',content_type:'1',
            'dialog_show':false,'dialog_add_friend':false,'dialog_flag':'','dialog_value':'','dialog_name':'','comfirming':false,'groupOwnerId':chatContact.groupOwnerId,
            'isNotAtSession':true,'cur_msg_wx_id':message.group_member_id
        };
        $scope.selectList=[];//选择转发的好友或群
        if(!flag){
            if(chatContact.isGroup == "1"){
                $scope.contextMenuFlag.is_group=true;
                $scope.contextMenuFlag.is_friend=false;
            }
            else{
                $scope.contextMenuFlag.is_group=false;
                $scope.contextMenuFlag.is_friend=true;
            }
            $scope.contextMenuFlag.is_top=chatContact.isTop;
        }
        else if(flag == "chat"){
            $scope.contextMenuFlag.is_chat=true;
            var content = message.content;
            if(message.MsgType == 3 ||message.MsgType == 7){
                content = message.filename+"|"+message.FileExt+"|"+message.filesize+"|"+message.totallen+"|"+message.FileStatus+"|"+message.content;
            }
            if(message.MsgType == 2){
                var filenames= message.content.split("/");

                content = filenames[filenames.length-1]+"|jpg|0|0|1|"+message.content;
            }
            else if(message.MsgType == 6){
                content = message.content+"|"+message.VoiceLength+"|0";
            }
            else if(message.MsgType == 9 || message.MsgType == 12){
                if(message.linkurl){
                    content = message.title+"|"+message.des+"|"+message.content+"|0|"+message.linkurl;
                }else{
                    content = message.title+"|"+message.des+"|"+message.content+"|0";
                }
            }

            $scope.contextMenuFlag.transpond_content=content;//转发内容
            $scope.contextMenuFlag.content_type=message.MsgType;//转发内容类型
            $scope.contextMenuFlag.FileStatus=message.FileStatus;//转发内容类型
        }
        else if(flag == "head"){
            $scope.contextMenuFlag.is_head=true;
            $scope.contextMenuFlag.headname="@" + name + " ";
        }

        var e = window.event;
        var profileX = e.clientX;
        var profileY = e.clientY;

        if(flag == "notice"){
            $scope.contextMenuFlag.is_notice=true;
            $scope.contextMenuFlag.headname=$(event.target).html();
            $("#contextMenu").attr("style","display:block; top:"+ profileY + "px; left:"+ profileX + "px");
        }
        else{
            if(window.innerWidth-profileX < 127) {profileX=profileX-127}
            if(window.innerHeight-profileY < 180) {profileY=profileY-180}
            $("#contextMenu").attr("style","display:block; top:"+ profileY + "px; left:"+ profileX + "px");
        }

        if(chatContact.isAtSession){
            $scope.contextMenuFlag.isNotAtSession = false;
        }

        e.preventDefault();
    };

    //滚动条事件
    $scope.loadMore = function(){
        //每次获取5条记录
        var top_len=0;
        for(var i=0; i<5; i++){
            if($scope.chatContentDB.length > 0){
                $scope.chatContent.unshift($scope.chatContentDB.pop());
                top_len=top_len+40;
            }
        }
        $('#chat_main').scrollTop(5);
        $scope.formatTimeShow();
    };

    $scope.checkAt=function(content){
        if($scope.chatKeywordList!=null&$scope.chatKeywordList.length>0){
            for(var i=0;i<$scope.chatKeywordList.length;i++) {
                if (content.indexOf($scope.chatKeywordList[i][0]) != -1) {
                    return true;
                }
        }
        }
        return false;

    };

    $scope.QQFaceMap={"微笑":"0","撇嘴":"1","色":"2","发呆":"3","得意":"4","流泪":"5","害羞":"6","闭嘴":"7","睡":"8","大哭":"9","尴尬":"10","发怒":"11","调皮":"12","呲牙":"13","惊讶":"14","难过":"15","酷":"16","冷汗":"17","抓狂":"18","吐":"19","偷笑":"20","可爱":"21","愉快":"21","白眼":"22","傲慢":"23","饥饿":"24","困":"25","惊恐":"26","流汗":"27","憨笑":"28","悠闲":"29","大兵":"29","奋斗":"30","咒骂":"31","疑问":"32","嘘":"33","晕":"34","疯了":"35","折磨":"35","衰":"36","骷髅":"37","敲打":"38","再见":"39","擦汗":"40","抠鼻":"41","鼓掌":"42","糗大了":"43","坏笑":"44","左哼哼":"45","右哼哼":"46","哈欠":"47","鄙视":"48","委屈":"49","快哭了":"50","阴险":"51","亲亲":"52","吓":"53","可怜":"54","菜刀":"55","西瓜":"56","啤酒":"57","篮球":"58","乒乓":"59","咖啡":"60","饭":"61","猪头":"62","玫瑰":"63","凋谢":"64","嘴唇":"65","示爱":"65","爱心":"66","心碎":"67","蛋糕":"68","闪电":"69","炸弹":"70","刀":"71","足球":"72","瓢虫":"73","便便":"74","月亮":"75","太阳":"76","礼物":"77","拥抱":"78","强":"79","弱":"80","握手":"81","胜利":"82","抱拳":"83","勾引":"84","拳头":"85","差劲":"86","爱你":"87",NO:"88",OK:"89","爱情":"90","飞吻":"91","跳跳":"92","发抖":"93","怄火":"94","转圈":"95","磕头":"96","回头":"97","跳绳":"98","投降":"99","激动":"100","乱舞":"101","献吻":"102","左太极":"103","右太极":"104","嘿哈":"105","捂脸":"106","奸笑":"107","机智":"108","皱眉":"109","耶":"110","鸡":"111","红包":"112","<笑脸>":"1f604","<开心>":"1f60a","<大笑>":"1f603","<热情>":"263a","<眨眼>":"1f609","<色>":"1f60d","<接吻>":"1f618","<亲吻>":"1f61a","<脸红>":"1f633","<露齿笑>":"1f63c","<满意>":"1f60c","<戏弄>":"1f61c","<吐舌>":"1f445","<无语>":"1f612","<得意>":"1f60f","<汗>":"1f613","<失望>":"1f640","<合十>":"1f64f","<低落>":"1f61e","<呸>":"1f616","<焦虑>":"1f625","<担心>":"1f630","<震惊>":"1f628","<悔恨>":"1f62b","<眼泪>":"1f622","<哭>":"1f62d","<破涕为笑>":"1f602","<晕>":"1f632","<恐惧>":"1f631","<心烦>":"1f620","<生气>":"1f63e","<睡觉>":"1f62a","<生病>":"1f637","<恶魔>":"1f47f","<外星人>":"1f47d","<心>":"2764","<心碎>":"1f494","<丘比特>":"1f498","<闪烁>":"2728","<星星>":"1f31f","<叹号>":"2755","<问号>":"2754","<睡着>":"1f4a4","<水滴>":"1f4a6","<音乐>":"1f3b5","<火>":"1f525","<便便>":"1f4a9","<强>":"1f44d","<弱>":"1f44e","<拳头>":"1f44a","<胜利>":"270c","<上>":"1f446","<下>":"1f447","<右>":"1f449","<左>":"1f448","<第一>":"261d","<强壮>":"1f4aa","<吻>":"1f48f","<热恋>":"1f491","<男孩>":"1f466","<女孩>":"1f467","<女士>":"1f469","<男士>":"1f468","<天使>":"1f47c","<骷髅>":"1f480","<红唇>":"1f48b","<太阳>":"2600","<下雨>":"2614","<多云>":"2601","<雪人>":"26c4","<月亮>":"1f319","<闪电>":"26a1","<海浪>":"1f30a","<猫>":"1f431","<小狗>":"1f429","<老鼠>":"1f42d","<仓鼠>":"1f439","<兔子>":"1f430","<狗>":"1f43a","<青蛙>":"1f438","<老虎>":"1f42f","<考拉>":"1f428","<熊>":"1f43b","<猪>":"1f437","<牛>":"1f42e","<野猪>":"1f417","<猴子>":"1f435","<马>":"1f434","<蛇>":"1f40d","<鸽子>":"1f426","<鸡>":"1f414","<企鹅>":"1f427","<毛虫>":"1f41b","<章鱼>":"1f419","<鱼>":"1f420","<鲸鱼>":"1f433","<海豚>":"1f42c","<玫瑰>":"1f339","<花>":"1f33a","<棕榈树>":"1f334","<仙人掌>":"1f335","<礼盒>":"1f49d","<南瓜灯>":"1f383","<鬼魂>":"1f47b","<圣诞老人>":"1f385","<圣诞树>":"1f384","<礼物>":"1f381","<铃>":"1f514","<庆祝>":"1f389","<气球>":"1f388","<相机>":"1f4f7","<录像机>":"1f3a5","<电脑>":"1f4bb","<电视>":"1f4fa","<电话>":"1f4de","<解锁>":"1f513","<锁>":"1f512","<钥匙>":"1f511","<成交>":"1f528","<灯泡>":"1f4a1","<邮箱>":"1f4eb","<浴缸>":"1f6c0","<钱>":"1f4b2","<炸弹>":"1f4a3","<手枪>":"1f52b","<药丸>":"1f48a","<橄榄球>":"1f3c8","<篮球>":"1f3c0","<足球>":"26bd","<棒球>":"26be","<高尔夫>":"26f3","<奖杯>":"1f3c6","<入侵者>":"1f47e","<唱歌>":"1f3a4","<吉他>":"1f3b8","<比基尼>":"1f459","<皇冠>":"1f451","<雨伞>":"1f302","<手提包>":"1f45c","<口红>":"1f484","<戒指>":"1f48d","<钻石>":"1f48e","<咖啡>":"2615","<啤酒>":"1f37a","<干杯>":"1f37b","<鸡尾酒>":"1f377","<汉堡>":"1f354","<薯条>":"1f35f","<意面>":"1f35d","<寿司>":"1f363","<面条>":"1f35c","<煎蛋>":"1f373","<冰激凌>":"1f366","<雪糕>":"1f366","<蛋糕>":"1f382","<苹果>":"1f34f","<飞机>":"2708","<火箭>":"1f680","<自行车>":"1f6b2","<高铁>":"1f684","<警告>":"26a0","<旗>":"1f3c1","<男人>":"1f6b9","<男>":"1f6b9","<女人>":"1f6ba","<女>":"1f6ba","<版权>":"a9","<版權>":"a9","<注册商标>":"ae","<商标>":"2122"}

    $scope.clickMenu=function(panelName) {
        //刷新默认选中的
        if('panel_wx' == panelName){
            $scope.chooseWx($scope.account,$scope.choose_wx_index);
        }else {
            $scope.chooseWxAt($scope.accountAt,$scope.choose_at_index);
        }
          $scope.showPanel = panelName;
    };
    $scope.timeShow=function(sendmin){
        if(sendmin==null||sendmin==""){
            return "";
        }
        var now = new Date();
        var sdate =new Date(new Date(Date.parse(sendmin.replace(/-/g, "/"))).format('yyyy-MM-dd'));// new Date(sendmin.replace(/-/g, "/"))
        var days = now.getTime() - sdate.getTime();
        var day = parseInt(days / (1000 * 60 * 60 * 24))
        var sendTime=sendmin.split(" ")[1];
        if (day == 0)
            return sendTime;
        else if(day == 1)
            return "昨天 "+sendTime;
        else if (day > 1 && day < 30)
            return day+"天前 "+sendTime;
        else if (day > 30 && day < 60)
            return "上月 "+sendTime;
        else if (day > 60 && day < 360)
            return "两月前 "+sendTime;
        else
            return "去年";
    };
    //快捷回复列表获取
    $.ajax({
        type: "GET",
        url: "http://"+window.location.host+"/WXCRM/quickReplyData/",
        //async: true,
        data: {"type":"getListJson"},
        success: function (result) {
            severcheck(result);
            result = parseJson(result);
            $scope.quickReplyList=result.retList;
        },
        error: function (XMLHttpRequest, textStatus, errorThrown, data) {
            alert(JSON.stringify(data));// 请求失败执行代码
        }
    });
    $scope.goQuickReply = function(content) {
        $scope.currentContact.draft = content;
        $scope.chooseQuickReply = content;
        $("#editArea").html(content);
        //$scope.sendTextMessage();
    };
    //初始化关键字信息
    $.ajax({
        type: "GET",
        url: "http://"+window.location.host+"/WXCRM/chatKeywordData/",
        //async: true,
        data: {"type":"getListJson"},
        success: function (result) {
            severcheck(result);
            result = parseJson(result);
            $scope.chatKeywordList=result.retList;
        },
        error: function (XMLHttpRequest, textStatus, errorThrown, data) {
            alert(JSON.stringify(data));// 请求失败执行代码
        }
    });
 
    //微信主号列表中点击…显示功能列表
    $scope.showMainWxMenu=function(event,wx){
        var e=event||window.event;
        e.stopPropagation();//阻止事件冒泡,防止点击父容器
        $scope.mainWxMenuFlag={'isShowMainWxMenu':true,'isClearUnread':true,"wx_id":wx.wx_id};
        var e = window.event;
        var profileX = e.clientX;
        var profileY = e.clientY;
        if(window.innerWidth-profileX < 127) {profileX=profileX-127}
        if(window.innerHeight-profileY < 180) {profileY=profileY-180}
        $("#mainWxMenu").attr("style","display:block; top:"+ profileY + "px; left:"+ profileX + "px");

    };
    $scope.clearUnread=function() {
        $scope.mainWxMenuFlag.isShowMainWxMenu=false;
        $.ajax({
            method: 'POST',
            async:false,
            url: 'http://'+window.location.host+'/WXCRM/wxChatInfo/',
            data:{'wx_main_id':$scope.mainWxMenuFlag.wx_id,
                   'oper':'clearUnread'
            },
            success: function (ret) {
                severcheck(ret);
                clearDB();
                //alert("一键标记未读消息为已读成功！");
            },
            error: function (XMLHttpRequest, textStatus, errorThrown, data) {
                var errorTips=showAjaxError("一键标记已读",XMLHttpRequest,errorThrown);
                alert(errorTips);
            }
        });
    };

    $scope.fileuploadInit = function () {
        $('#file_upload').fileupload({
            url: 'http://'+window.location.host+'/fileupload/',
            //url: 'http://124.172.188.65:8001/uploadMsgFile/',
            //dataType: 'JSONP',
            //forceIframeTransport: true,
            change: function(e, data) {//这个是选择文件的回调函数
                if(data.files.length > 9){//这里是判断选择文件的个数,根据实际情况设置
                    alert("最多只能选择9个文件");
                    return false;
                }
                for(var i=0;i < data.files.length;i++) {
                    if(data.files[i].size > 1024*1024*10)
                    {
                        alert("文件"+data.files[i].name+"大于10MB");
                        return false;
                    }
                }
                data.formData = { wx_id: $("#wx_main_id").val() };
            },
            done: function (e, data) {
                if(data && data.result){
                    severcheck(data.result);
                    data=JSON.parse(data.result);
                    var fileObject={"filename": data.filename, "filesize": data.filesize,"totallen": data.totallen, "content": data.content,
                        "MsgType": data.MsgType, "FileExt": data.FileExt}
                    var appElement = document.querySelector('[ng-controller=appController]');
                    //获取$scope变量
                    var $scope = angular.element(appElement).scope();
                    $scope.sendTextMessage(fileObject);
                    //同步到Angular控制器中，则需要调用$apply()方法即可
                    $scope.$apply();
                }
            },
            fail: function () {
                alert('上传出错！');
            }
        });
    };

    //设置Ctrl+Enter换行
    document.onkeydown=function(e){
        if(e.keyCode == 13 && e.ctrlKey){
           // 这里实现换行
            if (browserType() == "IE" || browserType() == "Edge") {
                $("#editArea").append("<div></div>");
            }
            else if (browserType() == "FF") {
                $("#editArea").append("<br/><br/>");
            } else {
                $("#editArea").append("<div><br/></div>");
            }
            //设置输入焦点
            var o = document.getElementById("editArea").lastChild;
            var textbox = document.getElementById('editArea');
            var sel = window.getSelection();
            var range = document.createRange();
            range.selectNodeContents(textbox);
            range.collapse(false);
            range.setEndAfter(o);//
            range.setStartAfter(o);//
            sel.removeAllRanges();
            sel.addRange(range);
            //
        }else if(e.keyCode == 13){
            // 避免回车键换行
            e.preventDefault();
        }
    };
    //判断浏览器
    function browserType () {
        var userAgent = navigator.userAgent; //取得浏览器的userAgent字符串
        var isOpera = false;
        if (userAgent.indexOf('Edge') > -1) {
            return "Edge";
        }
        if (userAgent.indexOf('.NET') > -1) {
            return "IE";
        }
        if (userAgent.indexOf("Opera") > -1 || userAgent.indexOf("OPR") > -1) {
            isOpera = true;
            return "Opera"
        }; //判断是否Opera浏览器
        if (userAgent.indexOf("Firefox") > -1) {
            return "FF";
        } //判断是否Firefox浏览器
        if (userAgent.indexOf("Chrome") > -1) {
            return "Chrome";
        }
        if (userAgent.indexOf("Safari") > -1) {
            return "Safari";
        } //判断是否Safari浏览器
        if (userAgent.indexOf("compatible") > -1 && userAgent.indexOf("MSIE") > -1 && !isOpera) {
            return "IE";
        }; //判断是否IE浏览器
    }

});

//这个必须要加上右键菜单才能出来
appWx.directive('ngRightClick', function($parse) {
    return function(scope, element, attrs) {
        var fn = $parse(attrs.ngRightClick);
        element.bind('contextmenu', function(event) {
            scope.$apply(function() {
                event.preventDefault();
                fn(scope, {$event:event});
            });
        });
    };
});

//滚动指令
appWx.directive('whenScrolled', function() {
    return function(scope, elm, attr) {
        // 内层DIV的滚动加载
        var raw = elm[0];
        elm.bind('scroll', function() {
            if(raw.scrollTop == 0){
                scope.$apply(attr.whenScrolled);
            }
        });
    };
});

//绑定在了body上，也可以绑定在其他可用元素行，但是不是所有元素都支持copy和past事件。
$(document.body).bind({
    copy: function(e) {//copy事件
        var clipboardData = window.clipboardData; //for IE
        if (!clipboardData) { // for chrome
            clipboardData = e.originalEvent.clipboardData;
        }
        clipboardData.setData('Text', window.getSelection());
        return false;//否则设不生效
    }
});

$(function(){
    //初始化select2 初始化好友标签下来列表
    $('.select2').select2({
        allowClear: true, //是否允许清空选中
    });
    //打开数据库
    myIndexedDb.open();

});

function delete_member(){
    if($(event.target.parentElement.parentElement).attr("id") == "friend_show"){
        $('#delete_member_div').append($(event.target.parentElement).prop("outerHTML"));
    }
    else{
        $('#friend_show').append($(event.target.parentElement).prop("outerHTML"));
    }

    $(event.target.parentElement).remove();
}

//外部接口实现 从本地数据库获取聊天记录
function returnDataResult(dataContentList) {
    var appElement = document.querySelector('[ng-controller=appController]');
    //获取$scope变量
    var $scope = angular.element(appElement).scope();
    $scope.chatShowing(dataContentList);
    //同步到Angular控制器中，则需要调用$apply()方法即可
    $scope.$apply();
}

function memberHide(){
    var friend_filter=$("#friend_filter").val();
    $("input[name='addMemberCheck']").each(function () {
        if($(this).attr("data").indexOf(friend_filter) != -1){
            $(this).parent().parent().show();
        }
        else{
            $(this).parent().parent().hide();
        }
    });
}

