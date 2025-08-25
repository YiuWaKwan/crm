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

    var start= new Date(new Date().setDate(new Date().getDate()-1)).format('yyyyMMdd');
    var end=new Date().format('yyyyMMdd');
        //执行一个laydate实例
    laydate.render({
        elem: '#start',//指定元素
        value:new Date(new Date().setDate(new Date().getDate()-1)),
        done:function (value) {
            start=$('#start').val().replace(/-/g,'');
        }
    });
    //执行一个laydate实例
    laydate.render({
        elem: '#end',//指定元素
        value: new Date(),
        done:function (value) {
            start=$('#start').val().replace(/-/g,'');
            end = value.replace(/-/g,'');
            if(parseInt(start)>parseInt(end)){
                $('#end').val('');
                alert('时间段选择错误，请重新选择')
            }
        }
    });
    get_display();
    function get_display() {
         jQuery("#table").bootstrapTable({ // 对应table标签的id
            method: "post",
            dataType: "json",
            url: "../get_chatReport/", // 获取表格数据的url
            cache: false, // 设置为 false 禁用 AJAX 数据缓存， 默认为true
            striped: true,  //表格显示条纹，默认为false
            pagination: true, // 在表格底部显示分页组件，默认false
            pageList: [5,10,20,30], // 设置页面可以显示的数据条数
            pageSize: 10, // 页面数据条数
            pageNumber: 1, // 首页页码
            //showRefresh:true,
            //search:true,
            paginationLoop: true,
            sidePagination: 'server', // 设置为服务器端分页
             //showExport: true,                     //是否显示导出
            queryParams: function (params) { // 请求服务器数据时发送的参数，可以在这里添加额外的查询参数，返回false则终止请求

                return {
                    pageSize: params.limit, // 每页要显示的数据条数
                    offset: params.offset, // 每页显示数据的开始行号
                    start:start,
                    end:end,
                    // sort: params.sort, // 要排序的字段
                    // sortOrder: params.order, // 排序规则
                }
            },
            // sortName: 'JOB_ID', // 要排序的字段
            // sortOrder: 'desc', // 排序规则
            columns: [
                {
                    field: 'wx_name', // 返回json数据中的name
                    title: '微信号', // 表格表头显示文字
                    align: 'center', // 左右居中
                    valign: 'middle' // 上下居中
                }, {
                    field: 'chat_fri_num',
                    title: '聊天好友数',
                    align: 'center',
                    valign: 'middle'
                }, {
                    field: 'chat_group_num',
                    title: '聊天群友数',
                    align: 'center',
                    valign: 'middle',
                }, {
                    field: 'add_s_person_num',
                    title: '累计服务人次数',
                    align: 'center',
                    valign: 'middle',
                }, {
                    field: 'send_num',
                    title: '累计信息发送条数',
                    align: 'center',
                    valign: 'middle',
                }, {
                    field: 'chat_group_fri_num',
                    title: '交互（含@）群友人次数',
                    align: 'center',
                    valign: 'middle',
                }
                , {
                    field: 'chat_group_call_num',
                    title: '群内被@人次数',
                    align: 'center',
                    valign: 'middle',
                }
            ]

        });
     };
    $('#search').click(function () {
        $('#table').bootstrapTable('refresh')
    });
});