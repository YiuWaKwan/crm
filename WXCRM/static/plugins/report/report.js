window.onload = function () {

    dataEcharts();
    $('#datareport').click(function () {
        dataEcharts();
    });
    $('#wechatreport').click(function () {
        wechatEcharts();
    });
    $('#wgreport').click(function () {
        wgEcharts();
    });
};

function dataEcharts() {
    $.ajax({
        type: "POST",
        dataType: 'json',
        url: "../get_data_report/",
        data: {},
        success: function (data) {
            var myDate = new Date();
            month = ' '+(myDate.getMonth()+1).toString()+'月';
            var myChart = echarts.init(document.getElementById('report'));
            var xdata=[];
            var ydata=[];
             for(x in data){
                xdata.push(data[x]['cur_date']);
                ydata.push(data[x]['add_s_person_num']);
            }
            var option = {
                title: {
                    text: '累计服务人次数',
                    left: 'center'
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
                    data: ['服务人次数'],
                    bottom: 5
                },
                toolbox: {
                    feature: {
                        dataView: {},
                        magicType: {type: ['line', 'bar', 'stack', 'tiled']},
                        restore: {},
                        saveAsImage: {},
                    }
                },
                grid: {
                    left: '3%',
                    right: '6%',
                    bottom: '5%',
                    containLabel: true
                },
                xAxis: [
                    {
                        type: 'category',
                        boundaryGap: false,
                        data: xdata,
                        name: month,
                    }
                ],
                yAxis: [
                    {
                        type: 'value'
                    }
                ],
                series: [
                    {
                        name: '服务人次数',
                        type: 'line',
                        color:'#fe4668',
                        smooth: true,
                        areaStyle: {
                            normal: {
                                color: '#d56f89', opacity: 0.26
                            }
                        },
                        data: ydata
                    }
                ]
            };
            myChart.setOption(option,true);
            },
        error: function (e) {
            alert("未知错误，请联系系统管理员。");
        }
    });
};

