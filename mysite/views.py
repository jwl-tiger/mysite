import datetime
from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum,Q
from django.core.cache import cache
from django.urls import reverse
from read_statistics.utils import get_seven_days_read_data, get_today_hot_data, get_yesterday_hot_data
from blog.models import Blog
from django.core.paginator import Paginator
from django.core.mail import send_mail, send_mass_mail, EmailMultiAlternatives
 
from django.conf import settings


def get_seven_days_hot_blogs():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects.filter(read_details__date__lt=today,read_details__date__gte=date) \
                    .values('id','title','content') \
                    .annotate(read_num_sum=Sum('read_details__read_num')) \
                    .order_by('-read_num_sum')
    return blogs

def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog) #接收一个模型类或模型的实例，并返回表示该模型的ContentType实例　
    dates,read_nums = get_seven_days_read_data(blog_content_type)

    context = {}
    context['dates'] = dates
    context['read_nums'] = read_nums
    context['today_hot_data'] = get_today_hot_data(blog_content_type)
    context['yesterday_hot_data'] = get_yesterday_hot_data(blog_content_type)
    context['hot_blogs_for_7_days'] = get_seven_days_hot_blogs()
    return render(request,'home.html',context)
    
def search(request):
    redirect_to = request.GET.get('from', reverse('home'))
    search_words = request.GET.get('wd', '').strip()
    # 分词：按空格 & | ~
    condition = None
    for word in search_words.split(' '):
        if condition is None:
            condition = Q(title__icontains=word)
        else:
            condition = condition | Q(title__icontains=word)
    
    search_blogs = []
    if condition is not None:
        # 筛选：搜索
        search_blogs = Blog.objects.filter(condition)

    # 分页
    paginator = Paginator(search_blogs, 5)
    page_num = request.GET.get('page', 1) # 获取url的页面参数（GET请求）
    page_of_blogs = paginator.get_page(page_num)

    context = {}
    context['search_words'] = search_words
    context['search_blogs_count'] = search_blogs.count()
    context['page_of_blogs'] = page_of_blogs
    context['return_back_url'] = redirect_to
    return render(request, 'search.html', context)

def send_email(request):
    if request.method == 'POST':
        # 值1：  邮件标题   值2： 邮件主体
        # 值3： 发件人      值4： 收件人
        res = send_mail('关于中秋节放假通知',
                        '中秋节放三天假',
                        '1185127147@qq.com',
                        ['1185127147@qq.com'])
        if res == 1:
            return HttpResponse('邮件发送成功')
        else:
            return HttpResponse('邮件发送失败')
    else:
        return render(request, 'test.html')
