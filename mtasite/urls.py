from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', views.index, name="INDEX"),
    path('', views.mta_line, name="INDEX"),
    path('mta-line', views.mta_line, name="MTA-Line"),
    # path('about', views.about, name="MTA-About"),
    # path('service', views.service, name="MTA-Service"),
    # path('blog', views.blog, name="MTAblog"),
    # path('contact', views.contact, name="MTA-Contact"),
    # path('ajax/update/graph/', views.UpdateGraph.as_view(), name='update_graph'),
    path('ajax/update/graph/multiple', views.UpdateGraphMultiple.as_view(), name='update_graph_multiple'),
]