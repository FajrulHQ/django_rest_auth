"""
URL configuration for rest_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.shortcuts import redirect

from rest_framework import routers

from rest_framework.documentation import include_docs_urls
from rest_framework.permissions import AllowAny

from core.routers import routes as core_router

router = routers.SimpleRouter()
router.registry.extend(core_router.registry)

documentation = include_docs_urls(
        public=True,
        title="REST API",
        permission_classes=[AllowAny],
    )
urlpatterns = [
    path('', lambda request: redirect('/docs/'), name='root'),
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('docs/', documentation, name="docs"),
    # re_path('(^(?!(admin|docs)).*$)', documentation, name='index'),
]
