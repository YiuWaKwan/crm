var groupSent = angular.module("groupSent", ["ui.router","ngSanitize","ngAnimate"]);

//{{}} 转换成 [[]]
groupSent.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('[[');
  $interpolateProvider.endSymbol(']]');
});

//路由配置
groupSent.config(['$stateProvider','$urlRouterProvider', function ($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise("/main");
    $stateProvider.state('main', {
        url:'/main',
        views:{
            'groupSentMainView':{
                templateUrl: "/WXCRM/groupSentIndex"
            }
        }
    }).state('groupSentIndex', {
        url:'/groupSentIndex',
        views:{
            'groupSentMainView':{
                templateUrl: "/WXCRM/groupSentIndex"
            }
        }
    }).state('groupSentCreate', {
        url:'/groupSentCreate',
        views:{
            'groupSentMainView':{
                templateUrl: "/WXCRM/groupSentCreate"
            }
        }
    })
}]);

//远程请求服务
groupSent.service("remoteService",["$http",function ($http) {
    this.__post__ = function (url, reqData, callback, error_callback=function(){}) {
        $http({method:'post', url:url, data:reqData, headers: { 'Content-Type': 'application/x-www-form-urlencoded'},
            transformRequest: function(obj) {var str = [];for(var p in obj){str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));}return str.join("&");}})
            .then(function (res) {severcheck(res.data);callback(res);},function (res) {console.error(res);error_callback(res)})
    };
    this.getWxId = function ($scope, callback) {
        this.__post__('/getWxId/', {}, function(res){callback(res.data, $scope);})
    };
    this.getGroupSentInfo = function ($scope, callback) {
        var reqData = {
            wx_ids_query :$scope.wx_ids_query,
            sent_status: $scope.sent_status,
            sent_beginTime :$scope.sent_beginTime,
            sent_endTIme :$scope.sent_endTIme,
            key_word: $scope.key_word,
            pageIndex: $scope.pageIndex,
            pageSize: $scope.pageSize,
            totalCount: $scope.totalCount
        };
        this.__post__('/WXCRM/getGroupSentInfo/', reqData, function(res){callback(res.data, $scope);})
    };
    this.queryZone = function ($scope, callback) {
        this.__post__('/WXCRM/queryZone/', {}, function(res){callback(res.data, $scope);})
    };
    this.queryFriends = function ($scope, callback) {
        var reqData = {
            sent_wxId :$scope.sent_wxId,
            friend_nickname: $scope.friend_nickname,
            friend_zone: $scope.friend_zone,
            friend_remark :$scope.friend_remark,
            friend_flag :$scope.friend_flag,
            pageIndex: $scope.pageIndex,
            pageSize: $scope.pageSize,
            totalCount: $scope.totalCount
        };
        this.__post__('/WXCRM/queryFriends/', reqData, function(res){callback(res.data, $scope);})
    };
    this.groupSent = function ($scope, $rootScope, callback) {
        var type = "1";
        var content = $rootScope.content;
        if($rootScope.fileContent){
            type = "2";
            content = $rootScope.fileContent;
        }
        $rootScope.type = type;

        if($scope.receive_wxIds.length <= 0){
            alert("请选择收信好友");
            return
        }
        if(!(content && content.length > 0)){
            alert("不能发送空白消息");
            return
        }

        var receive_wxIds = [];
        angular.forEach($scope.receive_wxIds, function (o) {
            receive_wxIds.push(o.wx_id);
        });

        var reqData = {
            sent_wxId: $scope.sent_wxId,
            receive_wxIds: receive_wxIds,
            type: type,
            content: content
        };
        $scope.isShow_sD();
        this.__post__('/WXCRM/addGroupSentTask/', reqData, function(res){callback(res.data, $scope);},function (res) {
            alert("群发异常");
            $scope.isHide_sD();
        })
    };
    this.deleteSent = function ($scope, callback) {
        var reqData = {group_sent_id:$scope.delPkId};
        this.__post__('/WXCRM/deleteSent/', reqData, function(res){callback(res.data, $scope);})
    };
    this.sentAgain = function (id, $scope, callback) {
        var reqData = {group_sent_id:id};
        this.__post__('/WXCRM/sentAgain/', reqData, function(res){callback(res.data, $scope);})
    };
    this.resend = function (id, $scope, callback) {
        if($scope.resend_flag)return false;
        $scope.resend_flag = true;
        var reqData = {group_sent_id:id};
        this.__post__('/WXCRM/resend/', reqData, function(res){callback(res.data, $scope);})
    };
}]);

