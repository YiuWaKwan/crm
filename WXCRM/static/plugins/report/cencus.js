window.onload = function () {
              /**
     * 日期格式化方法
     * @param format
     * @returns {*}
     */
         Date.prototype.format = function (format) {
        var o = {
            "M+": this.getMonth() + 1, //month
            "d+": this.getDate(), //day
            "h+": this.getHours(), //hour
            "m+": this.getMinutes(), //minute
            "s+": this.getSeconds(), //second
            "q+": Math.floor((this.getMonth() + 3) / 3), //quarter
            "S": this.getMilliseconds() //millisecond
        }

        if (/(y+)/.test(format)) {
            format = format.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
        }

        for (var k in o) {
            if (new RegExp("(" + k + ")").test(format)) {
                format = format.replace(RegExp.$1, RegExp.$1.length == 1 ? o[k] : ("00" + o[k]).substr(("" + o[k]).length));
            }
        }
        return format;
    };

    start_time= new Date(new Date().setDate(new Date().getDate()-1)).format('yyyyMMdd');
    end_time=start_time;
        //执行一个laydate实例
    laydate.render({
        elem: '#start_time',//指定元素
        value:new Date(new Date().setDate(new Date().getDate()-1)),
        done:function (value) {
            start_time=$('#start_time').val().replace(/-/g,'');
        }
    });
    //执行一个laydate实例
    laydate.render({
        elem: '#end_time',//指定元素
        value: new Date(new Date().setDate(new Date().getDate()-1)),
        done:function (value) {
            start_time=$('#start_time').val().replace(/-/g,'');
            end_time = value.replace(/-/g,'');
            if(parseInt(start_time)>parseInt(end_time)){
                $('#end_time').val('');
                alert('时间段选择错误，请重新选择')
            }
        }
    });
    getWxId();
    data_sum();
    group_day_change();
    group_spread();
    get_group_num();

    $('#refresh').click(function () {
        data_sum();
        group_day_change();
        group_spread();
    })

    function data_sum() {
    $.ajax({
        type: "POST",
        url: "../get_data_sum/",
        data: {'group_list':selected_id_list_str,'wx_id':wx_id,'start':start_time,'end':end_time},
        success: function (data) {
                severcheck(data);
                data = parseJson(data);
                if (data!='') {
                    $('#group_num').html(data[0]['group_num']);
                    $('#active_num').html(data[0]['active_num']);
                    $('#total_num').html(data[0]['total_num']);
                    $('#reply_num').html(data[0]['reply_num']);
                    $('#reply_avg_time').html(data[0]['consult_avg_num']);
                    $('#active_percent').html(data[0]['active_percent']);
                }
             },
        error: function (e) {
            alert("未知错误，请联系系统管理员。");
        }
    });
}
function getWxId() {
            $.ajax({
                    type: "POST",
                    url: "../getWxId/",
                    data: {},
                    success: function (data) {
                        severcheck(data);
                        data = parseJson(data);
                        var opt = [{label:"全部",value:0}];
                        $.each(data.data, function (key,wx_info) {
                            opt.push({label:wx_info.wx_name ? wx_info.wx_name+'('+wx_info.wx_login_id+')' : wx_info.wx_login_id,value:wx_info.wx_id})
                        });
                        var mySelect= $("#wx_id_query").jqSelect({
                          mult:true,//true为多选,false为单选
                          option:opt,
                          onChange:function(res){//选择框值变化返回结果
                                var index = res.indexOf("0");
                                if (index > -1 ) {
                                    if(index<1) {
                                        res.splice(index, 1);
                                    }
                                    else {
                                        res=[];
                                        mySelect.setResult(["0"]);
                                        wx_id = '';
                                        $('#select_num').html('微信');
                                    }
                                }
                                if(res.length==0) {
                                    mySelect.setResult(["0"]);
                                    wx_id = '';
                                }else {
                                    mySelect.setResult([]);
                                    mySelect.setResult(res);
                                    wx_id = res.join(",");
                                    $('#select_num').html('微信(' + res.length + ')');
                                 }
                                get_group_num();
                          }
                      });
                      mySelect.setResult(["0"]);
                    }
                }
            );
        }
function get_group_num() {
    $.ajax({
        type: "POST",
        url: "../group_num/",
        data: {'wx_id': wx_id},
        success: function (data) {
            severcheck(data);
            data = parseJson(data);
            $('#selected_num').html('(已选择'+data[0]['group_num']+'个群)')
        }, error: function (e) {
            alert("未知错误，请联系系统管理员。");
        }
    });
}
function group_day_change() {
        $.ajax({
            type: "POST",
            url: "../get_group_change/",
            data: {'group_list': selected_id_list_str, 'wx_id': wx_id, 'start': start_time, 'end': end_time},
            success: function (data) {
                severcheck(data);
                data = parseJson(data);
                if(data!='') {
                    var xdata = [];
                    var ydata1 = [];
                    var ydata2 = [];
                    var ydata3 = [];
                    var ydata4 = [];
                    for (x in data) {
                        if(!data.hasOwnProperty(x)){
                            continue;
                        }
                        xdata.push(data[x]['cur_date']);
                        ydata1.push(data[x]['reply_num']);
                        ydata2.push(data[x]['total_num']);
                        ydata3.push(data[x]['active_people']);
                        ydata4.push(data[x]['service_people']);
                    }

                    var myChart = echarts.init(document.getElementById('group_change'));
                    var option = {
                        toolbox: {
                            feature: {
                                dataView: {},
                            }
                        },
                        tooltip: {
                            trigger: 'axis',
                            axisPointer: {
                                type: 'cross',
                                label: {
                                    backgroundColor: '#6a7985'
                                }
                            }
                        },
                        legend: {
                            data: ['回复总数', '信息总数', '活跃人数', '服务人次']

                        },
                        // toolbox: {
                        //     feature: {
                        //         dataView: {},
                        //         magicType: {type: ['line', 'bar', 'stack', 'tiled']},
                        //         restore: {},
                        //         saveAsImage: {},
                        //     }
                        // },
                        grid: {
                            left: '3%',
                            right: '4%',
                            bottom: '5%',
                            containLabel: true
                        },
                        xAxis: [
                            {
                                type: 'category',
                                boundaryGap: false,
                                data: xdata,
                                name: '日期'
                            }
                        ],
                        yAxis: [
                            {
                                type: 'value',
                                name:'(条)'
                            },
                            {
                                type: 'value',
                                name:'(人)'
                            }
                        ],
                        series: [
                            {
                                name: '回复总数',
                                type: 'line',
                                smooth: true,
                                lineStyle: {
                                    normal: {
                                        color: '#EA34CA'
                                    }
                                },
                                data: ydata1
                            },
                            {
                                name: '信息总数',
                                type: 'line',
                                smooth: true,
                                lineStyle: {
                                    normal: {
                                        color: '#A24EF8'
                                    }
                                },
                                data: ydata2
                            },
                            {
                                name: '活跃人数',
                                type: 'line',
                                smooth: true,
                                yAxisIndex: 1,
                                lineStyle: {
                                    normal: {
                                        color: '#67E9B7',
                                    }
                                },
                                data: ydata3
                            },
                            {
                                name: '服务人次',
                                type: 'line',
                                smooth: true,
                                yAxisIndex: 1,
                                lineStyle: {
                                    normal: {
                                        color: '#F75F46',
                                    }
                                },
                                data: ydata4
                            },
                        ]
                    };
                    myChart.setOption(option, true);
                }
        },
        error: function(e) {
            alert("未知错误，请联系系统管理员。");
        }
    });

 }
function group_spread() {
    $.ajax({
        type: "POST",
        url: "../get_group_spread/",
        data: {'group_list':selected_id_list_str,'wx_id':wx_id,'start':start_time,'end':end_time},
        success: function (data) {
                severcheck(data);
                data = parseJson(data);
                if (data!='') {
                    scaleData = [
                        {
                            'name': '文字',
                            'value': data[0]['words_msg_num']
                        },
                        {
                            'name': '图片',
                            'value': data[0]['picture_msg_num']
                        },
                        {
                            'name': '附件',
                            'value': data[0]['file_msg_num']
                        },
                        {
                            'name': '系统消息',
                            'value': data[0]['sys_msg_num']
                        },
                        {
                            'name': '语音',
                            'value': data[0]['voice_msg_num']
                        },
                        {
                            'name': '视频',
                            'value': data[0]['video_msg_num']
                        },
                        {
                            'name': '链接',
                            'value': data[0]['link_msg_num']
                        },
                        {
                            'name': '其它消息',
                            'value': data[0]['other_msg_num']
                        }
                    ];
                    var myChart = echarts.init(document.getElementById('group_msg_spread'));
                    var option = {
                        toolbox: {
                            feature: {
                                dataView: {},
                            }
                        },
                        color:['#87E7FF','#6ABDFD','#879DFF','#9A87FF','#DB88FF','#2ED3FC','#BFC2FB','#67E9B7'],
                        tooltip: {
                            trigger: 'item',
                            formatter: "{a}{b} : {c} ({d}%)"
                        },
                        legend: {
                            type: 'scroll',
                            orient: 'vertical',
                            right: 50,
                            top: 40,
                            bottom: 20,
                            // data: data.legendData,
                            //
                            // selected: data.selected
                            formatter: function (name) {
                                  var total = 0;
                                  var tarValue;
                                  // for (var i = 0, l = data.length; i < l; i++) {
                                  //     total += data[i].value;
                                  //     if (data[i].name == name) {
                                  //         tarValue = data[i].value;
                                  //     }
                                  // }
                                  for (var x in scaleData){
                                        if(!scaleData.hasOwnProperty(x)){
                                                            continue;
                                                        }
                                        total= total+parseInt(scaleData[x].value);
                                        if(scaleData[x].name == name) {
                                            tarValue = parseInt(scaleData[x].value);
                                        }
                                    }
                                  var p = (tarValue / total * 100).toFixed(2);
                                  return name + ' ' + tarValue+'条' + '(' + p + '%)';
                            }
                        },
                        series: [
                            {
                                name: '',
                                type: 'pie',
                                radius: ['50%','70%'],
                                center: ['40%', '55%'],
                                data: scaleData,
                                itemStyle: {
                                    emphasis: {
                                        shadowBlur: 10,
                                        shadowOffsetX: 0,
                                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                                    }
                                }
                            }
                        ]
                    };
                    myChart.setOption(option, true);
                }
             },
        error: function (e) {
            alert("未知错误，请联系系统管理员。");
        }
    });
};
};





