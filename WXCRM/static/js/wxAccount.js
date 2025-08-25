$(function() {
    $(".input_account_bar>input").on("click",function(){
        $(".input_account_bar").removeClass("input_account_bar_active")
        $(this.parentNode).addClass("input_account_bar_active")
    })
});
function open_add_wx_modal(){

    $("#add_wx_account").show()
}
function open_login_modal(){
    var title_text='（2/2）登录成功，正在加载信息'
    var header_text='微信登录';
    var red_text='提示：手机上的微信会自动下线，并弹出已在系统登录的提示';
    var main_text='<img src="/static/img/wxAccount/3.png" style="width: 390px; height: 278px" class="login_show_img">';
    var bigfont_text='信息加载预计<span class="big_red_font"><span id="countdown_num">5</span>秒</span>完成';
    var close_text='请勿关闭该页面';
    var hide_close_flag=true;
    refreshScene(header_text,title_text,main_text,red_text,bigfont_text,close_text,hide_close_flag);
    countdown_sec(5,'#countdown_num');
}
function open_edit_wx_modal(wx_login_id,phone_num,passwd){
    if(!phone_num&&wx_login_id){ //wx_Modal_edit展示微信号不可编辑、phone_no_Modal_edit手机号为空非必填、password_Modal_edit密码为空必填
        $("#wx_Modal_edit").parent().show()
        $("#wx_Modal_edit").prev().removeClass('lable_edit_input_star')
        $("#wx_Modal_edit").val(wx_login_id).attr("disabled","true")
        $("#phone_no_Modal_edit").val(phone_num).removeAttr('disabled')
        $("#password_Modal_edit").val(passwd).attr('type',"password")
        $(".edit_show_passwd").show()
    }else if(phone_num&&wx_login_id && phone_num===wx_login_id){//微信号不展示、手机号展示不可改、密码为空必填
        $("#wx_Modal_edit").parent().hide()
        $("#wx_Modal_edit").val(wx_login_id)
        $("#phone_no_Modal_edit").val(phone_num).attr("disabled","true")
        $("#password_Modal_edit").val(passwd).attr('type',"password")
        $(".edit_show_passwd").show()
    }else if(phone_num&&wx_login_id && phone_num!==wx_login_id){//微信号展示不可修改、手机号展示可改、密码为空必填
        $("#wx_Modal_edit").parent().show()
        $("#phone_no_Modal_edit").val(phone_num)
        $("#wx_Modal_edit").val(wx_login_id).attr("disabled","true")
        $("#password_Modal_edit").val(passwd).attr('type',"password")
        $(".edit_show_passwd").show()
    }
    $("#edit_wx_account").show()
}
function close_add_wx_modal(){
    $("#add_wx_account").hide()
    $(".password_eye").hide()
    createInfoClear()
}
function close_wx_login_modal(){
    $("#wx_account_login").hide()
    $('#login_step_main_pic').show();
    $('#login_step_red_notice').show()
    $('#login_step_bigfont_notice').show()
    $('#login_step_close_notice').show()
    $("#task_list_bar").hide()
}
function close_edit_wx_modal(){
    $("#edit_wx_account").hide()
    $(".edit_show_passwd").hide()
    $(".edit_show_passwd_close_eye").hide()
    editInfoClear()
}
function add_by_this_type(obj,type){
    $(obj).removeClass("tabs_tab_inactive").addClass("tabs_tab_active")
    $(obj).siblings().removeClass("tabs_tab_active").addClass("tabs_tab_inactive")
    if(type===2){
        accountType=2
        $(".tabs_ink_bar").css("width","137px").css("transform",'translate3d(116px, 0px, 0px)');
        $(".tabs_content").children(":first").removeClass('tabs_tabpane_active').addClass('tabs_tabpane_inactive')
        $(".tabs_content").css("margin-left","-100%")
        $(".tabs_content").children(":nth-child(2)").removeClass('tabs_tabpane_inactive').addClass('tabs_tabpane_active')
    }else{
        accountType=1
        $(".tabs_ink_bar").css("width","96px").css("transform",'translate3d(0px, 0px, 0px)');
        $(".tabs_content").children(":nth-child(2)").removeClass('tabs_tabpane_active').addClass('tabs_tabpane_inactive')
        $(".tabs_content").css("margin-left","0")
        $(".tabs_content").children(":first").removeClass('tabs_tabpane_inactive').addClass('tabs_tabpane_active')
    }
}
function if_eye_show(obj){
    if(obj.value){
        $(obj).next().show()
    }else{
        $(obj).next().hide()
        $(obj).attr('type','password')
        $(obj).next().removeClass('input_hide_passwd_icon').addClass('input_show_passwd_icon')
    }
}

function toggle_show_pwd(obj){
    var pre_obj=$(obj).prev()
    if(pre_obj.attr('type')==='password'){
        pre_obj.attr('type','text')
        $(obj).removeClass('input_show_passwd_icon').addClass('input_hide_passwd_icon')
    }else{
        pre_obj.attr('type',"password")
        $(obj).removeClass('input_hide_passwd_icon').addClass('input_show_passwd_icon')
    }
}
function if_edit_eye_show(obj){
    if(obj.value&&$(".edit_show_passwd_close_eye").is(":hidden")){
        $(".edit_show_passwd").show()
    }else{
        $(".edit_show_passwd").hide()
        $(".edit_show_passwd_close_eye").hide()
        $(obj).attr('type','password')
    }
}
function toggle_show_edit_pwd(){
    var pre_obj=$("#password_Modal_edit")
    if(pre_obj.attr('type')==='password'){
        pre_obj.attr('type','text')
        $(".edit_show_passwd").hide()
        $(".edit_show_passwd_close_eye").show()
    }else{
        pre_obj.attr('type',"password")
        $(".edit_show_passwd").show()
        $(".edit_show_passwd_close_eye").hide()
    }
}
function editInfoClear() {
    $('#wx_Modal_edit').val("");
    $('#phone_no_Modal_edit').val("");
    $('#password_Modal_edit').val("");
}