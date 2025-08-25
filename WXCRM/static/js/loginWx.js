taskSeq='';
xValue='';
watingClickResult=false;
countdown_finishid="";
countdown_showid="";
countdown_func='';
cache_wx_id='';
logout_finish_flag=-1;
finish_refresh_friend_list=-1;
if_ready_countdown=false;
if_ready_checkpasswd=false;
login_state=''
check_passwd_timeout=false
weixin_open=false
show_time_out_pic=true
timer=''
xValueFinal=''
isFirstTime=0
function async_login_info(){
    $.ajax({
        type: 'POST',
        dataType: 'json',
        traditional:true,//传递数组
        async:true,
        url: '/WXCRM/loginData/',
        data: {"type":"getLoginInfo",
                "taskSeq":taskSeq
        },
        success: function (res) {
            severcheck(res);
            console.log(res);
            var type=res.type;
            if(type!=='1'&&res.state==='20') {
                logout_finish_flag=1
            }else if(type==='1'){
                if(res.state==='10'||res.state==='23'){
                            finish_refresh_friend_list=1
                        }
            }
        }
    })
}
function countdown_sec(seconds,showid,object_id,callbackfun){
    if(object_id){countdown_finishid=object_id}
    if(showid){countdown_showid=showid}
    if(callbackfun){countdown_func=callbackfun}
    if(logout_finish_flag===0||finish_refresh_friend_list===0){
        async_login_info()
    }
    if(seconds>0){
        $(countdown_showid).html(seconds);
        console.log('seconds:'+seconds)
        // if(if_ready_checkpasswd&&seconds===20){if(!weixin_open){console.log('倒计时剩余20未打开微信，停止任务');show_time_out_pic=false;checkPasswdTimeout();show_time_out_pic=true;}else{console.log('倒计时剩余20打开微信，不停止任务')}}
        seconds=seconds-1;
        if(logout_finish_flag===1){seconds=1;logout_finish_flag=-1}
        if(finish_refresh_friend_list===1){seconds=1;finish_refresh_friend_list=-1}
        timer=setTimeout("countdown_sec("+seconds+")",1000);
    }else{
        logout_finish_flag=-1
        finish_refresh_friend_list=-1
        $(countdown_finishid).hide()
        if(countdown_func){
            countdown_func()
        }
    }
}