function loadData(jsonData){

    var letter_html = '';
    // var letter_list = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'];
    var letter_list = [];
    var temp_html="";
    var group_info_list_temp={}
    for (var key in jsonData){
        letter_list.push(key);
        temp_html+= "<div >" +
                    "<div style=\"padding: 0 10px;\" id='letter_"+key+"'>\n" +
                    "    <span style=\"font-size: 24px\">"+key+"</span>\n" +
                    "    <div style=\"float: right;display:flex;\" >\n" +
                    "        <span style=\"margin: auto;font-size: 14px;opacity:0.8;\">全选</span>\n" +
                    "        <input type=\"checkbox\" style=\"margin: auto;width: 20px;\" onclick='select_all_letter(\""+key+"\")'>\n" +
                    "    </div>\n" +
                    "</div>"
        var group_name_list=jsonData[key]
        for (var name_key in group_name_list){
            if(group_info_list){
                if(group_info_list.hasOwnProperty(name_key)){
                    group_info_list_temp[name_key]=group_info_list[name_key]
                }else{
                    group_info_list_temp[name_key]={'group_name':group_name_list[name_key],'selected':0,'letter':key}
                }
                if(group_info_list_temp[name_key].selected){
                    temp_html+="<span class='group_list_item group_list_item_selected' onclick='click_group_name(this)' value='"+name_key+"'>"+group_name_list[name_key]+"</span>"
                }else{
                    temp_html+="<span class='group_list_item' onclick='click_group_name(this)'  value='"+name_key+"'>"+group_name_list[name_key]+"</span>"
                }
            }else{
                group_info_list[name_key]={'group_name':group_name_list[name_key],'selected':0,'letter':key}
                temp_html+="<span class='group_list_item group_list_item_selected' onclick='click_group_name(this)'  value='"+name_key+"'>"+group_name_list[name_key]+"</span>"
            }
        }
        temp_html+="</div>"
    }
    if(group_info_list){
            group_info_list=group_info_list_temp
    }
    for(x in letter_list){
        if(!letter_list.hasOwnProperty(x)){
                            continue;
                        }
        letter_html+='<li class="letter_btn_list"><a class="letter_btn" href="#letter_'+letter_list[x]+'">'+letter_list[x]+'</a></li>'
    }
    $('#letter').html(letter_html);
    $("#group_list_box").html(temp_html)
    temp_html=""
    for(var group_item in group_info_list){
       if(group_info_list[group_item].selected===1){
           temp_html+="<span class=\"selected_group_name\" value=\""+group_item+"\">"+group_info_list[group_item].group_name+"<span class=\"delete_btn hide_btn\"></span></span>"
       }
    }
    $("#selected_group_box").html(temp_html)
    $(".selected_group_name").bind('mouseover',function(){
        $(this).find(".delete_btn").removeClass("hide_btn").addClass("show_btn")
    })
    $(".selected_group_name").bind('mouseout',function(){
        $(this).find(".delete_btn").removeClass("show_btn").addClass("hide_btn")
    })
    $(".letter_btn").bind('click',function(){
            $(".letter_btn").each(function(index,item){
              $(item).css("color","#666666").css("background-color","#FFFFFF")
            })
            $(this).css("color","#0084FF").css("background-color","#ECF7FD")
        })
}
function delete_group(obj){
    var this_obj=$(obj).parent()
    var group_id=this_obj.attr('value')
    group_info_list[group_id].selected=0
    temp_html=""
    for(var group_item in group_info_list){
       if(group_info_list[group_item].selected===1){
           temp_html+="<span class=\"selected_group_name\" value=\""+group_item+"\">"+group_info_list[group_item].group_name+"<span class=\"delete_btn hide_btn\" onclick='delete_group(this)'></span></span>"
       }
    }
    $("#selected_group_box").html(temp_html)
        $(".selected_group_name").bind('mouseover',function(){
        $(this).find(".delete_btn").removeClass("hide_btn").addClass("show_btn")
    })
    $(".selected_group_name").bind('mouseout',function(){
        $(this).find(".delete_btn").removeClass("show_btn").addClass("hide_btn")
    })
    $(".group_list_item").each(function(index,obj){
        if($(obj).attr("value")===group_id){
            $(obj).removeClass("group_list_item_selected")
        }
    })
}
function click_group_name(obj){
    var this_obj=$(obj)
    if(this_obj.hasClass('group_list_item_selected')){
        this_obj.removeClass("group_list_item_selected")
        group_info_list[this_obj.attr('value')].selected=0
    }else{
        this_obj.addClass("group_list_item_selected")
        var temp_item=group_info_list[this_obj.attr('value')]
        delete group_info_list[this_obj.attr('value')]
        group_info_list[this_obj.attr('value')]=temp_item
        group_info_list[this_obj.attr('value')].selected=1
    }
    temp_html=""
    for(var group_item in group_info_list){
       if(group_info_list[group_item].selected===1){
           temp_html+="<span class=\"selected_group_name\" value=\""+group_item+"\">"+group_info_list[group_item].group_name+"<span class=\"delete_btn hide_btn\" onclick='delete_group(this)'></span></span>"
       }
    }
    $("#selected_group_box").html(temp_html)
    $(".selected_group_name").bind('mouseover',function(){
        $(this).find(".delete_btn").removeClass("hide_btn").addClass("show_btn")
    })
    $(".selected_group_name").bind('mouseout',function(){
        $(this).find(".delete_btn").removeClass("show_btn").addClass("hide_btn")
    })
}
function select_all(){
    if(select_all_btn){
        temp_html=""
        for(var group_item in group_info_list){
            group_info_list[group_item].selected=1
               temp_html+="<span class=\"selected_group_name\" value=\""+group_item+"\">"+group_info_list[group_item].group_name+"<span class=\"delete_btn hide_btn\" onclick='delete_group(this)'></span></span>"
        }
        $("#selected_group_box").html(temp_html)
        $(".selected_group_name").bind('mouseover',function(){
            $(this).find(".delete_btn").removeClass("hide_btn").addClass("show_btn")
        })
        $(".selected_group_name").bind('mouseout',function(){
            $(this).find(".delete_btn").removeClass("show_btn").addClass("hide_btn")
        })
        $(".group_list_item").each(function(index,obj){
                $(obj).removeClass("group_list_item_selected")
                $(obj).addClass("group_list_item_selected")
        })
        select_all_btn=0
    }else{
        for(var group_item in group_info_list){
            group_info_list[group_item].selected=0
        }
        $("#selected_group_box").html('')
        $(".group_list_item").each(function(index,obj){
                $(obj).removeClass("group_list_item_selected")
        })
        select_all_btn=1
    }
}
function select_all_letter(letter_str) {
    if (select_all_letter_btn.hasOwnProperty(letter_str) && select_all_letter_btn[letter_str] === 1) {//全部取消选中
        select_all_letter_btn[letter_str] = 0
        temp_html = ""
        for (var group_item in group_info_list) {
            if (group_info_list[group_item].letter === letter_str) {
                group_info_list[group_item].selected = 0
            } else if (group_info_list[group_item].selected === 1) {
                temp_html += "<span class=\"selected_group_name\" value=\"" + group_item + "\">" + group_info_list[group_item].group_name + "<span class=\"delete_btn hide_btn\" onclick='delete_group(this)'></span></span>"
            }
        }
        $("#selected_group_box").html(temp_html)
        $(".selected_group_name").bind('mouseover', function () {
            $(this).find(".delete_btn").removeClass("hide_btn").addClass("show_btn")
        })
        $(".selected_group_name").bind('mouseout', function () {
            $(this).find(".delete_btn").removeClass("show_btn").addClass("hide_btn")
        })
        $(".group_list_item").each(function (index, obj) {
            if (group_info_list[$(obj).attr("value")].selected === 0) {
                $(obj).removeClass("group_list_item_selected")
            }
        })
    } else {
        select_all_letter_btn[letter_str] = 1
        temp_html = ""
        for (var group_item in group_info_list) {
            if (group_info_list[group_item].letter === letter_str || group_info_list[group_item].selected === 1) {
                group_info_list[group_item].selected = 1
                temp_html += "<span class=\"selected_group_name\" value=\"" + group_item + "\">" + group_info_list[group_item].group_name + "<span class=\"delete_btn hide_btn\" onclick='delete_group(this)'></span></span>"
            }
        }
        $("#selected_group_box").html(temp_html)
        $(".selected_group_name").bind('mouseover', function () {
            $(this).find(".delete_btn").removeClass("hide_btn").addClass("show_btn")
        })
        $(".selected_group_name").bind('mouseout', function () {
            $(this).find(".delete_btn").removeClass("show_btn").addClass("hide_btn")
        })
        $(".group_list_item").each(function (index, obj) {
            if (group_info_list[$(obj).attr("value")].selected === 1) {
                $(obj).removeClass("group_list_item_selected")
                $(obj).addClass("group_list_item_selected")
            }
        })
    }
}
