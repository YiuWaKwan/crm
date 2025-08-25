Date.prototype.format = function(fmt) {
     var o = {
        "M+" : this.getMonth()+1,                 //月份
        "d+" : this.getDate(),                    //日
        "h+" : this.getHours(),                   //小时
        "m+" : this.getMinutes(),                 //分
        "s+" : this.getSeconds(),                 //秒
        "q+" : Math.floor((this.getMonth()+3)/3), //季度
        "S"  : this.getMilliseconds()             //毫秒
    };
    if(/(y+)/.test(fmt)) {
            fmt=fmt.replace(RegExp.$1, (this.getFullYear()+"").substr(4 - RegExp.$1.length));
    }
     for(var k in o) {
        if(new RegExp("("+ k +")").test(fmt)){
             fmt = fmt.replace(RegExp.$1, (RegExp.$1.length==1) ? (o[k]) : (("00"+ o[k]).substr((""+ o[k]).length)));
         }
     }
    return fmt;
}

function filterNull(_val, replaceVal){
		if (replaceVal == null || replaceVal == undefined)
			replaceVal = "&nbsp;";
		if (_val == null || _val == undefined || _val == ""|| _val == "null")
			_val = replaceVal;
		return _val;
	}

function checkEmail(str){
  var re = /^(\w-*\.*)+@(\w-?)+(\.\w{2,})+$/
  if(re.test(str)){
    return true;
  }else{
    return false;
  }
}

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

function childFrameSevercheck(data) {
    if(data  && typeof data=='string'){
        if(data.indexOf("<title>会话丢失</title>") !=-1){
            alert("会话丢失，请重新登录！");
            parent.window.location.href='http://'+window.location.host+'/hl/';
        }
        else if(data.indexOf("<title>账号被下线</title>") !=-1){
            alert("你的账号已在别的地方登录，被迫下线！");
            parent.window.location.href='http://'+window.location.host+'/hl/';
        }
    }
}

function parseJson(data) {
    if(data){
        data = JSON.parse(data);
    }
    return data;
}

function chatTypeTranslate(content, type){
    if(type == 1){
        return content;
    } else if(type == 6){
        return "[语音]";
    }
    else if(type == 2){
        return "[图片]";
    }
    else if(type == 7){
        return "[视频]";
    }
    else if(type == 3){
        return "[附件]";
    }
    else if(type == 8){
        return "[名片]";
    }
    else if(type == 9){
        return "[链接]";
    }
    else if(type == 10){
        return "[位置]";
    }
    else if(type == 11){
        return "[红包]";
    }

    return content;
}

function showAjaxError(funcName,XMLHttpRequest,errorThrown){
    console.log(funcName+":XMLHttpRequest.status："+XMLHttpRequest.status+"\n XMLHttpRequest.statusText："+XMLHttpRequest.statusText+"\n errorThrown："+errorThrown);
     var errorTips=funcName+"失败：服务器响应异常,错误码["+XMLHttpRequest.status+"]";
    if(XMLHttpRequest.status==0){
         var errorTips=funcName+"失败：网络连接失败或服务器无响应，错误码["+XMLHttpRequest.status+"]，请检查网络！";
    }
    return errorTips;
}