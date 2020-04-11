from django.urls import path
from .import views

urlpatterns = [
    path('<int:blog_pk>',views.blog_detail,name="blog_detail"),
    path('field_types/<int:field_type_pk>',views.home_to_coder_types,name='home_to_coder_types'),
    path('poetic_and_prose',views.poetic_and_prose,name='poetic_and_prose'),
    path('date/<int:year>/<int:month>',views.write_down_life,name='write_down_life'),
]