jQuery(function(){
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
            console.log(start_time);
            end_time = value.replace(/-/g,'');
            if(parseInt(start_time)>parseInt(end_time)){
                $('#end_time').val('');
                alert('时间段选择错误，请重新选择')
            }
        }
    });
    getWxId();
    get_display();
    get_group_num();
     $('#refresh').click(function () {
        $('#table').bootstrapTable('refresh');
    })
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
    function get_display() {
         jQuery("#table").bootstrapTable({ // 对应table标签的id
            method: "post",
            dataType: "json",
            url: "../group_imdetail_report/", // 获取表格数据的url
            cache: false, // 设置为 false 禁用 AJAX 数据缓存， 默认为true
            striped: true,  //表格显示条纹，默认为false
            pagination: true, // 在表格底部显示分页组件，默认false
            pageList: [], // 设置页面可以显示的数据条数
            pageSize: 10, // 页面数据条数
            pageNumber: 1, // 首页页码
            //showRefresh:true,
            //search:true,
            showExport:true,
            exportDataType:'all',
            paginationLoop: true,
            sidePagination: 'server', // 设置为服务器端分页
             exportOptions:{
                      //ignoreColumn: [0,0],            //忽略某一列的索引
                      fileName: '入群成员明细报表',              //文件名称设置
                      worksheetName: 'Sheet1',          //表格工作区名称
                      tableName: '报表',
                      excelstyles: ['background-color', 'color', 'font-size', 'font-weight'],
                      //onMsoNumberFormat: DoOnMsoNumberFormat
                  },
             //showExport: true,                     //是否显示导出
            queryParams: function (params) { // 请求服务器数据时发送的参数，可以在这里添加额外的查询参数，返回false则终止请求

                return {
                    pageSize: params.limit, // 每页要显示的数据条数
                    offset: params.offset, // 每页显示数据的开始行号
                    start:start_time,
                    end:end_time,
                    wx_id:wx_id,
                    group_list:selected_id_list_str,
                    // sort: params.sort, // 要排序的字段
                    // sortOrder: params.order, // 排序规则
                }
            },
            // sortName: 'JOB_ID', // 要排序的字段
            // sortOrder: 'desc', // 排序规则
            columns: [

                {
                    field: 'in_group_time',
                    title: '入群时间',
                    align: 'center',
                    valign: 'middle',
                }, {
                    field: 'group_member_name',
                    title: '昵称',
                    align: 'center',
                    valign: 'middle'
                }, {
                    field: 'group_member_id',
                    title: '用户ID',
                    align: 'center',
                    valign: 'middle',
                }, {
                    field: 'group_name',
                    title: '微信群',
                    align: 'center',
                    valign: 'middle',
                }, {
                    field: 'wx_login_id',
                    title: '微信号',
                    align: 'center',
                    valign: 'middle',
                }
                , {
                    field: 'invite_name',
                    title: '邀请人',
                    align: 'center',
                    valign: 'middle',
                }
            ]

        });
     };
});
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