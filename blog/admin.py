from django.contrib import admin
from .models import BlogType,Blog


@admin.register(BlogType)
class BlogTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name','id',)
    ordering = ('id',)



@admin.register(Blog)    
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id','title','blog_type','author','get_read_num','create_time','last_updated_time','status')

    actions = ['make_published']

    def make_published(self, request, queryset):
        rows_updated = queryset.update(status='p')
        if rows_updated == 1:
            message_bit = "1 篇文章"
        else:
            message_bit = "%s 篇文章" % rows_updated
        self.message_user(request,"%s 已被成功发表" % message_bit)
    make_published.short_description = "Mark as published"
    # ordering = ('id',) 

# class BlogAdmin(admin.ModelAdmin):
#     list_display = ('id','title','blog_type')
# admin.site.register(Blog,BlogAdmin) #初始,的模型 register method