//本地逻辑处理
groupSent.service("localService",["$http",function ($http) {
    this.buildZoneSelect = function (data, $scope) {
        if(data && data.data)data = data.data;
        // console.log(data);
        var opt = [{label:"请选择",value:0}];
        var unknown = false;
        var other = [];
        angular.forEach(data,function (e) {
            if( e == "未知")
                unknown = true;
            else
                other.push({label:e,value:e})
        });
        if(unknown)opt.push({label:"未知",value:"未知"});
        opt = opt.concat(other);

        $scope.regionSelect= $("#regionSelect").jqSelect({
          option:opt,
          onChange:function(res){
              if(res==""){
                  $scope.regionSelect.setResult("0");
                  $scope.friend_zone = "";
              }else {
                  $scope.friend_zone = res;
                  if (res=="0")$scope.friend_zone = "";
              }
          }
      });
      $scope.regionSelect.setResult(["0"]);

    };
    this.buildWxSelect = function(data, $scope){
        if(data && data.data)data = data.data;
        setWxId(data, $scope);
        // console.log(data);
        var opt = [{label:"请选择",value:0}];
        angular.forEach(data,function (e) {
            opt.push({label:e.wx_name ? e.wx_name : e.wx_login_id,value:e.wx_id})
        });

        var wxSelect= $("#wxSelect").jqSelect({
            option:opt,
            onChange:function(res){
              if(res==""){
                  wxSelect.setResult("0");
                  $scope.sent_wxId = "";
              }else{
                  $scope.sent_wxId = res;
                  if (res=="0")$scope.sent_wxId = "";
              }
              if($scope.sent_wxId){
                  var sent_wx = opt.find(o=>{return o.value == $scope.sent_wxId})
                  $scope.sent_wxName = sent_wx.label;
              }else{
                  $scope.sent_wxName = "";
              }
            }
        });
        wxSelect.setResult(["0"]);
    };
    this.buildWxSelectMult = function(data, $scope){  /*data=>{"data": [{"wx_id": "wxid_j6uch9ayzr6622", "wx_name": "\u5c0f\u4e56\u4e56", "head_picture": "http://wx.qlogo.cn/mmhead/ver_1/I8Vwzgydw3fLia6brGX61AjLNF7I8Nl6VGUyAsRoJ3VMRxggBFwht6Yxf2mcKgibXZnuGSzzuv35NICHmiagpyy49VXsehCcL1s0Sib5Xexico6M/0", "wx_login_id": "wxid_j6uch9ayzr6622"}, {"wx_id": "wxid_66j7k6sblcq222", "wx_name": "\u5954\u8dd1\u7684\u732a", "head_picture": "http://wx.qlogo.cn/mmhead/ver_1/WNMsXbK1NJECK7nDNn2m5uI4zmRWIZ34icrnRCMaps0EaSKkpPQBxrbHVCia4tSSpTqjNNU8B36f0Usomd06WVDT5kPRGegCEyk62j3hOH1V4/0", "wx_login_id": "17195592548"}, {"wx_id": "olaola156", "wx_name": null, "head_picture": null, "wx_login_id": "olaola156"}, {"wx_id": "wxid_u0vfthibggxh22", "wx_name": "\u5c0f\u53ef\u7231\u4e5f\u8981\u98de\u7fd4", "head_picture": "http://wx.qlogo.cn/mmhead/ver_1/eHaROsycY1HAVmH4T6l43kD9axX6ibmuNZibAL3iaaeKppjlfT9oicibOj72IeP5msD8BaTMZwnbhMPwrCqWnhMLqMT4dqmXXIeU03d09ZibWiaDqA/0", "wx_login_id": "17195592546"}]}*/
        if(data && data.data)data = data.data;
        setWxId(data, $scope);
        // console.log(data);
        var opt = [{label:"全部",value:0}];
        angular.forEach(data,function (e) {
            opt.push({label:e.wx_name ? e.wx_name : e.wx_login_id,value:e.wx_id})
        });

        $scope.wxSelect= $("#wxSelect").jqSelect({
            mult:true,  //true为多选,false为单选
            option:opt,
            onChange:function(res){   //选择框值变化返回结果
                var index = res.indexOf("0");
                if (index > -1) {
                    res.splice(index, 1);
                }
                if(res.length==0) {
                    $scope.wxSelect.setResult(["0"]);
                    $scope.wx_ids_query = [];
                }else {
                    $scope.wxSelect.setResult([]);
                    $scope.wxSelect.setResult(res);
                    // console.log(res);
                    $scope.wx_ids_query = res;
                }
            }
        });
        $scope.wxSelect.setResult(["0"]);
    };
    this.buildGroupSentInfoGrid = function (data, $scope) {
        // console.log(data);
        var temp = $scope.totalCount;
        $scope.totalCount = data.data.count;
        $scope.dataList = data.data.pageList;

        $('#pageBox').paging({
            pageNum: $scope.pageIndex, // 初始页码
            pageTotal: (parseInt($scope.totalCount / $scope.pageSize) + 1), //总页数
            callback: function (page) { // 回调函数
                $scope.pageIndex = page;
                $scope.query();
            }
        });
    };
    this.buildFriendsGrid = function (data, $scope) {
        // console.log(data);
        var temp = $scope.totalCount;
        $scope.totalCount = data.data.count;
        $scope.dataList = data.data.pageList;

        $('#pageBox').paging({
            pageNum: $scope.pageIndex, // 初始页码
            pageTotal: (parseInt($scope.totalCount / $scope.pageSize) + 1), //总页数
            callback: function(page) { // 回调函数
                $scope.pageIndex = page;
                $scope.queryFriends();
            }
        });
    };
    this.afterSent = function (data, $scope) {
        $scope.flag = data.flag;
        $scope.success_wxIds = data.success_wxIds;
        $scope.failure_wxIds = data.failure_wxIds;
        $scope.failure_remarks = data.failure_remarks;
        $scope.create_time = data.ctime;

        /*重新发送*/
        $scope.resend = function(){
            remoteService.resend(data.groupSentId, $scope, localService.afterResend)
        };

        if(!data.flag) {
            alert("群发异常");
            $scope.isHide_sD();
        }
    };
    this.afterResend = function (data, $scope) {
        $scope.resend_flag = false;
        if(data.flag){
            $scope.flag = data.flag;
            $scope.success_wxIds = data.success_wxIds;
            $scope.failure_wxIds = data.failure_wxIds;
            $scope.failure_remarks = data.failure_remarks;
            $scope.create_time = data.ctime;

            alert("重发成功");
        }else{
            alert("重发失败");
        }
    };
    this.viewDetail = function (data, $scope) {
        if(data.flag){
            $scope.flag = data.flag;
            $scope.success_wxIds = data.success_wxIds;
            $scope.failure_wxIds = data.failure_wxIds;
            $scope.failure_remarks = data.failure_remarks;
            $scope.create_time = data.ctime;
        }else{
            alert("获取详情信息失败");
            $scope.isHide_sD();
        }
    };
    this.afterDel = function (data, $scope) {

        if(data.flag){
            $scope.msg_success = true;
        }else{
            $scope.msg_failure = true;
        }

        var tips = $("#show_msg");
        setTimeout(function(){tips.slideDown(300);},300);
        setTimeout(function(){tips.slideUp(1000);},3000);

        $scope.isShow_delSent = false;

        $scope.totalCount = "";
        $scope.query();
    };
    this.afterSentAgain = function (data, $scope) {
        $scope.totalCount = "";
        $scope.query();
        $scope.isHide_sD();

        if(data.flag){
            $scope.msg_success = true;
        }else{
            $scope.msg_failure = true;
        }

        var tips = $("#show_msg");
        setTimeout(function(){tips.slideDown(300);},300);
        setTimeout(function(){tips.slideUp(1000);},5000);
    };
    this.QQFaceMap = {"微笑":"0","撇嘴":"1","色":"2","发呆":"3","得意":"4","流泪":"5","害羞":"6","闭嘴":"7","睡":"8","大哭":"9","尴尬":"10","发怒":"11","调皮":"12","呲牙":"13","惊讶":"14","难过":"15","酷":"16","冷汗":"17","抓狂":"18","吐":"19","偷笑":"20","可爱":"21","愉快":"21","白眼":"22","傲慢":"23","饥饿":"24","困":"25","惊恐":"26","流汗":"27","憨笑":"28","悠闲":"29","大兵":"29","奋斗":"30","咒骂":"31","疑问":"32","嘘":"33","晕":"34","疯了":"35","折磨":"35","衰":"36","骷髅":"37","敲打":"38","再见":"39","擦汗":"40","抠鼻":"41","鼓掌":"42","糗大了":"43","坏笑":"44","左哼哼":"45","右哼哼":"46","哈欠":"47","鄙视":"48","委屈":"49","快哭了":"50","阴险":"51","亲亲":"52","吓":"53","可怜":"54","菜刀":"55","西瓜":"56","啤酒":"57","篮球":"58","乒乓":"59","咖啡":"60","饭":"61","猪头":"62","玫瑰":"63","凋谢":"64","嘴唇":"65","示爱":"65","爱心":"66","心碎":"67","蛋糕":"68","闪电":"69","炸弹":"70","刀":"71","足球":"72","瓢虫":"73","便便":"74","月亮":"75","太阳":"76","礼物":"77","拥抱":"78","强":"79","弱":"80","握手":"81","胜利":"82","抱拳":"83","勾引":"84","拳头":"85","差劲":"86","爱你":"87",NO:"88",OK:"89","爱情":"90","飞吻":"91","跳跳":"92","发抖":"93","怄火":"94","转圈":"95","磕头":"96","回头":"97","跳绳":"98","投降":"99","激动":"100","乱舞":"101","献吻":"102","左太极":"103","右太极":"104","嘿哈":"105","捂脸":"106","奸笑":"107","机智":"108","皱眉":"109","耶":"110","鸡":"111","红包":"112","<笑脸>":"1f604","<开心>":"1f60a","<大笑>":"1f603","<热情>":"263a","<眨眼>":"1f609","<色>":"1f60d","<接吻>":"1f618","<亲吻>":"1f61a","<脸红>":"1f633","<露齿笑>":"1f63c","<满意>":"1f60c","<戏弄>":"1f61c","<吐舌>":"1f445","<无语>":"1f612","<得意>":"1f60f","<汗>":"1f613","<失望>":"1f640","<合十>":"1f64f","<低落>":"1f61e","<呸>":"1f616","<焦虑>":"1f625","<担心>":"1f630","<震惊>":"1f628","<悔恨>":"1f62b","<眼泪>":"1f622","<哭>":"1f62d","<破涕为笑>":"1f602","<晕>":"1f632","<恐惧>":"1f631","<心烦>":"1f620","<生气>":"1f63e","<睡觉>":"1f62a","<生病>":"1f637","<恶魔>":"1f47f","<外星人>":"1f47d","<心>":"2764","<心碎>":"1f494","<丘比特>":"1f498","<闪烁>":"2728","<星星>":"1f31f","<叹号>":"2755","<问号>":"2754","<睡着>":"1f4a4","<水滴>":"1f4a6","<音乐>":"1f3b5","<火>":"1f525","<便便>":"1f4a9","<强>":"1f44d","<弱>":"1f44e","<拳头>":"1f44a","<胜利>":"270c","<上>":"1f446","<下>":"1f447","<右>":"1f449","<左>":"1f448","<第一>":"261d","<强壮>":"1f4aa","<吻>":"1f48f","<热恋>":"1f491","<男孩>":"1f466","<女孩>":"1f467","<女士>":"1f469","<男士>":"1f468","<天使>":"1f47c","<骷髅>":"1f480","<红唇>":"1f48b","<太阳>":"2600","<下雨>":"2614","<多云>":"2601","<雪人>":"26c4","<月亮>":"1f319","<闪电>":"26a1","<海浪>":"1f30a","<猫>":"1f431","<小狗>":"1f429","<老鼠>":"1f42d","<仓鼠>":"1f439","<兔子>":"1f430","<狗>":"1f43a","<青蛙>":"1f438","<老虎>":"1f42f","<考拉>":"1f428","<熊>":"1f43b","<猪>":"1f437","<牛>":"1f42e","<野猪>":"1f417","<猴子>":"1f435","<马>":"1f434","<蛇>":"1f40d","<鸽子>":"1f426","<鸡>":"1f414","<企鹅>":"1f427","<毛虫>":"1f41b","<章鱼>":"1f419","<鱼>":"1f420","<鲸鱼>":"1f433","<海豚>":"1f42c","<玫瑰>":"1f339","<花>":"1f33a","<棕榈树>":"1f334","<仙人掌>":"1f335","<礼盒>":"1f49d","<南瓜灯>":"1f383","<鬼魂>":"1f47b","<圣诞老人>":"1f385","<圣诞树>":"1f384","<礼物>":"1f381","<铃>":"1f514","<庆祝>":"1f389","<气球>":"1f388","<相机>":"1f4f7","<录像机>":"1f3a5","<电脑>":"1f4bb","<电视>":"1f4fa","<电话>":"1f4de","<解锁>":"1f513","<锁>":"1f512","<钥匙>":"1f511","<成交>":"1f528","<灯泡>":"1f4a1","<邮箱>":"1f4eb","<浴缸>":"1f6c0","<钱>":"1f4b2","<炸弹>":"1f4a3","<手枪>":"1f52b","<药丸>":"1f48a","<橄榄球>":"1f3c8","<篮球>":"1f3c0","<足球>":"26bd","<棒球>":"26be","<高尔夫>":"26f3","<奖杯>":"1f3c6","<入侵者>":"1f47e","<唱歌>":"1f3a4","<吉他>":"1f3b8","<比基尼>":"1f459","<皇冠>":"1f451","<雨伞>":"1f302","<手提包>":"1f45c","<口红>":"1f484","<戒指>":"1f48d","<钻石>":"1f48e","<咖啡>":"2615","<啤酒>":"1f37a","<干杯>":"1f37b","<鸡尾酒>":"1f377","<汉堡>":"1f354","<薯条>":"1f35f","<意面>":"1f35d","<寿司>":"1f363","<面条>":"1f35c","<煎蛋>":"1f373","<冰激凌>":"1f366","<雪糕>":"1f366","<蛋糕>":"1f382","<苹果>":"1f34f","<飞机>":"2708","<火箭>":"1f680","<自行车>":"1f6b2","<高铁>":"1f684","<警告>":"26a0","<旗>":"1f3c1","<男人>":"1f6b9","<男>":"1f6b9","<女人>":"1f6ba","<女>":"1f6ba","<版权>":"a9","<版權>":"a9","<注册商标>":"ae","<商标>":"2122"}
    this.showFace = function(content){
        if(content){
            var QQFaceMap = this.QQFaceMap;
            var reg = /\[([^\]]+)\]/g;
            content = content.replace(reg, function($1){
                face=$1.replace('[','').replace(']','');
                if(QQFaceMap.hasOwnProperty(face)){
                    return "<img class='qqemoji qqemoji"+QQFaceMap[face]+"' src='/static/img/wx/spacer.gif'>";
                }else if(QQFaceMap.hasOwnProperty("<"+face+">")){
                    return "<img class='emoji emoji"+QQFaceMap["<"+face+">"]+"' src='/static/img/wx/spacer.gif'>";
                }
                return $1;
            });
        }
        return content;
    };
    
    function setWxId(data, $scope) {
        $scope.wxIds = [];
        angular.forEach(data,function (e) {
            $scope.wxIds.push(e.wx_id? e.wx_id : e.wx_login_id)
        });
    }
}]);

