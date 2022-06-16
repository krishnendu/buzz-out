"""ChatApi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.authtoken import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView

urlpatterns = [
    path('djangoadmin/', admin.site.urls),
    path('api/v1/', include('ChatApi.routers')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('', TemplateView.as_view(template_name="react_home.html")),
    # re_path(r'^chat/?$', TemplateView.as_view(template_name="react_home.html")),
    # re_path(r'^signup/?$', TemplateView.as_view(template_name="react_home.html")),
    # re_path(r'^crypto/?$', TemplateView.as_view(template_name="react_home.html")),
    # re_path(r'^forget-password/(?P<token>[0-9a-f]{12}4[0-9a-f]{3}[89ab][0-9a-f]{15}\Z)/?$', TemplateView.as_view(template_name="react_home.html")),
    # re_path(r'^404/?$', TemplateView.as_view(template_name="react_home.html")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += static(settings.REACT_URL, document_root=settings.REACT_ROOT)

handler404 = TemplateView.as_view(template_name="react_home.html")