 /*用于群成员的信息维护*/

function getScope(){
       var appElementGM = document.querySelector('[ng-controller=appController]');
       //获取$scope变量
       var $scopeGM = angular.element(appElementGM).scope();
       return $scopeGM;
}

 function getMemberInfo(member_wx_id,headPic,group_member_name){//
       var result;
       var $scopeGM = getScope();
       $.ajax({
            type: "GET",
            async:false,
            url: "http://"+window.location.host+"/WXCRM/groupMember/",
            data: {"oper":"getMemberInfo","member_wx_id":member_wx_id},
            success: function (result) {
                severcheck(result);
                //if (!result) {
                    result = parseJson(result);
                    $scopeGM.groupMemberInfoExt = result.memberInfoExt;
                    $scopeGM.groupMemberFlags = result.memberFlags;
                    //同步到Angular控制器中，则需要调用$apply()方法即可
                    //$scopeGM.$apply();

                //}
            },
            error: function (XMLHttpRequest, textStatus, errorThrown, data) {
                alert(data);// 请求失败执行代码
            }
        });
        $scopeGM.groupMemberInfoExt["headPic"] =headPic;
        $scopeGM.groupMemberInfoExt["group_member_name"] =group_member_name;
    }

  function editMemberInfo(){
       var $scopeGM = getScope();
       var setflagMem= $("#setflagMem");
       $("#extSeqId").val($scopeGM.groupMemberInfoExt.seqId);
       $("#real_name").val($scopeGM.groupMemberInfoExt.real_name);
       $("#birthday").val($scopeGM.groupMemberInfoExt.birthday);
       $("select[name='setflagMem']").select2('val', $scopeGM.groupMemberInfoExt.flagIds);
       $('input[name="sex"]').each( function(){
            if (this.value==$scopeGM.groupMemberInfoExt.sex)
            {
                $(this).iCheck('check');
            }
       })
       $("#address").val($scopeGM.groupMemberInfoExt.address);
        //初始化省份
       var bindData=getAreaData(null,"province");
       bindSelectOption(bindData,"province");
       var provinceValue=$scopeGM.groupMemberInfoExt.province;
       $("#province").select2('val',provinceValue);
       if(provinceValue!=null&&provinceValue!=""){
           bindData=getAreaData(provinceValue,"city");
           bindSelectOption(bindData,"city");
       }
      var cityValue=$scopeGM.groupMemberInfoExt.city
      $("#city").select2('val',cityValue);
       if(cityValue!=null&&cityValue!=""){
           bindData=getAreaData(cityValue,"area");
           bindSelectOption(bindData,"area");
       }
      $("#area").select2('val',$scopeGM.groupMemberInfoExt.area);
        $('input[type="checkbox"].minimal, input[type="radio"].minimal').iCheck({
            checkboxClass: 'icheckbox_minimal-blue',
            radioClass: 'iradio_minimal-blue'
        })

       $scopeGM.ifEditMemberInfo=true;

  }
//保存成员信息
function saveMemberInfoExt(){
    var $scopeGM = getScope();
    var birthday= $("#birthday").val();
    var sex= $("input[name='sex']:checked").val();
    var flags=$("select[name='setflagMem']").select2("val");
    var real_name=$("#real_name").val();
    $.ajax({
            type: 'POST',
            traditional: true,//传递数组
            url: '/WXCRM/groupMember/',
            data: {
                "oper": "saveMemberInfoExt",
                "member_wx_id": $scopeGM.groupMemberInfoExt.member_wx_id,
                "group_id":  $scopeGM.currentContact.wx_id,
                "wx_main_id":  $scopeGM.account.wx_id,
                "seqId": $("#extSeqId").val(),
                "birthday":birthday,
                "sex":sex,
                "real_name":real_name,
                "flags":flags,
                "province":$("#province").select2("val"),
                "city":$("#city").select2("val"),
                "area":$("#area").select2("val"),
                "address":$("#address").val()
            },
            success: function (res) {
                severcheck(res);
                res = parseJson(res);
                var result = res.result;
                if (result == 1) {
                    getMemberInfo($scopeGM.groupMemberInfoExt.member_wx_id,$scopeGM.groupMemberInfoExt.headPic,$scopeGM.groupMemberInfoExt.group_member_name);
                    $scopeGM.ifEditMemberInfo=false;
                    clearEditInfo();
                } else {
                    alert('保存失败')
                }
            }
        });
}

function clearEditInfo() {
        $("#seqId").val('');
        $("#birthday").val('');
        $("#real_name").val('');
        $("select[name='setflagMem']").select2('val',[]);
        $('input[name="sex"]').each( function(){
                $(this).iCheck('uncheck');
        });
        $("#address").val('');
    }
function initSex(){
    //性别词典初始化
    var res = getSexData();
    if(res!=null&&res.length>0){
        tempHtml="";
        for(var i=0;i<res.length;i++){
            tempHtml+='  <input type="radio" name="sex" class="minimal" value="'+res[i].dictValue+'">'+res[i].dictName;
        }
        $("#sexSpan").html(tempHtml);
    }

}
function getSexData(){
    var ret;
    if(sessionStorage.sexData){
        ret=JSON.parse(sessionStorage.sexData);
    }else{
        $.ajax({
            type: 'get',
            async:false,
            url: '/WXCRM/groupMember/',
            data: {"oper":"getDictData","dictType":"sex"},
            success: function (res) {
                severcheck(res);
                ret = parseJson(res);
                sessionStorage["sexData"]=JSON.stringify(ret);
            }
        });
    }
    return ret;
}
function getAreaData(parentCode,childName){
    var result;
    $.ajax({
        type: 'get',
        async:false,
        url: '/WXCRM/groupMember/',
        data: {"oper":"getAreaData","parentCode":parentCode,"childName":childName},
        success: function (res) {
            severcheck(res);
            res = parseJson(res);
            result= res;
        }
    });
    return result;
 }

function bindSelectOption(res,selectId){
     tempHtml='<option  value="">请选择</option>';
     if(res!=null&&res.length>0){
        for(var i=0;i<res.length;i++){
            tempHtml+='<option  value="'+res[i][0]+'">'+res[i][1]+'</option>';
        }
     }
     $("#"+selectId).html(tempHtml);
     $("#"+selectId).trigger("change");
 }

 function onChangeSelect(selectId,childName){
    $("#"+selectId).on("select2:select", function(e) {
            var selectedCode=$("#"+selectId).select2("val");
            var bindData=null;
            if(selectedCode!=null&&selectedCode!=""){
                bindData=getAreaData(selectedCode,childName)
            }
            bindSelectOption(bindData,childName);
            if(selectId=='province'){//切换了省份后清空区县列表
                $("#city").select2('val','');
                $("#area").select2('val','');
                bindData=null;
                bindSelectOption(bindData,"area");
            }else if(selectId=='city'){
                $("#area").select2('val','');
            }
    });

 }

function initData(){
    initSex();//初始化性别
    //绑定选择时间
    $("#province").on("change", function(e) {
        onChangeSelect("province","city");
    });
    $("#city").on("change", function(e) {
        onChangeSelect("city","area");
    });
}

initData();