function login(id){
    if(confirm("确定进行微信登录吗？")){
        var header_text='微信登录';
        var title_text='正在进行密码校验';
        var red_text='';
        var main_text='<img src="/static/img/wxAccount/2.png" style="width: 243px; height: 253px" id="login_show_img">';
        var bigfont_text='';
        var close_text='请勿关闭该页面';
        var hide_close_flag=true;
        refreshScene(header_text,title_text,main_text,red_text,bigfont_text,close_text,hide_close_flag);
        // debugger
         $.ajax({
            type: 'POST',
            dataType: 'json',
            traditional:true,//传递数组
            async:false,
            url: '/WXCRM/loginData/',
            data: {"type":"loginTask",
                    "wxLoginId":id
            },
            success: function (res) {
                severcheck(res);
                 var result=res.result;
                 if(result===1){
                     var ifStart=res.ifStart;
                     taskSeq=res.taskSeq;
                     var ifTask=res.ifTask;
                     if(ifStart===1){
                         $("#wx_account_login").hide()
                         queryWxInfo(1);
                         alert('该账号已在线！')
                     }else{
                        if_ready_countdown=false
                        if_ready_checkpasswd=false
                        check_passwd_timeout=false
                         weixin_open=false
                        setTimeout("getLoginInfo()",1000);
                     }
                 }else{
                     $("#wx_account_login").hide()
                     alert('无法登陆，请联系管理员。')
                 }
            },
             error:function(){
                $("#wx_account_login").hide()
             }
        });
     }
}
function refreshScene(header_text,title_text,main_text,red_text,bigfont_text,close_text,hide_close_flag){
    clearTimeout(timer)
    $("#login_header").text(header_text);
    $('#login_step_title').html(title_text)
    $('#login_step_main_pic').html(main_text);
    $('#login_step_red_notice').html(red_text)
    $('#login_step_bigfont_notice').html(bigfont_text)
    $('#login_step_close_notice').html(close_text)
    $(".close_this_modal").show()
    if(hide_close_flag){
        // $(".close_this_modal").hide()
        $("#login_mask").addClass('disable_click')
    }else{
        // $(".close_this_modal").show()
        $("#login_mask").removeClass('disable_click')
    }
    $("#task_list_bar").hide()
    $("#wx_account_login").show()
}
function getLoginInfo(){
    if(check_passwd_timeout){
        return
    }
    $("#task_list_bar").hide()
    $('#login_step_main_pic').show();
    $('#login_step_red_notice').show()
    $('#login_step_bigfont_notice').show()
    $('#login_step_close_notice').show()
    $.ajax({
        type: 'POST',
        dataType: 'json',
        traditional:true,//传递数组
        async:false,
        url: '/WXCRM/loginData/',
        data: {"type":"getLoginInfo",
                "taskSeq":taskSeq
        },
        success: function (res) {
            severcheck(res);
            console.log(res);
            var type=res.type;
            if(type==='1'){//登陆
                var result=res.result;
                if(result===1){
                    var picture=res.picture;
                    var state=res.state;
                    login_state=state;
                    if(state>0){
                        weixin_open=true
                    }
                    if(state>5){
                        if_ready_checkpasswd=false
                    }
                    var taskStatus=res.taskStatus;
                    var xValueDB=res.xValueDB;
                    var remark=res.remark;
                    isFirstTime=res.isFirstTime  //1是0否
                    if(state==='11'){//密码错误
                            var title_text='';
                            if(isFirstTime==='1'){
                                title_text='（1/3）正在进行密码校验'
                            }else{
                                title_text='（1/2）正在检查微信任务状态'
                            }
                            if_ready_countdown=false
                            var header_text='微信登录';
                            var red_text='提示：您输入的微信登录密码错误，请关闭该页面后修改密码再登录';
                            var main_text='<img src="/static/img/wxAccount/1.png" style="width: 242px; height: 209px" id="login_show_img">';
                            var bigfont_text='请点击右上角关闭';
                            var close_text='';
                            var hide_close_flag=false;
                            refreshScene(header_text,title_text,main_text,red_text,bigfont_text,close_text,hide_close_flag);
                            // clearTimeout(t);
                            return false;
                    }else if(taskStatus===3&&if_ready_checkpasswd){//30秒超时导致没打开微信就退出
                        check_passwd_timeout=true
                        console.log('打开微信30秒超时')
                    }else if((taskStatus===3&&!if_ready_checkpasswd)||state==='24'){//超时
                        var title_text='';
                        var header_text='微信登录';
                        var red_text='';
                        var main_text='<img src="/static/img/wxAccount/outoftime.png" style="width: 186px; height: 211px" class="login_show_img">';
                        var bigfont_text='由于某种原因，此次上线已经<span class="big_red_font">超时</span>，请关闭弹框重新上线';
                        var close_text='请关闭该页面';
                        var hide_close_flag=false;
                        refreshScene(header_text,title_text,main_text,red_text,bigfont_text,close_text,hide_close_flag);
                        queryWxInfo(1);
                    }else if(state==='8'||state==='9'||state==='10'||state==='23'||state==='25'){//25 扫码后点击了登录8载入数据中 9正在刷新好友 10刷新好友完成（23失败） 上线结束
                        if(!if_ready_countdown){
                            var title_text='';
                            if(isFirstTime==='1'){
                                title_text='（3/3）登录成功，正在加载信息'
                            }else{
                                title_text='（2/2）登录成功，正在加载信息'
                            }
                            var header_text='微信登录';
                            var red_text='提示：手机上的微信会自动下线，并弹出已在系统登录的提示';
                            var main_text='<img src="/static/img/wxAccount/3.png" style="width: 390px; height: 278px" class="login_show_img">';
                            if(state==='25'){
                                var bigfont_text='信息加载需要一段时间，请耐心等待';
                                var close_text='看到头像后表示信息加载完成';
                                var hide_close_flag=true;
                                refreshScene(header_text,title_text,main_text,red_text,bigfont_text,close_text,hide_close_flag);
                            }else{
                                var bigfont_text='信息加载预计<span class="big_red_font"><span id="countdown_num">20</span>秒</span>完成';
                                var close_text='请勿关闭该页面';
                                var hide_close_flag=true;
                                refreshScene(header_text,title_text,main_text,red_text,bigfont_text,close_text,hide_close_flag);
                                countdown_func=''
                                countdown_sec(20,"#countdown_num","#wx_account_login","");
                            }
                        }
                        if(state==='9'||state==='8'){
                            if_ready_countdown=true
                            if(state==='8'){//如果还没开始刷新好友，状态还是离线
                                setTimeout('getLoginInfo()', 200);
                            }else{
                                finish_refresh_friend_list=0
                                queryWxInfo(1);//开始刷新好友了，状态已经是在线了，刷新一下列表然后不再获取任务状态
                            }
                        }
                        // clearTimeout(t);
                    }else{

                        if((state==='0'&&!xValueDB)||state==='1'||state==='2'||state==='3'||state==='4'||state==='5'||!state){//正在登录
                            if(!if_ready_checkpasswd) {
                                var title_text = '';
                                var red_text = '';
                                var main_text = '';
                                if (isFirstTime === '1') {
                                    title_text = '（1/3）正在进行密码校验';
                                    red_text = "提示：密码校验完成后，手机上登录的该微信号会自动下线，并弹出已在系统登录的提示";
                                    main_text = '<img src="/static/img/wxAccount/2.png" style="width: 243px; height: 253px" id="login_show_img">';

                                } else {
                                    title_text = '（1/2）正在进行密码校验';
                                    red_text = '';
                                    main_text = '<img src="/static/img/wxAccount/2.png" style="width: 243px; height: 253px" id="login_show_img">';
                                }
                                var header_text = '微信登录';
                                var bigfont_text = '密码校验预计<span class="big_red_font"><span id="countdown_num_wx">60</span>秒</span>完成';
                                var close_text = '请勿关闭该页面';
                                var hide_close_flag = true;
                                refreshScene(header_text, title_text, main_text, red_text, bigfont_text, close_text, hide_close_flag);
                                countdown_sec(60, "#countdown_num_wx", "", checkPasswdTimeout);
                            }
                            if_ready_checkpasswd=true
                            t=setTimeout('getLoginInfo()', 1000);
                        }else if( state==='16'||state==='17'||state==='18'||state==='22' ){
                            var title_text='（2/3）正在进行登录授权'
                            var header_text='微信登录';
                            var red_text='提示：此微信号为首次登录，请您保持该微信在手机的登录状态以便授权系统登录';
                            if(state==='22'){red_text='提示：请在手机上点击授权';}
                            var main_text='<img src="/static/img/wxAccount/4.png" style="width: 250px; height: 188px" id="login_show_img">';
                            var bigfont_text='';
                            var close_text='请勿关闭该页面';
                            var hide_close_flag=true;
                            refreshScene(header_text,title_text,main_text,red_text,bigfont_text,close_text,hide_close_flag);
                            t=setTimeout('getLoginInfo()', 1000);
                        }else if(picture!=='' && (state==='6'||state==='15')&&xValueDB===""){ // 返回未点击过的图片
                            if(state==='15'){
                                watingClickResult=false;
                            }
                            if(!watingClickResult){
                                var title_text='（2/3）正在进行登录授权'
                                var header_text='微信登录';
                                var red_text='提示：请 <span class="big_font"> 点击 </span> 图中滑块暗处中心点，进行授权校验';
                                if(state==='15'){red_text='提示：请 <span class="big_font"> 重新点击 </span> 图中滑块暗处中心点，进行授权校验';}
                                var main_text='<img src='+picture+' style="width: 350px; height: 188px" onclick="mapOnClick(event)" id="login_show_img">';
                                var bigfont_text='';
                                var close_text='请勿关闭该页面';
                                var hide_close_flag=true;
                                refreshScene(header_text,title_text,main_text,red_text,bigfont_text,close_text,hide_close_flag);
                                $('#login_show_img').attr("src", picture);
                                  watingClickResult=false;
                                  clearTimeout(t) ;
                             }else{
                                  t=setTimeout('getLoginInfo()', 1000);
                             }
                         }else if (xValueDB=="" && (state==='7'||state==='14')&&picture!=""){//需要扫码验证
                            var title_text='（2/3）正在进行登录授权'
                            var header_text='微信登录';
                            var red_text='提示：请使用登录此手机的微信扫描二维码，进行授权验证';
                            if(state==='14'){red_text='提示：请使用登录此手机的微信 <span class="big_font"> 再次扫描 </span> 二维码，进行授权验证 '}
                            var main_text='<img src='+picture+' style="width: 244px; height: 244px"  id="login_show_img">';
                            var bigfont_text='';
                            var close_text='请勿关闭该页面';
                            var hide_close_flag=true;
                            refreshScene(header_text,title_text,main_text,red_text,bigfont_text,close_text,hide_close_flag);
                            $('#login_show_img').attr("src", picture);
                            t=setTimeout('getLoginInfo()', 1000);
                         }else{
                            t=setTimeout('getLoginInfo()', 1000);
                         }
                     }
                 }else{
                      alert('获取登录信息出错！')
                 }
            }else{
                var title_text='（1/2）正在检查微信任务状态'
                var header_text='微信下线';
                var red_text='';
                var main_text='<img src="/static/img/wxAccount/5.png" style="width: 242px; height: 209px;left: 52%;" id="login_show_img">';
                var bigfont_text='';
                var close_text='请勿关闭该页面';
                var hide_close_flag=true;
                refreshScene(header_text,title_text,main_text,red_text,bigfont_text,close_text,hide_close_flag);
                 var state=res.state;
                 var taskStatus=res.taskStatus;
                 if(taskStatus===3 || state==='19'){//系统异常
                        clearTimeout(t) ;
                        $("#wx_account_login").hide()
                        alert("下线失败！");
                        queryWxInfo(1);
                        return false;
                 }
                 if(state==='20') {//下线成功
                    var title_text=''
                    var header_text='微信下线';
                    var red_text='';
                    var main_text='<img src="/static/img/wxAccount/9.png" style="width: 265px; height: 194px" id="login_show_img">';
                    var bigfont_text='请点击右上角关闭';
                    var close_text='';
                    var hide_close_flag=false;
                    refreshScene(header_text,title_text,main_text,red_text,bigfont_text,close_text,hide_close_flag);
                     queryWxInfo(1);
                 }else if(state in ['1','18','21']){
                    var title_text='（2/2）正在下线'
                    var header_text='微信下线';
                    var red_text='';
                    var main_text='<div style="width: 174px; height: 174px" id="login_show_img" class="big_circle">15</div>';
                    var bigfont_text='';
                    var close_text='请勿关闭该页面';
                    var hide_close_flag=true;
                    refreshScene(header_text,title_text,main_text,red_text,bigfont_text,close_text,hide_close_flag);
                    logout_finish_flag=0
                    countdown_sec(15,".big_circle","",logout_finish)
                     // t=setTimeout('getLoginInfo()', 1000);
                 }else if(state==='19'){
                   alert('需要修改密码才能退出微信，请用户通过手机登陆微信并修改密码！');
                 }else{
                     setTimeout('getLoginInfo()', 1000)
                 }
             }
        }
    });
}
function logout_finish(){
    var title_text=''
    var header_text='微信下线';
    var red_text='';
    var main_text='<img src="/static/img/wxAccount/9.png" style="width: 265px; height: 194px" id="login_show_img">';
    var bigfont_text='请点击右上角关闭';
    var close_text='';
    var hide_close_flag=false;
    refreshScene(header_text,title_text,main_text,red_text,bigfont_text,close_text,hide_close_flag);
    queryWxInfo(1);
    setTimeout("close_wx_login_modal()",1000);
}
function checkPasswdTimeout(){
    var title_text = '';
    var red_text = '';
    var main_text = '';
    var header_text = '微信登录';
    if (isFirstTime === '1') {
        title_text = '（1/3）正在进行密码校验';
        red_text = "提示：密码校验完成后，手机上登录的该微信号会自动下线，并弹出已在系统登录的提示";
        main_text = '<img src="/static/img/wxAccount/2.png" style="width: 243px; height: 253px" id="login_show_img">';
    } else {
        title_text = '（1/2）正在进行密码校验';
        red_text = '';
        main_text = '<img src="/static/img/wxAccount/2.png" style="width: 243px; height: 253px" id="login_show_img">';
    }
    var bigfont_text = '登录中，请耐心等待';
    var close_text='请勿关闭该页面';
    var hide_close_flag = true;
    refreshScene(header_text,title_text,main_text,red_text,bigfont_text,close_text,hide_close_flag);
    // check_passwd_timeout=true
    // $.ajax({
    //     type: 'POST',
    //     dataType: 'json',
    //     traditional:true,//传递数组
    //     async:false,
    //     url: '/WXCRM/stopTaskBySeq/',
    //     data: {"taskSeq":taskSeq
    //     },
    //     success: function (res) {
    //         severcheck(res);
    //         if(res.result>0 && show_time_out_pic){
    //             var title_text='';
    //             var header_text='微信登录';
    //             var red_text='';
    //             var main_text='<img src="/static/img/wxAccount/outoftime.png" style="width: 186px; height: 211px" class="login_show_img">';
    //             var bigfont_text='由于某种原因，密码验证<span class="big_red_font">超时</span>，请关闭弹框重新上线';
    //             var close_text='请关闭该页面';
    //             var hide_close_flag=false;
    //             refreshScene(header_text,title_text,main_text,red_text,bigfont_text,close_text,hide_close_flag);
    //         }
    //     }
    // })

}
function logout(id){
    if(confirm("确定要退出微信登录吗？")){
        var title_text='（1/2）正在检查微信任务状态 '
        var header_text='微信下线';
        var red_text='';
        var main_text='<img src="/static/img/wxAccount/5.png" style="width: 242px; height: 209px;left: 52%;"" id="login_show_img">';
        var bigfont_text='';
        var close_text='请勿关闭该页面';
        var hide_close_flag=true;
        refreshScene(header_text,title_text,main_text,red_text,bigfont_text,close_text,hide_close_flag);
        var logout_flag=false
        $.ajax({
            type: 'POST',
            dataType: 'json',
            async:false,
            url: '/WXCRM/logoutTaskCheck/',
            data: {"wxLoginId":id},
            success: function (res) {
                severcheck(res);
                // console.log(res)
                // debugger;
                if(res.flag>0){
                    var taskList=res.taskList;
                    if(taskList.length>0){
                        logout_flag=true
                        cache_wx_id=id
                        var temp_html=''
                        for(var i=0;i<taskList.length;i++){
                            temp_html=temp_html+'<div class="task_list_item"><div class="task_index">'+(i+1)+'</div><div class="task_name">'+taskList[i]+'</div></div>'
                        }
                        $("#login_header").text("微信下线");
                        $('#login_step_title').html('（1/2）正在检查微信任务状态 ')
                        $('#login_step_main_pic').hide();
                        $('#login_step_red_notice').hide()
                        $('#login_step_bigfont_notice').hide()
                        $('#login_step_close_notice').hide()
                        $(".close_this_modal").show()
                        $("#login_mask").removeClass('disable_click')
                        $("#task_list_item_bar").html(temp_html)
                        $("#task_list_bar").show()
                        $("#wx_account_login").show()
                    }
                }
            }
        })
        if(!logout_flag){
            $.ajax({
            type: 'POST',
            dataType: 'json',
            //headers: {"X-CSRFToken": $.cookie('csrftoken')},
            traditional:true,//传递数组
            async:false,
            url: '/WXCRM/loginData/',
            data: {"type":"logoutTask",
                    "wxLoginId":id
            },
            success: function (res) {
                severcheck(res);
                 var result=res.result;
                 if(result==1){
                     var ifStart=res.ifStart;
                     taskSeq=res.taskSeq;
                     if(ifStart==0){
                         $("#wx_account_login").hide()
                         queryWxInfo(1);
                         alert('该账号当前已经是下线状态')
                     }else{
                        setTimeout("getLoginInfo()",1000);
                     }
                 }else{
                     alert('无法下线，请联系管理员。');
                 }
            }
        });
        }

     }

}
function contunueLogout(){
    close_wx_login_modal()
    if(cache_wx_id){
        var title_text='（1/2）正在检查微信任务状态'
        var header_text='微信下线';
        var red_text='';
        var main_text='<img src="/static/img/wxAccount/5.png" style="width: 242px; height: 209px;left: 52%;" id="login_show_img">';
        var bigfont_text='';
        var close_text='请勿关闭该页面';
        var hide_close_flag=true;
        refreshScene(header_text,title_text,main_text,red_text,bigfont_text,close_text,hide_close_flag);
        $.ajax({
            type: 'POST',
            dataType: 'json',
            //headers: {"X-CSRFToken": $.cookie('csrftoken')},
            traditional:true,//传递数组
            async:false,
            url: '/WXCRM/loginData/',
            data: {"type":"logoutTask",
                    "wxLoginId":cache_wx_id
            },
            success: function (res) {
                severcheck(res);
                 var result=res.result;
                 if(result===1){
                     var ifStart=res.ifStart;
                     taskSeq=res.taskSeq;
                     var ifTask=res.ifTask
                     if(ifStart===0){
                         $("#wx_account_login").hide()
                         queryWxInfo(1);
                         alert('该账号当前已经是下线状态')
                     }else{
                        setTimeout("getLoginInfo()",1000);
                     }
                 }else{
                     $("#wx_account_login").hide()
                     alert('无法下线，请联系管理员。');
                 }
            },
            error:function(){
                $("#wx_account_login").hide()
            }
        });
    }else{
        alert("无法确定需要下线的微信号！")
    }

}
function stopLogout(){
    cache_wx_id=''
    close_wx_login_modal()
}
function mapOnClick(e){
    e = e || window.event;
    var imgId ='#'+ $(e.target).attr('id');
    var currentWidth = $(imgId).width();
    var currentHeight = $(imgId).height();
    var offsetX = e.pageX - $(imgId).offset().left;
    var offsetY = e.pageY - $(imgId).offset().top;
    var x = offsetX / currentWidth;
    var y = offsetY / currentHeight;
    xValueFinal=x
    // $("#xValue").val(x);
    console.log(xValueFinal)
    //alert(x + ':' + y);

    $('#loginTips').html('正在验证，请稍候……')
     writeCoord();
    $('#checkCodeImgDiv').hide();
    watingClickResult=true;
    t=setTimeout('getLoginInfo()', 1000);
}

function writeCoord() {
    // xValue = $("#xValue").val();
    $.ajax({
        type: 'POST',
        dataType: 'json',
        //headers: {"X-CSRFToken": $.cookie('csrftoken')},
        traditional: true,//传递数组
        url: '/WXCRM/loginData/',
        data: {
            "type": "writeCoord",
            "xValue": xValueFinal,
            "taskSeq": taskSeq
        },
        success: function (res) {
            severcheck(res);
            var result = res.result;
            if (result == 1) {
                alert('保存中心点成功,请等待验证结果');
            } else {
                alert('保存中心点失败');
            }
        }
    });
}
