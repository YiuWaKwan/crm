/**
 * Created by xiaox on 2018/8/15.
 */

var taskID="None";
$(document).ready(function(){
        setInterval(function () {
         viewmodal = document.getElementById('viewmodal');
            if(viewmodal.style.display == "block"){
                startRequest(2,taskID)
            };
        }, 2000);

 });


 function modalinit(taskid) {
         $('#taskId').val("");
         $('#taskId').val(taskid);
         //重置
        $('#taskSpan').html("");
        $('#addrDiv').html("");
        $('#tmtDiv').html("");
        $('#jobDiv').html("");
        $('#sexDiv').html("");
        $('#ageDiv').html("");
        $('#consumeDiv').html("");
        $('#flagDiv').html("");
        $('#addAddrDiv').html("");
        $('#addTimeDiv').html("");
        $('#greetDiv').html("");
        $('#remarkDiv').html("");
        $('#taskcnt').html("");
        $("#chatresult").html("");
        $('#nicheng').html("");
     $.ajax({
         type: "POST",
         url: "/friend_task/",
         dataType: "json",
         async: false,
         data: {'taskid':String(taskid)},
         success: function(data) {
             $('#taskSpan').append(data.task);
             $('#addrDiv').append(data.addr);
             $('#tmtDiv').append(data.tmt);
             $('#jobDiv').append(data.job);
             $('#sexDiv').append(data.sex);
             $('#ageDiv').append(data.age);
             $('#consumeDiv').append(data.consume);
             $('#addAddrDiv').append(data.addAddr);
             $('#addTimeDiv').append(data.addTime);
             $('#greetDiv').append(data.greet);
             $('#remarkDiv').val(data.remark);
             $('#taskcnt').append(data.taskcnt);
             $('#exectime').val(data.exectime);
             $('#nicheng').append(data.nicheng);
             document.getElementById("headpic").src=data.pictureurl;

             $("#sendcnt").html("");
             $("#passcnt").html("");
             $("#sendcnt").append("-");
             $("#passcnt").append("-");
             $('#sendtime').val("None");

             if(data.remark==null){$('#remarkDiv').val("无");}

             taskstate=data.taskstate;
             straa=data.flag
             //console.log('straa:'+straa)
             if(straa!='不限'){
             flagAtr=straa.split(',');
               for (i  in  flagAtr){
                   flagstr='<span class="flagcls">'+flagAtr[i]+'</span>';
                   $('#flagDiv').append(flagstr);
                };
              }
              else{$('#flagDiv').append('不限');}

             // document.getElementById("stopTask").style.background="#2894ff";
             // document.getElementById("pauseOrstart").style.background="red";
             // document.getElementById("jingxing").src="/static/img/onekey/popup/jingxingzhong.png";
             // $("#stopTask").attr("disabled", false);
             // $("#pauseOrstart").attr("disabled", false);
             // $("#remarkDiv").attr("disabled", false);

             if(taskstate=='1'){
                   $("#pauseOrstart").val('暂停');
                  }
             else if(taskstate=='2'){
                    $("#pauseOrstart").val('重启');
                   }
             else{
                  $("#stopTask").attr("disabled", true);
                  $("#pauseOrstart").attr("disabled", true);
                  document.getElementById("stopTask").style.background="#ADADAD";
                  document.getElementById("pauseOrstart").style.background="#ADADAD";
                  document.getElementById("jingxing").src="/static/img/onekey/popup/jingxingzhong.png";
                  $("#remarkDiv").attr("disabled", true);
             }
         },
         error: function(data){
              console.log("init()发生错误")
         }
     });
 }

 function startRequest(loadcnt,taskid,ifShow) {
     exectime=$('#exectime').val();
     sendtime=$('#sendtime').val();
     passtime=$('#passtime').val();
     if(taskid=="None"){return;};
     if(loadcnt==2 && sendtime=="None"){return;};
     //console.log("exectime:"+exectime)
     if(exectime==null||exectime=="")
      {querytime=gettime()}
     else
      {querytime=exectime}
    $.ajax({
        url: "/task_schedule/",
        type: 'POST',
        dataType : 'json',
        data: {'taskid': taskid,'querytime':querytime ,'loadcnt':loadcnt,'sendtime':sendtime,'passtime':passtime},
        success: function (data) {
            severcheck(data);
            $('#sendtime').val(data.sendtime);
            $('#passtime').val(data.passtime);
            $("#sendcnt").html("")
            $("#sendcnt").append(data.sendcnt)
            $("#passcnt").html("")
            $("#passcnt").append(data.passcnt)
            data=data.listmsg
            for (i in data){
                str='<div class="logR">'
                if(data[i].ctype=='1'){
                    str=str+'<div style="color: #626262" class="logS">'
                    str1='<div style="color: #626262" class="logB">'
                     }
                else{
                    str=str+'<div style="color:#E90433" class="logS">'
                    str1='<div style="color:#E90433" class="logB">'
                   }
                    str=str+"&lt;"+data[i].wx+"&gt;"+data[i].msg+"</div>"
                    str=str+str1+data[i].optime+"</div></div>"

                $("#chatresult").append(str)
            }
        },
        // error : function(data) {
        //     console.log("startRequest()发生错误")
        // }
    });
 }

 function gettime() {
     var date=new Date();
     var year=date.getFullYear(); //获取当前年份
     var mon=date.getMonth()+1; //获取当前月份
     var da=date.getDate(); //获取当前日
     var day=date.getDay(); //获取当前星期几
     var h=date.getHours(); //获取小时
     var m=date.getMinutes(); //获取分钟
     var s=date.getSeconds(); //获取秒
     if (da<10){da='0'+String(da)};
     if (m<10){m='0'+String(m)};
     if (h<10){h='0'+String(h)};
     if (mon<10){mon='0'+String(mon)};
     if (s<10){s='0'+String(s)};
     curtime=String(year)+String(mon)+String(da)+String(h)+String(m)+String(s);
     return curtime
 }

