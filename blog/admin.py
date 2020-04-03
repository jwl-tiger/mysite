from django.contrib import admin
from .models import BlogType,Blog


@admin.register(BlogType)
class BlogTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name','id',)
    ordering = ('id',)

@admin.register(Blog)    
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id','title','blog_type','author','get_read_num','create_time','last_updated_time')
    # ordering = ('id',) 
'''
@admin.register(ReadNum)
class BlogTypeAdmin(admin.ModelAdmin):
    list_display = ('read_num','blog')
    ordering = ('id',)
'''