//群发主页控制器
groupSent.controller("indexController",function ($scope, $rootScope, remoteService, localService) {

    $scope.wx_ids_query = [];  //查询条件 微信号
    $scope.sent_status = "";   // 查询条件 状态
    $scope.sent_beginTime = ""; //查询条件 开始时间
    $scope.sent_endTIme = ""; //查询条件 结束时间
    $scope.key_word = "";    //查询条件 昵称关键字

    $scope.pageIndex = "1";
    $scope.pageSize = "5";
    $scope.totalCount = "";

    $scope.ztSelect = null;  //状态下拉组件
    $scope.wxSelect = null;  //微信号下拉组件
    $scope.wxIds = [];      //微信号列表

    $scope.isShow_sentDetails = false;    //发送详情弹窗开关标识
    $scope.flag = false;     // 结果状态
    $scope.resend_flag = false;
    $scope.success_wxIds = [];  // 成功收信好友
    $scope.failure_wxIds = [];  // 异常收信好友
    $scope.failure_remarks = [];  // 异常原因
    $scope.create_time = "";    // 创建时间
    $scope.receive_wxIds = [];  //收信人
    $scope.sent_wxName = "";  //发信人
    $scope.content = ""; //信息内容
    $scope.fileContent = "";  //文件内容
    $scope.type = "";  //内容类型

    $scope.delFlag = true;  //处理状态显示开关
    $scope.isShow_delSent = false;  //确认删除弹窗开关
    $scope.delPkId = "";   //被删除记录的ID

    $scope.msg_success = false;
    $scope.msg_failure = false;

    $scope.isShow_sD=function(){
        $scope.isShow_sentDetails = true;
    };
    $scope.isHide_sD=function(){
        $scope.isShow_sentDetails = false;

        $scope.flag = false;     // 结果状态
        $scope.success_wxIds = [];  // 成功收信好友
        $scope.failure_wxIds = [];  // 异常收信好友
        $scope.failure_remarks = [];  // 异常原因
        $scope.create_time = "";    // 创建时间
        $scope.receive_wxIds = [];  //收信人
        $scope.sent_wxName = "";  //发信人
    };
    $scope.viewDetail = function(info){
        $scope.isShow_sD();

        $scope.sent_wxName = info[2];
        $scope.create_time = info[5];
        $scope.content = info[4];
        $scope.fileContent = info[4];
        $scope.type = info[11];

        $scope.receive_wxIds = [];
        $scope.success_wxIds = [];
        if(info[12]){
            info[12].split(",").forEach(function (str) {
                var wx = str.split(";");
                $scope.success_wxIds.push(wx[0]);
                $scope.receive_wxIds.push({wx_id:wx[0],wx_name:wx[1]});
            });
        }
        $scope.failure_wxIds = [];
        if(info[13]){
            info[13].split(",").forEach(function (str) {
                var wx = str.split(";");
                $scope.failure_wxIds.push(wx[0]);
                $scope.receive_wxIds.push({wx_id:wx[0],wx_name:wx[1]});
            });
        }
        $scope.failure_remarks = [];
        if(info[8]){
             info[8].split(",").forEach(function (str) {
                 $scope.failure_remarks.push(str);
             });
        }

        /*重新发送*/
        $scope.resend = function(){
            remoteService.resend(info[0], $scope, localService.afterResend)
        };

        $scope.flag = true;
    };

    $scope.deleteSent = function(id){
        $scope.delPkId = id;
        $scope.delFlag = true;
        $scope.isShow_delSent = true;
    };
    $scope.confirm_del = function(){
        $scope.delFlag = false;
        remoteService.deleteSent($scope, localService.afterDel);
    };
    $scope.cancel_del = function(){
        $scope.delPkId = "";
        $scope.delFlag = true;
        $scope.isShow_delSent = false;
    };

    $scope.sentAgain = function(id){
        $scope.flag = false;
        $scope.isShow_sD();
        remoteService.sentAgain(id, $scope, localService.afterSentAgain);
    };

    $scope.init = function(){
        remoteService.getWxId($scope,localService.buildWxSelectMult);

        $scope.ztSelect= $("#ztSelect").jqSelect({
          option:[
              {label:"全部",value:0},
              {label:"成功",value:1},
              {label:"异常",value:2}
          ],
          onChange:function(res){
            if(res=="")ztSelect.setResult("0");
            $scope.sent_status = res;
            if(res=="0")$scope.sent_status="";
          }
        });
        $scope.ztSelect.setResult("0");

        $scope.query();
    };

    $scope.checkLength = function(id){
        setTimeout(function () {
            if($("#"+id +" .single_text").width() < 300){
            $("#"+id+" .count").hide();
        }
        },0);
    };

    $scope.strLength = function(str){
        return str.replace(/[\u0391-\uFFE5]/g,"aa").length
    };

    $scope.query = function () {
        remoteService.getGroupSentInfo($scope, localService.buildGroupSentInfoGrid);
    };

    $scope.queryTrigger = function(){
        $scope.sent_beginTime=$("#sent_beginTime").val();
        $scope.sent_endTIme=$("#sent_endTIme").val();
        $scope.pageIndex = "1";
        $scope.totalCount = "";

        remoteService.getGroupSentInfo($scope, localService.buildGroupSentInfoGrid);
    };

    $scope.reset = function () {
        $scope.wx_ids_query = [];
        $scope.wxSelect.setResult(["0"]);

        $scope.sent_status = "";
        $scope.ztSelect.setResult("0");

        $scope.sent_beginTime = "";
        $scope.sent_endTIme = "";
        $scope.key_word = "";
    };

});

