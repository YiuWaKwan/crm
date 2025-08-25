import datetime
import urllib

def single_get_first(unicode1):
    try:
        str1 = unicode1.encode('gbk')
        try:
            ord(str1)
            return unicode1
        except:
            asc = str1[0] * 256 + str1[1] - 65536
            if asc >= -20319 and asc <= -20284:
                return 'a'
            if asc >= -20283 and asc <= -19776:
                return 'b'
            if asc >= -19775 and asc <= -19219:
                return 'c'
            if asc >= -19218 and asc <= -18711:
                return 'd'
            if asc >= -18710 and asc <= -18527:
                return 'e'
            if asc >= -18526 and asc <= -18240:
                return 'f'
            if asc >= -18239 and asc <= -17923:
                return 'g'
            if asc >= -17922 and asc <= -17418:
                return 'h'
            if asc >= -17417 and asc <= -16475:
                return 'j'
            if asc >= -16474 and asc <= -16213:
                return 'k'
            if asc >= -16212 and asc <= -15641:
                return 'l'
            if asc >= -15640 and asc <= -15166:
                return 'm'
            if asc >= -15165 and asc <= -14923:
                return 'n'
            if asc >= -14922 and asc <= -14915:
                return 'o'
            if asc >= -14914 and asc <= -14631:
                return 'p'
            if asc >= -14630 and asc <= -14150:
                return 'q'
            if asc >= -14149 and asc <= -14091:
                return 'r'
            if asc >= -14090 and asc <= -13119:
                return 's'
            if asc >= -13118 and asc <= -12839:
                return 't'
            if asc >= -12838 and asc <= -12557:
                return 'w'
            if asc >= -12556 and asc <= -11848:
                return 'x'
            if asc >= -11847 and asc <= -11056:
                return 'y'
            if asc >= -11055 and asc <= -10247:
                return 'z'
            return ''
    except:
        return ''


def getPinyin(string):
    if string == None:
        return None
    lst = list(string)
    ret = single_get_first(lst[0]).upper()
    if ret == ':':
        ret = 'A'
    elif ret == '1':
        ret = 'Y'
    elif ret == '2':
        ret = 'E'
    elif ret == '3' or ret == '4':
        ret = 'S'
    elif ret == '5':
        ret = 'W'
    elif ret == '6':
        ret = 'L'
    elif ret == '7':
        ret = 'Q'
    elif ret == '8':
        ret = 'B'
    elif ret == '9':
        ret = 'J'
    return ret

def getDayFormat(str):
    if str == None:
        return None
    targetDate=str.split(" ")[0]+" 00:00:00"
    date1 = datetime.datetime.now()
    date2 = datetime.datetime.strptime(targetDate, '%Y-%m-%d %H:%M:%S')
    delta = date1 - date2
    if delta.days == 0:
        return str.split(" ")[1]
    elif delta.days == 1:
        return "昨天"
    elif delta.days > 1 and delta.days < 30:
        return "%d天前"%delta.days
    elif delta.days > 30 and delta.days < 60:
        return "上月"
    elif delta.days > 60 and delta.days < 360:
        return "两月前"
    else:
        return "去年"

def getValue(request,flag):
    if request.method == 'GET':
        return request.GET.get(flag)
    elif request.method == 'POST':
        return request.POST.get(flag)
    return ""

def getValueList(request,flag):
    if request.method == 'GET':
        return request.GET.getlist(flag)
    elif request.method == 'POST':
        return request.POST.getlist(flag)
    return ""

def chartTypeTranslate(content, type):
    if type == "1":
        return content
    elif type == "6":
        return "[语音]"
    elif type == "2":
        return "[图片]"
    elif type == "7":
        return "[视频]"
    elif type == "3":
        return "[附件]"
    elif type == "8":
        return "[名片]"
    elif type == "9":
        return "[链接]"
    elif type == "10":
        return "[位置]"
    elif type == "11":
        return "[红包]"

    return content


def alarm(logger, msg, alarm_server):
    msg = urllib.parse.quote(msg)
    warn_msg = "%s?msg=%s&type=2&user=R_221&creator=maizq" % (alarm_server, msg)
    logger.info(warn_msg)
    warning(warn_msg)

def warning(url):
    http_client=urllib.request.urlopen(url, timeout = 5)
    print(http_client.read())
    return http_client.read()

if __name__ == '__main__':
    print(getPinyin('drp200992'))
