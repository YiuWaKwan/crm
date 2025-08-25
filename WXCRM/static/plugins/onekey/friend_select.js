window.onload = function () {
    var ii = layer.load();
    var OK =false;
    var search_num = 0;
    var input_ok = true;//执行规模输入正确
    //获取城市列表
    $.ajax({
        type: 'get',
        url: '../citydata/',
        data: {},
        success: function (jsonvalue) {
            severcheck(jsonvalue);
            jsonvalue = parseJson(jsonvalue);
            $('#citylist').cxSelect({
                selects: ['province', 'city'], // 数组，请注意顺序
                data: jsonvalue,
                required:true,
                jsonName: "name",
                //jsonValue: "value",
                jsonSub: 'city_name'
            });
            layer.close(ii);
        },
        // error: function (e) {
        //     alert("未知错误，请联系系统管理员。");
        // }
    });
    $(document).on('click', '.default', function () {
        $(this).toggleClass('on')
        if ($(this).parent().find('.default.on').length > 0) {
            $(this).parent().find('.all').removeClass('on')
            $(this).parent().parent().find('.all').removeClass('on')
        } else {
            $(this).parent().find('.all').addClass('on')
        }

    });

    $(document).on('click', '.all', function () {

        if ($(this).hasClass('on')) {

        } else {
            $(this).parent().find('.on').removeClass('on');
            $(this).toggleClass('on')
        }

    });
    var btn = document.getElementById('showModel');
    // var close = document.getElementsByClassName('close')[0];
    var cancel = document.getElementById('cancel');
    var modal = document.getElementById('modal');
    btn.addEventListener('click', function () {
        data = [];
        $('.cation-list').each(function (index, item) {

            $.each($('dt', item), function () {
                data1 = {}
                data2 = [];
                if ($(this).attr('data') == '0' || $(this).attr('data') == '-1') {
                }
                else {
                    data1 = { 'id': $(this).attr('data'), 'child': '' };
                    $(item).find('dd .on').each(function (ind, ite) {
                        if ($(ite).attr("data") != "") {
                            data3 = { 'childid': $(ite).attr("data") };
                            data2.push(data3)
                        }
                        data1.child = data2;
                    });
                    data.push(data1)
                }
            });

        });
        province = $('#province option:selected').text();
        city = $('#city option:selected').text();
        // preage = $('#preage').val();
        // postage = $('#postage').val();
        // if(preage==''){
        //     preage=$('#preage').attr('placeholder')
        // }
        // if(postage==''){
        //     postage=$('#preage').attr('placeholder')
        // }
        //插入条件并查询数量
        modal.style.display = "block";
        $.ajax({
            type: 'post',
            url: '../get_weixin_num/',
            data: { 'province': province, 'city': city, 'data': JSON.stringify(data) },
            cache: 'false',
            success: function (result) {
                severcheck(result);
                result = parseJson(result);
                search_num = result[0]['num'];
                if(search_num>=1000){
                    html = '<span style="display: inline-block;text-align: center;"><img src="/static/img/onekey/wancheng.png" alt="" style="float:left;" ><p style="float: left;font-size: 16px;line-height: 67px;">根据您的条件筛选&nbsp&nbsp<strong  style="font-size: 25px;color: red;">1000+</strong>&nbsp&nbsp个好友</p ></span>';
                }else {
                    $('#add_num').attr("placeholder",search_num)
                    html = '<span style="display: inline-block;text-align: center;"><img src="/static/img/onekey/wancheng.png" alt="" style="float:left;" ><p style="float: left;font-size: 16px;line-height: 67px;">根据您的条件筛选&nbsp&nbsp<strong  style="font-size: 25px;color: red;">' + search_num + '</strong>&nbsp&nbsp个好友</p ></span>';
                }
                $('#search_num').html(html);
                OK =true;
                if (search_num==0){
                    modal.style.display = "none" ;
                    var modal1 = document.getElementById('modal1');
                    modal1.style.display = "block" ;
                }
            },
            // error: function (e) {
            //     alert("未知错误，请联系系统管理员。");
            // }
        });
    });
    // close.addEventListener('click', function () {
    //     modal.style.display = "none";
    //     $('#search_num').html('<img src="/static/img/onekey/loading.gif" style="margin-left: 150px;">');
    //     $('#tip').html('');
    //         $("#add_num")[0].style.border = "1px solid #e7e5e5";
    //     $('#add_num').val('');
    //     $('#add_num').attr("placeholder",1000)
    //
    // });
    cancel.addEventListener('click', function () {
        modal.style.display = "none" ;
        $('#search_num').html('<img src="/static/img/onekey/loading.gif" style="text-align: center">');
        $('#tip').html('');
        $("#add_num")[0].style.border = "1px solid #e7e5e5";
        $('#add_num').val('');
        $('#add_num').attr("placeholder",1000)
    });
    //执行规模监控
    $("#add_num").bind("input propertychange",function(){
        $("#add_num")[0].style.border = "1px solid #e7e5e5";
        $('#tip').html('');
        input_ok =true;
        var filter_fact = $(this).val();
        if(parseInt(filter_fact)>parseInt(search_num)  ){
            $('#tip').html('');
            $("#add_num")[0].style.border = "1px solid red";
            html ='<dl style="margin-top: 0px;margin-left:-65px;height: 20px;display: inline-block;">\n' +
                '                        <img src="/static/img/onekey/tip.png" style="float: left;width: 19px;">\n' +
                '                        <p style="color: red;float: left">不可以大于查询值</p>\n' +
                '                    </dl>';
            $('#tip').html(html);
            input_ok=false;
        }else if(parseInt(filter_fact)>1000){
            $('#tip').html('');
            $("#add_num")[0].style.border = "1px solid red";
            html ='<dl style="margin-top: 0px;margin-left:-65px;height: 20px;display: inline-block;">\n' +
                '                        <img src="/static/img/onekey/tip.png" style="float: left;width: 19px;">\n' +
                '                        <p style="color: red;float: left">不可以大于1000</p>\n' +
                '                    </dl>';
            $('#tip').html(html);
            input_ok=false;
        }
        // else {
        //     if (parseInt(filter_fact) > 25) {
        //         $("#add_num")[0].style.border = "1px solid #89b6fd";
        //         html = '<dl style="margin-top: 0px;margin-left:-84px;height: 20px;display: inline-block;">\n' +
        //             '                        <p style="color: #72a8fd;float: left">预计' + Math.ceil(parseInt(filter_fact) / 25) + '天完成</p>\n' +
        //             '                    </dl>';
        //         $('#tip').html(html);
        //     }
        // }
    });
    $('#clo').click(function () {
        var modal1 = document.getElementById('modal1');
        modal1.style.display = 'none';
    });
    //好友筛选结果确认
    $('#sure').click(function () {

            if (OK && input_ok) {
                var task_name = '';
                var add_num = '';
                if ($('#task_name').val() == '') {
                    task_name = $('#task_name').attr('placeholder')
                }
                else {
                    task_name = $('#task_name').val()
                }
                if ($('#add_num').val() == '') {
                    add_num = $('#add_num').attr('placeholder')
                }
                else {
                    add_num = $('#add_num').val()
                }
                $.ajax({
                    type: 'post',
                    url: '../put_task/',
                    data: {'task_name': task_name, 'add_num': add_num, 'tot_user': search_num},
                    dataType: 'json',
                    success: function (result) {
                        if (result = 'success') {
                            window.location.href = '/friend_add/';
                        } else {
                            alert('服务器错误')
                        }
                    },
                    // error: function (e) {
                    //     alert("未知错误，请联系系统管理员。");
                    // }
                });
            }
            else {
                alert('数据还未加载或输入错误')
            }
    });
    $('#back').click(function () {
        window.location.href= '../WXCRM/friend_onekey/';
    });

    $(document).on('click','#more',function () {
        var more = document.getElementById('more5');
        console.log($('#more').html())
        if($('#more').html()=='更多'){
            more.style.display = "block";
            $('#more').html('收起')
        }else{
            more.style.display = "none";
            $('#more').html('更多')
        }
    })
    //
    // $('#more').click(function(){
    //     var list = document.getElementById('childlist');
    //     var img = document.getElementById('more');
    //     if($('#more').attr("data")=='更多'){
    //
    //         list.style.display = "block";
    //         img.src = "../static/img/shouqi.png";
    //         $('#more').attr('data','收起')
    //     }else{
    //         list.style.display = "none";
    //         img.src = "../static/img/more.png";
    //         $('#more').attr('data','更多')
    //     }
    // });
    //刷新筛选条件
    $.ajax({
        type: 'get',
        url: '../get_list/',
        data: {},
        cache: 'false',
        success: function (result) {
            severcheck(result);
            result = JSON.parse(result);
            html = "";
            for (x in result) {
                if (result[x]['id'] == '4') {
                    html += "<dl class=\"cation-list\"><dt data='-1'>年龄</dt><dd><a href=\"javascript:;\" rel=\"\" name=\"price\" class=\"all on\">不限</a>" +
                        "<a><input id='preage' type=\"text\" name=\"\" placeholder=\"20\" style=\"width: 52px;border: 1px solid #CCC;padding: 3px;height:20px\">" +
                        "<em>-</em><input id='postage'  type=\"text\" name=\"\" placeholder=\"30\" style=\"width: 52px;border: 1px solid #CCC;padding: 3px;height:20px\">" +
                        "</a><a href=\"javascript:;\" rel=\"其它\" name=\"price\" class=\"default\">其它</a></dd></dl>"
                }
                html += "<dl class=\"cation-list\"><dt data='" + result[x]['id'] + "'>" + result[x]['name'] + "</dt><dd>";
                id = result[x]['id']
                data = result[x]['child'];
                len = data.length;
                n = 1;
                for (i in data) {
                    if (n <=7){
                        if (data[i]['FLAG_VALUE_VALUE'] == '0') {
                            html += "<a href='javascript:;' rel='' name='mode' class='all on' data='0'>不限</a>"
                        } else {
                            html += "<a href='javascript:;' rel='' name='mode' class='default' data='" + data[i]['FLAG_VALUE_VALUE'] + "'>" + data[i]['FLAG_VALUE_NAME'] + "</a>"
                        }
                    }
                    if(n==7){html +="<div id='more"+id+"' style='display:none;'>"}
                    if(n>7){
                         html += "<a href='javascript:;' rel='' name='mode' class='default' data='" + data[i]['FLAG_VALUE_VALUE'] + "'>" + data[i]['FLAG_VALUE_NAME'] + "</a>"
                    }
                    if(n==len && n>7){
                        html +="</div><a href='javascript:;' id='more' rel='' name='mode' style='padding-left: 17px;color: #dc3545;'>更多</a>"
                    }
                    n = n+1
                }
                html += "</dd></dl>";

            }
            $('#list').html(html);
        },
        // error: function (e) {
        //     alert("未知错误，请联系系统管理员。");
        // }
    });
}


