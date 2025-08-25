/**
 * Created by xiaox on 2018/8/9.
 */
    $(document).ready(function(){
        init();
        startRequest(1);
        sleep(500);
        setInterval("startRequest(2)", 2000); //0.5s
     });

     function init() {
         var taskid=$("#taskid").val();
         //consle.log(String(taskid));
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
                 //$('#flagDiv').append(data.flag);
                 $('#addAddrDiv').append(data.addAddr);
                 $('#addTimeDiv').append(data.addTime);
                 $('#greetDiv').append(data.greet);
                 $('#remarkDiv').append(data.remark);
                 $('#taskcnt').append(data.taskcnt);
                 $('#exectime').val(data.exectime);
                 taskstate=data.taskstate;

                 straa=data.flag
                 console.log('straa:'+straa)
                 if(straa!='不限'){
                 flagAtr=straa.split(',');
                   for (i  in  flagAtr){
                        //console.log(i);
                       flagstr='<span class="flagcls">'+flagAtr[i]+'</span>';
                       $('#flagDiv').append(flagstr);
                    };
                  }
                  else{$('#flagDiv').append('不限');}

                 if(taskstate=='1'){$("#pauseOrstart").val('暂停');}
                 else if(taskstate=='2'){$("#pauseOrstart").val('继续');}
                 else{
                      $("#stopTask").attr("disabled", true);
                      $("#pauseOrstart").attr("disabled", true);
                      document.getElementById("stopTask").style.background="#ADADAD";
                      document.getElementById("pauseOrstart").style.background="#ADADAD";
                 }

             },
             error: function(data){
                  console.log("init()发生错误")
             }
         });
     }

     function startRequest(loadcnt) {
         exectime=$('#exectime').val();
         sendtime=$('#sendtime').val();
         passtime=$('#passtime').val();
         //console.log("exectime:"+exectime)
         if(exectime=="")
         {querytime=gettime()}
         else
          {querytime=exectime}

         if (loadcnt!=1) {
             querytime = gettime()
         }
         //console.log("querytime :"+querytime);
         var taskid=$("#taskid").val();
        $.ajax({
            url: "/task_schedule/",
            type: 'POST',
	        dataType : 'json',
            data: {'taskid': taskid,'querytime':querytime ,'loadcnt':loadcnt,'sendtime':sendtime,'passtime':passtime},
            success: function (data) {
                $('#sendtime').val(data.sendtime);
                $('#passtime').val(data.passtime);
                $("#sendcnt").html("")
                $("#sendcnt").append(data.sendcnt)
                $("#passcnt").html("")
                $("#passcnt").append(data.passcnt)
                data=data.listmsg
                for (i in data){
                    console.log(data[i].ctype);
                    str=""
                    if(data[i].ctype=='1'){str='<p style="color:red">'}
                    else{str='<p style="color:blue">'}
                    str=str+data[i].optime+"&nbsp&nbsp&nbsp&nbsp"+"&lt;"+ data[i].wx+"&gt;"+data[i].msg+"</p>"
                    //console.log(i);
                    $("#chatresult").append(str)
                }

               // $("#chatresult").append(str)
            },
	        error : function(data) {
		        //alert("发生错误：" );
                console.log("startRequest()发生错误")
	        }
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
          taskstate=$("#pauseOrstart").val();
          taskid=$("#taskid").val();
          task_state='1'
          if (int==1){
              task_state='3';}
          else if(taskstate=='暂停'){
              task_state='2';
          }
          else if(taskstate=='继续'){
              task_state='1';
          }
          else{return}

          $.ajax({
            url: "/change_task/",
            type: 'POST',
	        dataType : 'json',
            data: {'taskid': taskid,'task_state':task_state },
            success: function (data) {

                  if (task_state=='3'){
                      alert("已终止任务！");
                      $("#stopTask").attr("disabled", true);
                      document.getElementById("stopTask").style.background="#ADADAD";
                      $("#pauseOrstart").attr("disabled", true);
                      document.getElementById("pauseOrstart").style.background="#ADADAD";


                  }
                   else if(task_state=='2'){
                       alert("暂停任务成功！");
                       $("#pauseOrstart").val('继续');
                  }
                   else if(task_state=='1'){
                       alert("已重新启动任务！");
                       $("#pauseOrstart").val('暂停');
                  }
            },
	        error : function(data) {
		        alert("变更任务状态发生错误！")
                console.log("change_task()发生错误")
	        }
        });


      }

