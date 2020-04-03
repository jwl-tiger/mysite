import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from .models import ReadNum,ReadDetail


def read_statistics_once_read(request,obj):
    ct = ContentType.objects.get_for_model(obj) #获取到与obj的模型对应的ContentType对象
    key = "%s_%s_read" % (ct.model,obj.pk) #.model：以字符串的形式返回与ContentType对象对应的模型的名称

    if not request.COOKIES.get(key): #第一次请求，get不到这样key形式的cookie，执行加1操作
        #总阅读数+1
        readnum,created = ReadNum.objects.get_or_create(content_type=ct,object_id=obj.pk)
        readnum.read_num +=1
        readnum.save()
        #当天阅读数+1：分别为两个模型下的read_num字段加1
        date = timezone.now().date()
        readDetail,created = ReadDetail.objects.get_or_create(content_type=ct,object_id=obj.pk,date=date)
        readDetail.read_num += 1
        readDetail.save()
    return key

def get_seven_days_read_data(content_type):
    today = timezone.now().date() #得到今天的日期
    dates = []
    read_nums = []
    for i in range(7,0,-1):
        date = today - datetime.timedelta(days=i) #得到连续一周的日期：减去差值为i天的时间段
        dates.append(date.strftime('%m/%d'))
        read_datails = ReadDetail.objects.filter(content_type=content_type,date=date) #根据需求设置筛选条件= =，得到对应模型且日期为date的全部对象组成的序列
        result = read_datails.aggregate(read_num_sum = Sum('read_num'))      #
        read_nums.append(result['read_num_sum'] or 0)                             #返回一个元组，因为Sum（）结果被赋给了变量，里面是字典的形式：（'read_num_sum':计算结果）
    return dates,read_nums       

def get_today_hot_data(content_type):
    today = timezone.now().date()
    read_datails = ReadDetail.objects.filter(content_type=content_type,date=today).order_by('-read_num')
                                                                                     #order_by函数，根据对象参数的值的大小对这个序列进行排序
    return read_datails[:3]

def get_yesterday_hot_data(content_type):
    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days=1)
    read_datails = ReadDetail.objects.filter(content_type=content_type,date=yesterday).order_by('-read_num')
                                                                                     #order_by函数，根据对象参数的值的大小对这个序列进行排序
    return read_datails[:3]