//群发创建控制器
groupSent.controller("createController",function ($scope, $rootScope, $state, remoteService, localService) {

    $scope.sent_wxId = "";  //发信人
    $scope.sent_wxName = "";  //发信人名称
    $scope.receive_wxIds = [];  //收信人
    $scope.temp_receive_wxIds = []; //用于选择收信人时
    $rootScope.content = "";  //发送文本内容
    $rootScope.fileContent = "";  //发送文件内容
    $rootScope.type = "";  //发送类型 1文本 2文件

    $scope.friend_nickname = "";  //查询条件 昵称
    $scope.friend_zone = "";     //查询条件 地区
    $scope.friend_remark = "";    //查询条件 备注
    $scope.friend_flag = "";     //查询条件 标签

    $scope.pageIndex = "1";
    $scope.pageSize = "5";
    $scope.totalCount = "";

    $scope.regionSelect = null;   //地区下拉组件

    $scope.isShow_chooseFriends = false;  //好友选择弹窗开关标志
    $scope.isShow_sentDetails = false;    //发送详情弹窗开关标识

    $scope.resend_flag = false;
    $scope.flag = false;     // 结果状态
    $scope.success_wxIds = [];  // 成功收信好友
    $scope.failure_wxIds = [];  // 异常收信好友
    $scope.failure_remarks = [];  // 异常原因
    $scope.create_time = "";    // 创建时间

    $scope.isShow_cF=function(){
        if($scope.sent_wxId == ""){
            alert("请先选择发信人");
            return;
        }
        $scope.isShow_chooseFriends = true;
        $scope.temp_receive_wxIds = [].concat($scope.receive_wxIds);
        $scope.queryFriends();
    };
    $scope.isHide_cF=function(){
        $scope.isShow_chooseFriends = false;

        $scope.temp_receive_wxIds = [];
    };

    $scope.isShow_sD=function(){
         $scope.isShow_sentDetails = true;
    };
    $scope.isHide_sD=function(){
         $scope.isShow_sentDetails = false;

         $state.go("groupSentIndex");
    };

    $scope.init = function(){
        remoteService.getWxId($scope,localService.buildWxSelect);
    };

    $scope.init_choose = function(){
        remoteService.queryZone($scope, localService.buildZoneSelect);
    };

    $scope.queryTrigger = function(){
        $scope.pageIndex = "1";
        $scope.totalCount = "";
        $scope.queryFriends();
    };

    $scope.queryFriends = function(){
        remoteService.queryFriends($scope, localService.buildFriendsGrid)
    };

    $scope.clearFriends = function(){
        $scope.temp_receive_wxIds = [];

        var tips = $("#clear_choose");
        // tips.show();
        setTimeout(function(){tips.slideDown(300);},300);
        setTimeout(function(){tips.slideUp(1000);},3000);
    };

    $scope.reset = function () {
        $scope.friend_nickname = "";
        $scope.friend_zone = "";
        $scope.regionSelect.setResult(["0"]);
        $scope.friend_remark = "";
        $scope.friend_flag = "";
    };

    $scope.check = function (event, wx_id, wx_name) {
        var action = event.target;
        if(action.checked) {//选中，就添加
            if(!$scope.isContain(wx_id))
                $scope.temp_receive_wxIds.push({wx_id:wx_id,wx_name:wx_name});
        }else{
            var idx = $scope.temp_receive_wxIds.indexOf({wx_id:wx_id,wx_name:wx_name});
            $scope.temp_receive_wxIds.splice(idx,1);
        }
    };

    $scope.isContain = function (wx_id) {
        if($scope.temp_receive_wxIds.find(o=>{return o.wx_id == wx_id}))return true;
        return false;
    };

    $scope.confirm = function () {
        $scope.receive_wxIds = [].concat($scope.temp_receive_wxIds);

        $scope.isHide_cF();
    };
    
    $scope.remove = function (_wx_id) {
        var idx = $scope.receive_wxIds.findIndex((o)=>{return o.wx_id == _wx_id});
        if (idx > -1)
            $scope.receive_wxIds.splice(idx, 1);
    };

    $scope.send = function () {

        // localService.afterSent("",$scope)
        remoteService.groupSent($scope, $rootScope, localService.afterSent)
    }
});

