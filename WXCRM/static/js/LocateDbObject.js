useIndexedDB = true;
var indexedDB = window.indexedDB || window.webkitIndexedDB || window.mozIndexedDB || window.msIndexedDB;
if(!indexedDB)
{
    useIndexedDB=false;
    console.log("你的浏览器不支持IndexedDB");
}

myIndexedDb = {
    db_version:20180722, //数据库版本
    db_name:"myChart",   //数据库名称
    max_store_list: 500, //每个store(最大记录数)
    store_name:"wx_table", //储存表名
    store_param:{object:1,list:2}, //单个对象和数组的定义
    update_param:{voice:1, video:2, filestate:3} //修改内容
};
myIndexedDb.onerror = function(e) {
    console.log(e);
};

myIndexedDb.open = function(){
    var requestDb = indexedDB.open(myIndexedDb.db_name, myIndexedDb.db_version);
    requestDb.onerror = function(e) {
        console.log("打开数据库报错！");
        console.log(e.currentTarget.error.message);
    };
    requestDb.onsuccess = function(e) {
        console.log("打开数据库成功！");
    };

    requestDb.onupgradeneeded = function(e) {
        myIndexedDb.db = e.target.result;
        //获取数据表，如果不存在就创建，按微信主号id+好友id(群id)标识建一张表
        //只能在onupgradeneeded函数中创建objcetstore否则会报错
        if (!myIndexedDb.db.objectStoreNames.contains(myIndexedDb.store_name)) {
            myIndexedDb.db.createObjectStore(myIndexedDb.store_name, { keyPath: 'key'});
        }
        console.log('数据库版本更改为： ' + myIndexedDb.db_version);
    };
}
//数据库每次要单独打开(更新数据)
myIndexedDb.updateDataByKey=function(store_name, store_key, store_obj, store_type /*1 单个对象  2 数组*/) {
    var requestDb = indexedDB.open(myIndexedDb.db_name, myIndexedDb.db_version);

    requestDb.onerror = function(e) {
        console.log("打开数据库报错！");
        console.log(e.currentTarget.error.message);
    };

    requestDb.onsuccess = function(e) {
        var db = e.target.result;
        var transaction=db.transaction(store_name,'readwrite');
        var store=transaction.objectStore(store_name);
        var request=store.get(store_key);
        request.onsuccess=function(e){
            var store_obj_tmp=[]
            if(store_type == 1){
                store_obj_tmp.push(store_obj);
            }else{
                store_obj_tmp=store_obj;
            }
            var dataList =e.target.result;
            if(!dataList){
                dataList={"key":store_key, "content":store_obj_tmp};
            }
            else{
                var contentList = dataList.content;
                store_obj_tmp.forEach(function (val, index) {
                    //判断最大记录数  myIndexedDb.max_store_list
                    if(contentList.length >= myIndexedDb.max_store_list){
                        contentList.shift();//删除第一个元素
                    }
                    contentList.push(val);//在最后添加一个元素
                })
                dataList={"key":store_key,"content":contentList};
            }

            var transaction=db.transaction(store_name,'readwrite');
            var store=transaction.objectStore(store_name);
            store.put(dataList);

            db.close();
        };

        request.onerror = function(e) {
            console.log("读取store错误！");
            console.log(e.currentTarget.error.message);
        };
    };

    requestDb.onupgradeneeded = function(e) {
        myIndexedDb.db = e.target.result;
        //获取数据表，如果不存在就创建，按微信主号id+好友id(群id)标识建一张表
        //只能在onupgradeneeded函数中创建objcetstore否则会报错
        if (!myIndexedDb.db.objectStoreNames.contains(myIndexedDb.store_name)) {
            myIndexedDb.db.createObjectStore(myIndexedDb.store_name, { keyPath: 'key'});
        }
        console.log('数据库版本更改为： ' + myIndexedDb.db_version);
    };
}

//更新微信聊天内容具体的某一记录的某个字段
myIndexedDb.updateContentByKey=function(store_name, store_key, store_obj, store_type /*1 改是否已读  2 视频资料更新*/) {
    var requestDb = indexedDB.open(myIndexedDb.db_name, myIndexedDb.db_version);

    requestDb.onerror = function(e) {
        console.log("打开数据库报错！");
        console.log(e.currentTarget.error.message);
    };

    requestDb.onsuccess = function(e) {
        var db = e.target.result;
        var transaction=db.transaction(store_name,'readwrite');
        var store=transaction.objectStore(store_name);
        var request=store.get(store_key);
        request.onsuccess=function(e){
            var dataList =e.target.result;
            if(dataList){
                var contentList = dataList.content;
                contentList.forEach(function (val, index) {
                    if(val.msgId==store_obj.msgId){
                        if(store_type == myIndexedDb.update_param.voice){
                            val.voiceUnRead = store_obj.voiceUnRead;
                        }
                        else if(store_type == myIndexedDb.update_param.video){

                        }
                        else if(store_type == myIndexedDb.update_param.filestate){
                            val.FileStatus = store_obj.FileStatus;
                            val.content = store_obj.content;
                        }
                    }
                })
                dataList={"key":store_key,"content":contentList};
            }

            var transaction=db.transaction(store_name,'readwrite');
            var store=transaction.objectStore(store_name);
            store.put(dataList);

            db.close();
        };

        request.onerror = function(e) {
            console.log("读取store错误！");
            console.log(e.currentTarget.error.message);
        };
    };
}

//数据库每次要单独打开(删除数据)
myIndexedDb.deleteDataByKey=function(store_name, store_key) {
    var requestDb = indexedDB.open(myIndexedDb.db_name, myIndexedDb.db_version);

    requestDb.onerror = function(e) {
        console.log("打开数据库报错！");
        console.log(e.currentTarget.error.message);
    };

    requestDb.onsuccess = function(e) {
        var db = e.target.result;
        var transaction=db.transaction(store_name,'readwrite');
        var store=transaction.objectStore(store_name);
        store.delete(store_key);

        db.close();
    };
}

myIndexedDb.getDataByKey=function(store_name, store_key) {
    var requestDb = indexedDB.open(myIndexedDb.db_name, myIndexedDb.db_version);

    requestDb.onerror = function(e) {
        console.log("打开数据库报错！");
        console.log(e.currentTarget.error.message);
    };

    requestDb.onsuccess = function(e) {
        var db = e.target.result;
        if (!db.objectStoreNames.contains(store_name)) {//去数据库中查询
            //调用js方法进行操作
            returnDataResult([]);
        }
        else {
            var transaction = db.transaction(store_name, 'readwrite');
            var store = transaction.objectStore(store_name);
            var request = store.get(store_key);
            request.onsuccess = function (e) {
                var dataList = e.target.result;
                //调用js方法进行操作
                if(!dataList || dataList == [] || (dataList && dataList.content instanceof Array && dataList.content.length < 10)){
                    store.delete(store_key);  //把缓存清空
                    returnDataResult([]);
                }
                else{
                    returnDataResult(dataList.content);
                }
            };
        }
        db.close();
    };
}

function deleteDB(){
    indexedDB.deleteDatabase(myIndexedDb.db_name);
}

function clearDB(){
        var requestDb = indexedDB.open(myIndexedDb.db_name, myIndexedDb.db_version);
        requestDb.onerror = function(e) {
            console.log("打开数据库报错！");
            console.log(e.currentTarget.error.message);
        };
        requestDb.onsuccess = function(e) {
            var db = e.target.result;
            var transaction = db.transaction(myIndexedDb.store_name, 'readwrite');
            var store = transaction.objectStore(myIndexedDb.store_name);
            store.clear();
        }
}