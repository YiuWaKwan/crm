window.onload = function() {
    var wx_id="";
	$.ajax({
        type: 'post',
        url: '../get_weixin/',
        data: {'oper_id':7},
        async:false,
        cache: 'false',
        success: function (result) {
            severcheck(result);
            result = JSON.parse(result);
            html = '';
            for (x in result){
                html += "<div class='list'datanum='" + result[x]['fri_num'] + "' addnum = '"+result[x]['add_num']+"' data='" + result[x]['wx_id'] + "," + result[x]['phone_no'] + "," + result[x]['wx_name'] + "'><img src='" + result[x]['head_picture'] + "' alt=''><div class='list_1'><span class='s1'>" +
                    result[x]['wx_name']+"(</span><span class='s2'>"+result[x]['fri_num']+"</span><span class='s3'>个好友)</span></div></div>";
            }
            $("#friend_list").html(html);
                $(".list").click(function () {
                    wx_id = $(this).attr('data').split(',')[0];
                    console.log(wx_id);
                    $("#detail").html($(this).html());
                    $('#friend_sum').html($(this).attr('datanum'));
                    $('#add_num').html($(this).attr('addnum'))
                });

	        // $("#search_btn").click(function(){
            //
	        // })
            $("#search").bind("input propertychange",function(){
                  var search = $(this).val();
                  if (search !="") {
                      $('.friend_list .list').each(function () {
                          this.style.display = 'none';
                          if (((this.getAttribute('data').split(',')[0]).indexOf(search))>=0 || (( this.getAttribute('data').split(',')[1]).indexOf(search))>=0 ||(( this.getAttribute('data').split(',')[2]).indexOf(search))>=0) {
                              this.style.display = 'block';
                          }
                      })
                  }else
                  {
                      $('.friend_list .list').each(function () {
                        this.style.display = 'block'
                      })
                  }
            });
        },
        // error: function (e) {
        //     alert("未知错误，请联系系统管理员。");
        // }
    });
	var modal = document.getElementById('modal');
	var cancel = document.getElementById('before');
	cancel.addEventListener('click', function(){
                modal.style.display = "none";
            });
	// $('#submit').click(function () {
	//     if(wx_id == ''){
    //         alert('请选择微信号！')
    //     }else {
	//         if ($('#sayhi').val() == '') {
    //             sayHi = $('#sayhi').attr('placeholder')
    //         }
    //         else {
    //             sayHi = $('#sayhi').val()
    //         }
    //         $.ajax({
    //             type: 'post',
    //             url: '/commit_task/',
    //             data: {'oper_id': 7, 'wx_id': wx_id, 'sayHi': sayHi},
    //             cache: 'false',
    //             dataType: 'json',
    //             success: function (result) {
    //                 console.log(result)
    //                 if (result.msg == 'success') {
    //                     window.location.href = '../WXCRM/friend_onekey/'
    //                 }else{
    //                     var modal = document.getElementById('modal');
    //                     modal.style.display = "block";
    //                 }
    //             },
    //             error: function (e) {
    //                 alert("未知错误，请联系系统管理员。");
    //             }
    //         })
    //     };
    // });
    	$('#submit').click(function () {
	    if(wx_id == ''){
            alert('请选择微信号！')
        }else {
	        if ($('#sayhi').val() == '') {
                sayHi = $('#sayhi').attr('placeholder')
            }
            else {
                sayHi = $('#sayhi').val()
            }
            $.ajax({
                type: 'post',
                url: '/task_exist/',
                data: { 'wx_id': wx_id},
                cache: 'false',
                dataType: 'json',
                success: function (result) {
                    if(result[0]['type'] == '0'){
                        $.ajax({
                            type: 'post',
                            url: '/commit_task/',
                            data: {'wx_id': wx_id, 'sayHi': sayHi,'type':'2'},
                            cache: 'false',
                            dataType: 'json',
                            success: function (result) {
                                console.log(result)
                                if (result.msg == 'success') {
                                    window.location.href = '../WXCRM/friend_onekey/'
                                }
                            },
                            // error: function (e) {
                            //     alert("未知错误，请联系系统管理员。");
                            // }
                            });
                    }else{
                        var modal = document.getElementById('modal');
                        modal.style.display = "block";
                        html='';
                        html+='<dl  style="height: 70px; margin-left: 0px;text-align: center;">\n' +
                            '                        <span style="display: inline-block;text-align: center;padding-top: 30px;">\n' +
                            '                            该微信账号当前有正在执行的加好友任务，任务详情：\n' +
                            '                        </span>\n' +
                            '                    </dl>\n' +
                            '                    <dl style="">\n' +
                            '                        任务名称：'+ result[0]['task_name'] +
                            '                    </dl>\n' +
                            '                    <dl>\n' +
                            '                        创建时间：' +result[0]['create_time']+
                            '                    </dl>\n' +
                            '                    <dl>\n' +
                            '                        完成进度：'+result[0]['finish'] +
                            '                    %</dl>\n' +
                            '                    <dl>\n' +
                            '                        继续创建任务将终止该历史任务！\n' +
                            '                    </dl>';
                        $('#body').html(html);
                    }
                },
                // error: function (e) {
                //     alert("未知错误，请联系系统管理员。");
                // }
            })
        };
    })
    $('#back').click(function () {
        window.location.href = '/friend_select/'
    });
    $('#commit').click(function () {
        $('#title').html('创建任务中');
        $('#body').html('<dl  style="height: 70px; margin-left: 0px;text-align: center;"><img src="/static/img/onekey/loading.gif" style="text-align: center;padding-top: 20px;"></dl>')
        document.getElementById('footer').style.display='none';
        $.ajax({
                            type: 'post',
                            url: '/commit_task/',
                            data: {'wx_id': wx_id, 'sayHi': sayHi, 'type':'1'},
                            cache: 'false',
                            dataType: 'json',
                            success: function (result) {
                                console.log(result)
                                if (result.msg == 'success') {
                                    window.location.href = '../WXCRM/friend_onekey/'
                                }
                            },
                            // error: function (e) {
                            //     alert("未知错误，请联系系统管理员。");
                            // }
                            });
    });
    $('#cancel').click(function () {
        window.location.href = '../WXCRM/friend_onekey/'
    });
};


function severcheck(data) {
    if(data && typeof data=='string'){
        if(data.indexOf("<title>会话丢失</title>") !=-1){
            alert("会话丢失，请重新登录！");
            window.location.href='http://'+window.location.host+'/hl/';
        }
        else if(data.indexOf("<title>账号被下线</title>") !=-1){
            alert("你的账号已在别的地方登录，被迫下线！");
            window.location.href='http://'+window.location.host+'/hl/';
        }
    }
}