groupSent.controller("appController", function ($scope, $state, $interval, $http, $timeout, localService) {
    $scope.showFace = function(content){
        return localService.showFace(content);
    };

    $scope.showFile = function (filesContent) {
        var filesName = [];
        var files = filesContent.split(";");
        angular.forEach(files, function (v,i) {
            if (v.indexOf("|") != -1){
                filesName.push(v.split("|")[0])
            }
        });
        return filesName.join(", ")
    };
});

groupSent.controller('hypertextController', function($scope, $rootScope, $state, localService) {

    $scope.showBiaoQing=0; //默认关闭

    $scope.filesObject = [];

    $scope.file_upload = function(){
        //绑定文件上传事件
        $('#file_upload').fileupload({
            url: 'http://'+window.location.host+'/fileupload/',
            //url: 'http://124.172.188.65:8001/uploadMsgFile/',
            //dataType: 'JSONP',
            //forceIframeTransport: true,
            change: function(e, data) {//这个是选择文件的回调函数
                if($scope.sent_wxId){}else {
                    alert("请先选择发信人");
                    return false;
                }
                if($scope.filesObject.length + data.files.length > 1 ){
                    alert("每次最多发送一个文件");
                    return false;
                }
                if(!confirm("确定选择文件：" + data.files[0].name)){
                    return false;
                }
                if(data.files.length > 9){//这里是判断选择文件的个数,根据实际情况设置
                    alert("最多只能选择9个文件");
                    return false;
                }
                angular.forEach($scope.filesObject,function (v, i) {
                    var idx = data.files.findIndex(o=>{return v.filename == o.name});
                    if(idx > -1) {
                        alert("文件" + data.files[idx].name + "已存在，不需要重复选择");
                        data.files.splice(idx, 1);
                    }
                });
                for(var i=0;i < data.files.length;i++) {
                    if(data.files[i].size > 1024*1024*10)
                    {
                        alert("文件"+data.files[i].name+"大于10MB");
                        return false;
                    }
                }

                data.formData = { wx_id: $scope.sent_wxId};
                if(data.files.length == 0){
                    return false;
                }
            },
            done: function (e, data) {
                if(data && data.result){
                    severcheck(data.result);
                    data=JSON.parse(data.result);
                    var fileObject={"filename": data.filename, "filesize": data.filesize,"totallen": data.totallen, "content": data.content,
                        "MsgType": data.MsgType, "FileExt": data.FileExt}
                    // var appElement = document.querySelector('[ng-controller=appController]');
                    //获取$scope变量
                    // var $scope = angular.element(appElement).scope();
                    $scope.setFileMessage(fileObject);
                    $scope.filesObject.push(fileObject);
                    //同步到Angular控制器中，则需要调用$apply()方法即可
                    $scope.$apply();
                }
                if (data && !data.flag){
                    alert("上传失败")
                }
            },
            fail: function () {
                alert('上传出错！');
            }
        });
    };

    //发送文件内容
    $scope.setFileMessage = function(fileObject){
        if(!fileObject){
            return false;
        }
        //上级变量
        $rootScope.fileContent += fileObject.filename+"|"+fileObject.FileExt+"|"+fileObject.filesize+"|"+fileObject.totallen+"|1|"+fileObject.content+";";

        var targetHtml="附件：" + $scope.showFile($rootScope.fileContent);
        angular.element("#fileArea").html(targetHtml);
    };

    //发送聊天信息
    $scope.setTextMessage=function(){
        if($("#editArea").html().trim() == ''){
            return false;
        }

        var content=$("#editArea").html();
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

        //上级变量
        $rootScope.content = content;
    };

    //打开表情选择窗口
    $scope.showExpression=function(event){
        $scope.showBiaoQing=1;
        $scope.biaoQingIndex=1;
        event=event||window.event;
        event.stopPropagation();//阻止事件冒泡,防止隐藏
    };
    //关闭弹窗窗
    document.addEventListener("click",function(){
        if((!$scope.foucus && $("#profile").html() != '') || $("#mmpop_search").html() != ''){
            $state.go('none');
        }
        if($scope.showBiaoQing==1) {
            $scope.showBiaoQing=0;
        }
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
        if(localService.QQFaceMap.hasOwnProperty(face)){
            classStr=classStr+localService.QQFaceMap[face];
            var targetHtml="<img class='"+classStr+"' text='"+text+"' src='/static/img/wx/spacer.gif'>";
            angular.element("#editArea").append(targetHtml);
        }
    };
    //回车键事件
    $scope.editAreaKeydown=function(event){
        if (event.ctrlKey && event.keyCode == 13){
            return true;
        }
        else if(event.keyCode == 13){
            // $scope.sendTextMessage();    //20190329 现在什么都不做
            return false;
        }
    };



});

//滚动指令
groupSent.directive('whenScrolled', function() {
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




