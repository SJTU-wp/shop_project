"""WpShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, re_path, include
from django.views.generic import TemplateView
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token

import xadmin
from goods.views import GoodsListViewSet, CategoryViewset, BannerViewset, IndexCategoryViewset
from trade.views import ShoppingCartViewset, OrderViewset, AlipayView
from user_operation.views import UserFavViewset, LeavingMessageViewset, AddressViewset
from users.views import UserViewset, SmsCodeViewset

xadmin.autodiscover()
from xadmin.plugins import xversion
xversion.register_models()

from WpShop.settings import MEDIA_ROOT
from django.views.static import serve
from rest_framework.documentation import include_docs_urls

router = DefaultRouter()
router.register(r'goods', GoodsListViewSet, base_name='goods')
router.register(r'categorys', CategoryViewset, base_name="categorys")
router.register(r'users', UserViewset, base_name="users")
router.register(r'codes', SmsCodeViewset, base_name="codes")
router.register(r'userfavs', UserFavViewset, base_name="userfavs")
router.register(r'messages', LeavingMessageViewset, base_name="messages")
# 用户地址
router.register(r'address', AddressViewset, base_name="address")
# 购物车url
router.register(r'shopcarts', ShoppingCartViewset, base_name="shopcarts")
# 订单相关url
router.register(r'orders', OrderViewset, base_name="orders")
# 轮播功能
router.register(r'banners', BannerViewset, base_name="banners")
# 首页商品系列数据
router.register(r'indexgoods', IndexCategoryViewset, base_name="indexgoods")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('xadmin/', xadmin.site.urls),
    # 下面的配置是为了django支持静态资源图片的加载
    re_path(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    path('api-auth/', include('rest_framework.urls')),
    re_path(r'^api-token-auth/', views.obtain_auth_token),  # 理解token，向这个url post我们的用户名和密码就会返回我们的token
    path('login/', obtain_jwt_token),  # 理解jwt
    path('docs/', include_docs_urls(title="我的商城")),  # drf的api文档自动生成
    re_path(r'^alipay/return/', AlipayView.as_view(), name="alipay"),
    # 简单发布后用户访问到的首页
    re_path(r'^index/', TemplateView.as_view(template_name="index.html"), name="index"),
    path('', include(router.urls)),
]
