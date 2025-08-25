$(function () {
    get_friendsum(); // 好友规模
    get_tasklist_ing();
    get_tasklist_com();
    get_tasklist_pause();
    setInterval("get_tasklist_ing()", 20000); //20s
    setInterval("get_tasklist_pause()", 20000); //20s
    setInterval("get_tasklist_com()", 60000);
});

function get_friendsum() {
    $.ajax({
        type: "POST",
        url: "/WXCRM/friend_sum/",
        data: {},
        success: function (data) {
            severcheck(data);
            data = JSON.parse(data);
            var data = data[0]['f_sum'];
            $("#f_sum").html(String(data).replace(/(?=(?!\b)(\d{3})+$)/g, ','));
        }
    }
        );
}

function get_tasklist_ing() {
    $.ajax({
        type: "POST",
        url: "/WXCRM/get_tasklist_ing/",
        data: {},
        success: function (data) {
            severcheck(data);
            data = JSON.parse(data);
            if(data == ''){
                document.getElementById('title_ing').style.display='none';
            }
            if (data == 'fail'){
                window.location.href='http://'+window.location.host+'/hl/';
            }
            // data = data;
            var tempHtml = '';
            for (x in data) {
                //获取div
                if (x < 5) {
                    tempHtml += '<div class="col_ing" style="display:;" onclick="taskDetail(\'' + data[x]['task_id'] + '\',\''+data[x]['task_state']+ '\')"><div class="about_list">'
                }
                else { tempHtml += '<div class="col_ing" style="display: none;" onclick="taskDetail(\'' + data[x]['task_id'] + '\',\''+data[x]['task_state']+ '\')"><div class="about_list">' }
                tempHtml += '<div style="border-bottom:2px solid #f9f9f9;"><span class="about_sp">' + data[x]['task_name'] + '</span> <a  class="about_a"><img src="/static/img/onekey/next.png" alt="" ></a></div>';
                tempHtml += '<table class="about_table" border="0"  cellspacing="0" cellpadding="0">\n' +
                    '                              <tr>\n' +
                    '                                <th width= "30%"><div class="icon-fea"><img src="' + data[x]['head_picture'] + '" alt="" ></div></th>\n' +
                    '                                <th width= "50% "><h5>' + data[x]['wx_name'] + '</h5></th>\n' +
                    '                              </tr>\n' +
                    '                              <tr>\n' +
                    '                                <td ><div class="about_para">好友总数:</div></td>\n' +
                    '                                <td ><div class="about_para">' + data[x]['f_count'] + '</div></td>\n' +
                    '                              </tr>\n' +
                    '                              <tr>\n' +
                    '                                <td><div class="about_para">任务规模:</div></td>\n' +
                    '                                <td><div class="about_para">' + data[x]['filter_fact'] + '</div></td>\n' +
                    '                              </tr>\n' +
                    '                              <tr>\n' +
                    '                                <td><div class="about_para">已发请求:</div></td>\n' +
                    '                                <td><div class="about_para">' + data[x]['m_count'] + '</div></td>\n' +
                    '                              </tr>\n' +
                    '                              <tr>\n' +
                    '                                <td ><div class="about_para">好友通过:</div></td>\n' +
                    '                                <td ><span class="about_success">' + data[x]['success_count'] + '</td>\n' +
                    '                              </tr>\n' +
                    '                              <tr>\n' +
                    '                               <td colspan=2>\n' +
                    '                                    <div class="progress progress-striped">\n' +
                    '                                        <div class="progress-bar progress-bar-info" role="progressbar"\n' +
                    '                                             aria-valuenow="60" aria-valuemin="0" aria-valuemax="100"\n' +
                    '                                             style="background: linear-gradient(to right, #ff9402 35%,#ffc039 98%);width: ' + data[x]['sum_count'] + '%;">\n';
                    if (parseInt(data[x]['sum_count'])>20){
                        tempHtml+='<span>' + data[x]['sum_count'] + '%</span>'
                    }
                    tempHtml += ' </div>\n' +
                    '                                    </div>\n' +
                    '                                </td>\n' +
                    '                              </tr>\n' +
                    '                            </table>'+'</div></div>';
            }
            $(".about_bottom_warp_ing").html(tempHtml)

        },
        // error: function () {
        //     severcheck(data);
        //     alert('数据加载失败')
        // }
    }
        );
}
function get_tasklist_pause() {
    $.ajax({
        type: "POST",
        dataType: 'json',
        url: "/WXCRM/get_tasklist_pause/",
        data: {},
        success: function (data) {
            if(data == ''){
                document.getElementById('title_pause').style.display='none';
            }
            severcheck(data);
            if (data == 'fail'){
                window.location.href='http://'+window.location.host+'/hl/';
            }
            // data = data;
            var tempHtml = '';
            for (x in data) {
                //获取div
                if (x < 5) {
                    tempHtml += '<div class="col_pause" style="display:;" onclick="taskDetail(\'' + data[x]['task_id'] + '\',\''+data[x]['task_state']+ '\')"><div class="about_list">'
                }
                else { tempHtml += '<div class="col_pause" style="display: none;" onclick="taskDetail(\'' + data[x]['task_id'] + '\',\''+data[x]['task_state']+ '\')"><div class="about_list">' }
                tempHtml += '<div style="border-bottom:2px solid #f9f9f9;"><span class="about_sp">' + data[x]['task_name'] + '</span> <a  class="about_a"><img src="/static/img/onekey/next.png" alt="" ></a></div>';
                tempHtml += '<table class="about_table" border="0"  cellspacing="0" cellpadding="0">\n' +
                    '                              <tr>\n' +
                    '                                <th width= "30%"><div class="icon-fea"><img src="' + data[x]['head_picture'] + '" alt="" ></div></th>\n' +
                    '                                <th width= "50% "><h5>' + data[x]['wx_name'] + '</h5></th>\n' +
                    '                              </tr>\n' +
                    '                              <tr>\n' +
                    '                                <td ><div class="about_para">好友总数:</div></td>\n' +
                    '                                <td ><div class="about_para">' + data[x]['f_count'] + '</div></td>\n' +
                    '                              </tr>\n' +
                    '                              <tr>\n' +
                    '                                <td><div class="about_para">任务规模:</div></td>\n' +
                    '                                <td><div class="about_para">' + data[x]['filter_fact'] + '</div></td>\n' +
                    '                              </tr>\n' +
                    '                              <tr>\n' +
                    '                                <td><div class="about_para">已发请求:</div></td>\n' +
                    '                                <td><div class="about_para">' + data[x]['m_count'] + '</div></td>\n' +
                    '                              </tr>\n' +
                    '                              <tr>\n' +
                    '                                <td ><div class="about_para">好友通过:</div></td>\n' +
                    '                                <td ><span class="about_success">' + data[x]['success_count'] + '</td>\n' +
                    '                              </tr>\n' +
                    '                              <tr>\n' +
                    '                               <td colspan=2>\n' +
                    '                                    <div class="progress progress-striped">\n' +
                    '                                        <div class="progress-bar progress-bar-info" role="progressbar"\n' +
                    '                                             aria-valuenow="60" aria-valuemin="0" aria-valuemax="100"\n' +
                    '                                             style="background: linear-gradient(to right, #ff9402 35%,#ffc039 98%);width: ' + data[x]['sum_count'] + '%;">\n';
                    if (parseInt(data[x]['sum_count'])>20){
                        tempHtml+='<span>' + data[x]['sum_count'] + '%</span>'
                    };
                    tempHtml += ' </div>\n' +
                    '                                    </div>\n' +
                    '                                </td>\n' +
                    '                              </tr>\n' +
                    '                            </table>'+'</div></div>';
            }
            $(".about_bottom_warp_pause").html(tempHtml)

        },
        // error: function () {
        //     alert('数据加载失败')
        // }
    }
        );
}

