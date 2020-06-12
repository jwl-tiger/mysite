import datetime
from random import sample
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum,Q
from django.core.cache import cache
from django.urls import reverse
from blog.models import Blog,BlogType
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Count
from read_statistics.utils import read_statistics_once_read
from comment.models import Comment 

def get_seven_days_hot_blogs():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects.filter(read_details__date__lt=today,read_details__date__gte=date) \
                    .values('id','title','content') \
                    .annotate(read_num_sum=Sum('read_details__read_num')) \
                    .order_by('-read_num_sum')
    six_hot_blogs = []
    for blog in blogs:
        six_hot_blogs.append(blog)
    return blogs[:5]

def random_blogs():
    blogs = Blog.objects.all()
    blogs = list(blogs)
    return sample(blogs, 5)

def get_blog_list_common_data(request,blogs_for_onepage):
    paginator = Paginator(blogs_for_onepage,settings.EACH_PAGE_BLOGS_NUMBER) #  每N页进行分页
    page_num = request.GET.get('page',1) #获取页码参数（GET请求）
    page_of_blogs = paginator.get_page(page_num)
    current_page_num = page_of_blogs.number #获取当前页码
    #获取当前页码以及前两页和后两页
    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
               list(range(current_page_num,min(current_page_num +2 ,paginator.num_pages) + 1))
    
    #加上省略页码标记
    if page_range[0] - 1 >=2:
        page_range.insert(0,'...')
    if paginator.num_pages - page_range[-1] >=2:
        page_range.append('...')

    #加上首页和尾页
    if page_range[0] != 1:
        page_range.insert(0,1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)  
    
    blog_dates = Blog.objects.dates('create_time','month',order='DESC')
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(create_time__year=blog_date.year,
                                       create_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count

    context = {}
    context['page_of_blogs'] = page_of_blogs #获取的页
    context['page_range'] = page_range #根据需求筛选出的要显示的滚动条对应具体的页码值列表
    context['blog_dates'] = blog_dates_dict #日期                                         
    return context

def home(request):
    coder_types = list(BlogType.objects.exclude(id=6).exclude(id=7).exclude(id=8).annotate(blogtype_count=Count('blog')))
    blogs = Blog.objects.filter(status="p")
    hot_blogs = get_seven_days_hot_blogs() 
    randoms = random_blogs()
    hot_comments = list(Comment.objects.all().order_by('-id'))
    hot_comments = hot_comments[:5]
    context = get_blog_list_common_data(request,blogs)
    context['coder_types'] = coder_types
    context['blogs'] = blogs
    context['hot_blogs'] = hot_blogs
    context['hot_comments'] = hot_comments
    context['random_blogs'] = randoms
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

# from django.core.mail import send_mail, send_mass_mail, EmailMultiAlternatives
# from django.conf import settings

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