//预览弹出框
 var g_postindex=0;
function  showViewModal() {
    viewmodal = document.getElementById('viewmodal');
    viewmodal.style.display = "block";

    tableLoadData(g_postindex);
     }

function offViewModal(){
     viewmodal = document.getElementById('viewmodal');
     viewmodal.style.display = "none";
     g_postindex=0;
    }

function  tableLoadData(postindex) {
    //获取请求参数
    data = [];
    $('.cation-list').each(function (index, item) {
            $.each($('dt', item), function () {
                data1 = {}
                data2 = [];
                if ($(this).attr('data') == '0' || $(this).attr('data') == '-1') {
                    console.log('你好')
                }
                else {
                    data1 = { 'id': $(this).attr('data'), 'child': '' };
                    $(item).find('dd .on').each(function (ind, ite) {
                        if ($(ite).attr("data") != "") {
                            data3 = { 'childid': $(ite).attr("data") };
                            data2.push(data3)
                        }
                        data1.child = data2;
                    });
                    data.push(data1)
                }
            });
        });
        console.log(data);
        province = $('#province option:selected').text();
        city = $('#city option:selected').text();
    //请求数据
    datalist=[];
    $.ajax({
    type: "POST",
    url: "../preview/",
    async: false,
    data: { 'province': province, 'city': city, 'data': JSON.stringify(data),'postindex':postindex },
    success: function(data) {
        severcheck(data);
        data = JSON.parse(data);
        datalist=data;
    },
    error : function(data) {
        console.log("获取预览数据出错！")
    }
    });

    // datalist =[ {"mobile":"139****9517",'province':'广东', 'city':'广州','hangye':'IT','job':'前端','sex':'男','age':'26','xiaofei':'高','flag':'音乐爱好者,帅哥'}];
     //加载数据
    console.log("datalist:"+datalist);
    if(datalist.length>0) {
        $(function () {
            grid = BCGrid.create("#table", {
                columns: [
                    {name: 'WX_CODE', display: '手机号', align: 'center'},
                    {name: 'PROVINCE_NAME', display: '省份', align: 'center'},
                    {name: 'CITY_NAME', display: '城市', align: 'center'},
                    {name: 'SEX', display: '性别', align: 'center'},
                    {name: 'AGE', display: '年龄', align: 'center'},
                    {name: 'HANGYE', display: '行业', align: 'center'},
                    {name: 'JOB', display: '职业', align: 'center'},
                    {name: 'FLAG', display: '标签', align: 'center'}
                ],
                dataSource: 'local',
                localData: datalist
            });
        });
    }
    else{
        $('#table').html("");
        $('#table').append('<p style="width: 100%;text-align: center">无符合条件的好友</p>');
         $("#batch").attr("disabled", true);
          document.getElementById("batch").style.background="#ADADAD";
      }

     }
     
function batchNext() {
     g_postindex=g_postindex+1;
     if(g_postindex<=20){tableLoadData(g_postindex);}
     else{alert("每次只能预览200条信息！");}
    }