function addFriend() {
    window.location.href = '/friend_select/';
}
function taskDetail(taskid,task_state) {
            // console.log(taskid,task_state);
           //window.location.href = '/friend_task?taskid=' + taskid;
    showViewModal(taskid,task_state);
}
function get_tasklist_com() {
    $.ajax({
        type: "POST",
        dataType: 'json',
        url: "/WXCRM/get_tasklist_com/",
        data: {},
        success: function (data) {
            if(data == ''){
                document.getElementById('title_com').style.display='none';
            }
            severcheck(data);
            if (data == 'fail'){
                window.location.href='http://'+window.location.host+'/hl/';
            }
            // data = data;
            var tempHtml = '';
            for (x in data) {
                //获取div
                if (x < 5) {
                    tempHtml += '<div class="col_com" style="display:;" onclick="taskDetail(\'' + data[x]['task_id'] + '\',\''+data[x]['task_state']+'\')" ><div class="about_list">'
                }
                else {
                    tempHtml += '<div class="col_com"  style="display: none;" onclick="taskDetail(\'' + data[x]['task_id'] + '\',\''+data[x]['task_state']+'\')"><div class="about_list">' }
                    tempHtml += '<div style="border-bottom:2px solid #f9f9f9;"><span class="about_sp">' + data[x]['task_name'] + '</span> <a  class="about_a"><img src="/static/img/onekey/next.png" alt="" ></a></div>';
                    tempHtml += '<table class="about_table" border="0"  cellspacing="0" cellpadding="0">\n' +
                    '                              <tr>\n' +
                    '                                <th><div class="icon-fea"><img src="' + data[x]['head_picture'] + '" alt="" ></div></th>\n' +
                    '                                <th><h5>' + data[x]['wx_name'] + '</h5></th>\n' +
                    '                              </tr>\n' +
                    '                              <tr>\n' +
                    '                                <td width= "30%" ><div class="about_para">好友总数:</div></td>\n' +
                    '                                <td width= "50% "><div class="about_para">' + data[x]['f_count'] + '</div></td>\n' +
                    '                              </tr>\n' +
                    '                              <tr>\n' +
                    '                                <td><div class="about_para">任务规模:</div></td>\n' +
                    '                                <td><div class="about_para">' + data[x]['filter_fact'] + '</div></td>\n' +
                    '                              </tr>\n' +
                    '                              <tr>\n' +
                    '                                <td><div class="about_para">已发请求:</div></td>\n' +
                    '                                <td><div class="about_para">' + data[x]['m_count'] + '</div></td>\n' +
                    '                              </tr>\n' +
                    '                              <tr>\n' +
                    '                                <td ><div class="about_para">好友通过:</div></td>\n' +
                    '                                <td ><span class="about_success">' + data[x]['success_count'] + '</td>\n' +
                    '                              </tr>\n' +
                    '                              <tr>\n' +
                    '                               <td colspan=2>\n' +
                    '                                    <div class="progress progress-striped">\n' +
                    '                                        <div class="progress-bar progress-bar-info" role="progressbar"\n' +
                    '                                             aria-valuenow="60" aria-valuemin="0" aria-valuemax="100"\n' +
                    '                                             style="background: linear-gradient(to right, #ff9402 35%,#ffc039 98%);width: ' + data[x]['sum_count'] + '%;">\n';
                    if (parseInt(data[x]['sum_count'])>20){
                        tempHtml+='<span>' + data[x]['sum_count'] + '%</span>'
                    }
                    tempHtml += ' </div>\n' +
                    '                                    </div>\n' +
                    '                                </td>\n' +
                    '                              </tr>\n' +
                    '                            </table>'+'</div></div>';
            }
            $(".about_bottom_warp_com").html(tempHtml)
            // function taskDetail(taskid) {
            //     console.log(taskid);
            //     window.location.href = '/friend_task?taskid=2';
            // }

        },
        // error: function () {
        //     alert('数据加载失败')
        // }
    }
        );
}

function js_ing() {
    if ($(".about_ing_more").text() == "更多") {
        $(".about_ing_more").text("收起");
        $(".col_ing").each(function () {
            this.style.display = "";
        })
    } else {
        $(".about_ing_more").text("更多");
        rn = 0;
        $(".col_ing").each(function () {
            rn = rn + 1;
            if (rn > 5) { this.style.display = "none"; }

        })
    }
}

function js_pause() {
    if ($(".about_ing_more").text() == "更多") {
        $(".about_ing_more").text("收起");
        $(".col_pause").each(function () {
            this.style.display = "";
        })
    } else {
        $(".about_ing_more").text("更多");
        rn = 0;
        $(".col_pause").each(function () {
            rn = rn + 1;
            if (rn > 5) { this.style.display = "none"; }

        })
    }
}

function js_com() {
    if ($(".about_com_more").text() == "更多") {
        $(".about_com_more").text("收起");
            $(".col_com").each(function () {
                this.style.display = "";
            })
        } else {
            $(".about_com_more").text("更多");
            rn = 0;
            $(".col_com").each(function () {
                rn = rn + 1;
                if (rn > 5) { this.style.display = "none"; }
            })
        }
}