function sleep(n) {
        var start = new Date().getTime();
        //  console.log('休眠前：' + start);
        while (true) {
            if (new Date().getTime() - start > n) {
                break;
            }
        }   // console.log('休眠后：' + new Date().getTime());
      }

function change_task(int) {
     var index = layer.load(2, {shade: [0.1,'#798187']});
  taskstate=$("#pauseOrstart").val();
  taskid=$("#taskId").val();
  remark=$("#remarkDiv").val();
  task_state='1'
  if (int==1){
      task_state='3';}
  else if(taskstate=='暂停'){
      task_state='2';
  }
  else if(taskstate=='重启'){
      task_state='1';
  }
  else{return}

  $.ajax({
    url: "/change_task/",
    type: 'POST',
    data: {'taskid': taskid,'task_state':task_state},
    success: function (data) {
          severcheck(data);
          data = JSON.parse(data);
          if(data) {
              layer.close(index);
              if (task_state == '3') {
                  alert("已终止任务！");
                  document.getElementById("jingxing").src = "/static/img/onekey/popup/icon_stop.png";
                  $("#stopTask").attr("disabled", true);
                  document.getElementById("stopTask").style.background = "#ADADAD";
                  $("#pauseOrstart").attr("disabled", true);
                  document.getElementById("pauseOrstart").style.background = "#ADADAD";
                  window.location.reload()

              } else if (task_state == '2') {
                  alert("暂停任务成功！");
                  document.getElementById("jingxing").src = "/static/img/onekey/popup/icon_suspend.png";
                  $("#pauseOrstart").val('重启');
                  window.location.reload()
              } else if (task_state == '1') {
                  alert("已重新启动任务！");
                  document.getElementById("jingxing").src = "/static/img/onekey/popup/jingxingzhong.png";
                  $("#pauseOrstart").val('暂停');
                  window.location.reload()
              }
          }
    },
    error : function(data) {
        layer.close(index);
        alert("变更任务状态发生错误,请重试！")
        console.log("change_task()发生错误")
    }
});

}

//关闭按钮
function offViewModal(){
     viewmodal = document.getElementById('viewmodal');
     viewmodal.style.display = "none";

     //$("#frameAdd").attr("src", "javascript:void(0)");
     $('#taskId').val("");
     taskID="None";
    }

//展示弹出框
function showViewModal_before(taskid){

    modalinit(taskid);
    viewmodal = document.getElementById('viewmodal');
    layer.close(ii);
    viewmodal.style.display = "block";
}

function  showViewModal(taskid,task_state){
    var taskID=taskid;
    modalinit(taskid);
    startRequest(1,taskid,task_state, 1);
    // startRequest(1,taskid);
    viewmodal = document.getElementById('viewmodal');
    if(task_state=='3'){
        document.getElementById("jingxing").src="/static/img/onekey/popup/icon_stop.png";
    }else if(task_state=='4'){
        document.getElementById("jingxing").src="/static/img/onekey/popup/icon_finish.png";
    }
    viewmodal.style.display = "block";
    taskReady(taskid,task_state);
     }
//先判断任务是否已经下发完成
function taskReady(taskID,task_state) {
    var taskid=taskID;
    $("#stopTask").attr("disabled", true);
      document.getElementById("stopTask").style.background="#ADADAD";
      $("#pauseOrstart").attr("disabled", true);
      document.getElementById("pauseOrstart").style.background="#ADADAD";
      if(task_state=='1'||task_state=='2'){
            $.ajax({
         type: "POST",
         url: "/taskReady/",
         data: {'taskid':taskid},
         success: function(data) {
            severcheck(data);
            data = JSON.parse(data);
            if(data.msg=='succeess'){
                if(task_state=='2'){
                    document.getElementById("jingxing").src="/static/img/onekey/popup/icon_suspend.png";
                }
                else {
                    document.getElementById("jingxing").src = "/static/img/onekey/popup/jingxingzhong.png";
                }
                document.getElementById("pauseOrstart").style.background="red";
                document.getElementById("stopTask").style.background="#2894ff";
                $("#stopTask").attr("disabled", false);
                $("#pauseOrstart").attr("disabled", false);
            }else{
                document.getElementById("jingxing").src="/static/img/onekey/popup/icon_putout.png";
                console.log('数据还未下发好')}
            taskOnline(taskid,task_state);
         },
         error: function(data){
              console.log("init()发生错误")
         }
    });
      }
}

//判断微信是否在线
function taskOnline(taskID,task_state) {
    if(task_state=='1'){
        $.ajax({
            type: "POST",
            url: "/wx_online/",
            // async: false,
            data: {'task_id':taskID},
            success: function(data) {
                severcheck(data);
                data = JSON.parse(data);
                if(data.status == 'offline'){
                    document.getElementById("jingxing").src="/static/img/onekey/popup/icon_offline.png";
                }
            },
            error: function(data){
                console.log("init()发生错误")
            }
        });
    }
}