function wechatEcharts() {
    $.ajax({
        type: "POST",
        dataType: 'json',
        url: "../get_wechat_report/",
        data: {},
        success: function (data) {
            var myDate = new Date();
            month = ' '+(myDate.getMonth()+1).toString()+'月';
            var xdata=[];
            var ydata1=[];
            var ydata2=[];
            var ydata3=[];
            var ydata4=[];
            var ydata5=[];
            var ydata6=[];
            for(x in data){
                xdata.push(data[x]['cur_date']);
                ydata1.push(data[x]['send_num']);
                ydata2.push(data[x]['receive_num']);
                ydata3.push(data[x]['chat_group_fri_num']);
                ydata4.push(data[x]['chat_fri_num']);
                ydata5.push(data[x]['chat_group_num']);
                ydata6.push(data[x]['chat_group_call_num']);
            }
            var myChart = echarts.init(document.getElementById('report'));
            var option = {
                title: {
                    text: '微信聊天情况',
                    left: 'center'
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
                    data: ['发送消息数', '接收消息数','聊天群友数','聊天好友数','与群友交互数','群内被@次数'],
                    bottom: 5
                },
                toolbox: {
                    feature: {
                        dataView: {},
                        magicType: {type: ['line', 'bar', 'stack', 'tiled']},
                        restore: {},
                        saveAsImage: {},
                    }
                },
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
                        data:xdata,
                        name:month
                    }
                ],
                yAxis: [
                    {
                        type: 'value'
                    },
                    {
                        type: 'value'
                    }
                ],
                series: [
                    {
                        name: '发送消息数',
                        type: 'line',
                        smooth: true,
                        yAxisIndex: 1,
                        // areaStyle: {
                        //     normal: {
                        //         color: 'red', opacity: 0.4
                        //     }
                        // },
                        data: ydata1
                    },
                    {
                        name: '接收消息数',
                        type: 'line',
                        smooth: true,
                        yAxisIndex: 1,
                        // areaStyle: {
                        //     normal: {
                        //         color: 'blue', opacity: 0.4
                        //     }
                        // },
                        data: ydata2
                    },
                    {
                        name: '聊天群友数',
                        type: 'line',
                        smooth: true,
                        // areaStyle: {
                        //     normal: {
                        //         color: 'blue', opacity: 0.4
                        //     }
                        // },
                        data: ydata3
                    },
                    {
                        name: '聊天好友数',
                        type: 'line',
                        smooth: true,
                        // areaStyle: {
                        //     normal: {
                        //         color: 'blue', opacity: 0.4
                        //     }
                        // },
                        data: ydata4
                    },
                    {
                        name: '与群友交互数',
                        type: 'line',
                        smooth: true,
                        yAxisIndex: 1,
                        // areaStyle: {
                        //     normal: {
                        //         color: 'blue', opacity: 0.4
                        //     }
                        // },
                        data: ydata5
                    },
                    {
                        name: '群内被@次数',
                        type: 'line',
                        smooth: true,
                        // areaStyle: {
                        //     normal: {
                        //         color: 'blue', opacity: 0.4
                        //     }
                        // },
                        data: ydata6
                    }
                ]
            };
            myChart.setOption(option,true);
      },
        error: function (e) {
            alert("未知错误，请联系系统管理员。");
        }
    });
};
function wgEcharts() {
     $.ajax({
        type: "POST",
        dataType: 'json',
        url: "../get_wg_report/",
        data: {},
        success: function (data) {
            var myDate = new Date();
            var month = ' '+(myDate.getMonth()+1).toString()+'月';
            var xdata=[];
            var ydata1=[];
            var ydata2=[];
            var ydata3=[];
            var ydata4=[];
            var ydata5=[];
            var ydata6=[];
            for(x in data){
                xdata.push(data[x]['cur_date']);
                ydata1.push(data[x]['group_num']);
                ydata2.push(data[x]['group_fri_num']);
                ydata3.push(data[x]['send_msg_num']);
                ydata4.push(data[x]['receive_msg_num']);
                ydata5.push(data[x]['chat_fri_inter_num']);
                ydata6.push(data[x]['new_chat_fri_num']);
            }
    var myChart = echarts.init(document.getElementById('report'));
    var option = {
        title: {
            text: '微信群聊情况',
            left: 'center'
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
            data: ['微信群数','微信群友数','发送消息数','接收消息数','与群友交互次数', '新增群友数'],
            bottom: 5
        },
        toolbox: {
            feature: {
                dataView: {},
                magicType: {type: ['line', 'bar', 'stack', 'tiled']},
                restore: {},
                saveAsImage: {},
            }
        },
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
                name:month
            }
        ],
        yAxis: [
            {
                type: 'value'
            },
            {
                type: 'value'
            }
        ],
       series: [
            {
                name: '微信群数',
                type: 'line',
                smooth: true,
                // areaStyle: {
                //     normal: {
                //         color: 'red', opacity: 0.4
                //     }
                // },
                data: ydata1
            },
            {
                name: '微信群友数',
                type: 'line',
                smooth: true,
                // areaStyle: {
                //     normal: {
                //         color: 'blue', opacity: 0.4
                //     }
                // },
                data: ydata2
            },
            {
                name: '发送消息数',
                type: 'line',
                smooth: true,
                yAxisIndex: 1,
                // areaStyle: {
                //     normal: {
                //         color: 'blue', opacity: 0.4
                //     }
                // },
                data: ydata3
            },
            {
                name: '接收消息数',
                type: 'line',
                smooth: true,
                yAxisIndex: 1,
                // areaStyle: {
                //     normal: {
                //         color: 'blue', opacity: 0.4
                //     }
                // },
                data: ydata4
            },
            {
                name: '与群友交互次数',
                type: 'line',
                smooth: true,
                yAxisIndex: 1,
                // areaStyle: {
                //     normal: {
                //         color: 'blue', opacity: 0.4
                //     }
                // },
                data: ydata5
            },
            {
                name: '新增群友数',
                type: 'line',
                smooth: true,
                yAxisIndex: 1,
                // areaStyle: {
                //     normal: {
                //         color: 'blue', opacity: 0.4
                //     }
                // },
                data: ydata6
            }
        ]
    };
    myChart.setOption(option,true);
    },
        error: function (e) {
            alert("未知错误，请联系系统管理员。");
        }
    });
};