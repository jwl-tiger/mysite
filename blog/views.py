import datetime
from django.shortcuts import render,get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from .models import Blog,BlogType
from read_statistics.utils import read_statistics_once_read
from comment.models import Comment 
from comment.forms import CommentForm
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
    return blogs[:6]

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
    #获取博客分类的对应博客数量
    #方法1：
    #BlogType.objects.annotate(blogtype_count=Count('blog'))
    #方法2：
    '''
    blog_types = BlogType.objects.all()
    blog_types_list = []
    for blog_type in blog_types:
        blog_type.blog_count = Blog.objects.filter(blog_type=blog_type).count()
        blog_types_list.append(blog_type)  
    '''
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

def home_to_coder(request):
    blogtypes_for_onepage = list(BlogType.objects.exclude(id=6).exclude(id=7).exclude(id=8).annotate(blogtype_count=Count('blog')))
    hot_comments = list(Comment.objects.all().order_by('-id'))
    hot_comments = hot_comments[:5]    
    someblogs_show = Blog.objects.filter(blog_type=blogtypes_for_onepage[0])
    context = get_blog_list_common_data(request,someblogs_show)
    context['blogtypes_for_onepage'] = blogtypes_for_onepage
    context['someblogs_show'] = someblogs_show
    context['hot_comments'] = hot_comments
    context['hot_blogs_for_7_days'] = get_seven_days_hot_blogs()
    return render(request,'blog/home_to_coder.html',context)

def home_to_coder_types(request,field_type_pk):
    blogtypes_for_onepage = list(BlogType.objects.exclude(id=6).exclude(id=7).exclude(id=8).annotate(blogtype_count=Count('blog')))
    someblogs_show_type = get_object_or_404(BlogType,id=field_type_pk)    
    hot_comments = list(Comment.objects.all().order_by('-id'))
    hot_comments = hot_comments[:5]    
    someblogs_show = Blog.objects.filter(blog_type=someblogs_show_type)
    context = get_blog_list_common_data(request,someblogs_show)
    context['blogtypes_for_onepage'] = blogtypes_for_onepage
    context['someblogs_show'] = someblogs_show
    context['hot_comments'] = hot_comments
    return render(request,'blog/field_types.html',context)

def poetic_and_prose(request):
    blogtypes_for_onepage = list(BlogType.objects.filter(id=6).annotate(blogtype_count=Count('blog')))
    blogs_for_onepage = Blog.objects.filter(blog_type=blogtypes_for_onepage[0])
    context = get_blog_list_common_data(request,blogs_for_onepage)
    return render(request,'blog/poetic_and_prose.html',context)

def write_down_life(request,year,month):
    blogs_for_onepage = Blog.objects.filter(create_time__year=year,create_time__month=month)
    context = get_blog_list_common_data(request,blogs_for_onepage)
    context['show_dates'] = "%s年%s月" % (year,month)
    return render(request,'blog/write_down_life.html',context)

def blog_detail(request,blog_pk): 

    blog = get_object_or_404(Blog, pk=blog_pk)
    read_cookie_key = read_statistics_once_read(request, blog)
    blog_content_type = ContentType.objects.get_for_model(blog)
    comments = Comment.objects.filter(content_type=blog_content_type, object_id=blog.pk, parent=None)

    context = {}
    context['previous_blog'] = Blog.objects.filter(create_time__gt=blog.create_time).last()
    context['next_blog'] = Blog.objects.filter(create_time__lt=blog.create_time).first()
    context['blog'] = blog
    context['comments'] = comments.order_by('-comment_time')
    context['comment_form'] = CommentForm(initial={'content_type': blog_content_type.model, 'object_id': blog_pk, 'reply_comment_id': 0})
    response = render(request, 'blog/blog_detail.html', context) # 响应
    response.set_cookie(read_cookie_key, 'true') # 阅读cookie标记
    return response
    '''
    blog = get_object_or_404(Blog,pk=blog_pk)
    read_cookie_key = read_statistics_once_read(request,blog)  # 某Blog实例对象的传入此方法的第一次，设计key对应到一个cookie，去标识这个对象
                                                            # 这样以后每次调用，只要那个cookie还在，就不会加一处理
    blog_content_type = ContentType.objects.get_for_model(blog)                                               
    comments = Comment.objects.filter(content_type=blog_content_type,object_id=blog.pk)    

    context = {}
    context['previous_blog'] = Blog.objects.filter(create_time__gt=blog.create_time).last()
    context['next_blog'] = Blog.objects.filter(create_time__lt=blog.create_time).first()
    context['blog'] = blog
    context['user'] = request.user
    context['comments'] = comments
    response= render(request,'blog/blog_detail.html',context) #每一个request（请求）对应一个response（响应）
    response.set_cookie(read_cookie_key,'true')     #阅读cookie的标记：
                                                    #第一次响应后设置一个标志性的cookie:通过response的set_cookie方法设置一个用特殊key值对应的cookie，响应之后保存在本地浏览器里
    return response   
    '''                              #每一次通过request请求服务器（后台程序）时，request可以把这个浏览器已保存的有效的cookie提交给服务器去检验，例如通过request.COOKIES.get方法去查
    

