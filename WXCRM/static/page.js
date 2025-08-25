function setPage(page,method,flag){
	if(flag == "show"){
		if(!$("#pageSize_value").val()){
			var tempHtmlPage="";
			tempHtmlPage="<select id='pageSize_value' class='show-tick form-control' onchange='"+method+"(1)'>"+
			"<option value='5'>5条/页</option><option value='10'>10条/页</option><option value='20'>20条/页</option>"+
			"<option value='30'>30条/页</option></select>";
			$("#div_pageSize").html(tempHtmlPage);
			
			tempHtmlPage="";
			tempHtmlPage="<input type='text' "+ "class='pull-right form-control' id='pageSize' placeholder='页' value=''/>"+
				"<button type='button' class='btn btn-primary pull-right' "+
			"onclick='var page=$(\"#pageSize\").val(); if(!isNaN(page)){"+method+"(page);}' >跳转</button>";
			$("#div_button").html(tempHtmlPage);
		}
		
		if(page["pages"] == 0){
			$("#div_pageSize").html("");
			$("#div_button").html("");
		}
	}
	else{$("#pageSize_value").hide();}
	$("#page").html("");
	$("#userListTable_info").html("共"+page["total"]+"条，当前第"+page["pageNum"]+"/"+page["pages"]+"页");
	var pre = page.pageNum == 1 ? 0 : (page.pageNum - 1);
	var next = page.pageNum + 1;
	html_ul = "<li class='paginate_button page-item previous ";

	if(page["pages"] == 0){
		return;
	}
	
	//前一页按钮
	if(pre == 0){html_ul=html_ul+"disabled'> <a href='#' class='page-link'>前一页</a></li>";}
	else{html_ul=html_ul+"' > <a href='#' onclick='"+method+"("+pre+")' class='page-link'>前一页</a></li>";}
	
	if(page["pages"] <= 7){
		for(var i=1;i<=page["pages"];i++){
			html_ul=addPageButton(html_ul, i, page.pageNum,method);
		}
	}
	else{
		//第一页
		html_ul=addPageButton(html_ul, 1, page.pageNum,method);
		
		//第二页
		if(page.pageNum >= 5){
			html_ul=addPageButtonDisable(html_ul);
			if(page.pages-page.pageNum > 3){
				//中间3页
				html_ul=addPageButton(html_ul,page.pageNum-1,page.pageNum,method);
				html_ul=addPageButton(html_ul,page.pageNum,page.pageNum,method);
				html_ul=addPageButton(html_ul,page.pageNum+1,page.pageNum,method);
			}
		}
		else {
			html_ul=addPageButton(html_ul,2,page.pageNum,method);
			//中间3页
			html_ul=addPageButton(html_ul,3,page.pageNum,method);
			html_ul=addPageButton(html_ul,4,page.pageNum,method);
			html_ul=addPageButton(html_ul,5,page.pageNum,method);
		}
		
		//倒数第二页
		if(page.pages-page.pageNum > 3){
			html_ul=addPageButtonDisable(html_ul);
		}
		else {
			//中间3页
			html_ul=addPageButton(html_ul,page.pages-4,page.pageNum,method);
			html_ul=addPageButton(html_ul,page.pages-3,page.pageNum,method);
			html_ul=addPageButton(html_ul,page.pages-2,page.pageNum,method);
			//中间3页
			html_ul=addPageButton(html_ul,page.pages-1,page.pageNum,method);
		}
		
		//最后一页按钮
		html_ul=addPageButton(html_ul, page.pages, page.pageNum,method);
	}
	
	//后一页按钮
	html_ul = html_ul + "<li class='paginate_button page-item next ";
	if(next > page.pages){html_ul = html_ul + "disabled'> <a href='#' class='page-link'>后一页</a></li>";}
	else{html_ul = html_ul + "'> <a href='#' onclick='"+method+"("+next+")' class='page-link'>后一页</a></li>";}
	
	$("#page").html(html_ul);
}

function addPageButton(html_ul,pageNum,currentPage,method){
	html_ul=html_ul+"<li class='paginate_button page-item "
	if(pageNum == currentPage){html_ul=html_ul+" active'> <a href='#' class='page-link'>"+pageNum+"</a></li>";}
	else{html_ul=html_ul+"'> <a href='#' onclick='"+method+"("+pageNum+")' class='page-link'>"+pageNum+"</a></li>";}
	return html_ul;
}

function addPageButtonDisable(html_ul){
	html_ul=html_ul+"<li class='paginate_button disabled'><a href='#' class='page-link'>…</a></li>";
	return html_ul;
}