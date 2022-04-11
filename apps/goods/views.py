# from django.shortcuts import render

# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, mixins
# from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.filters import GoodsFilter
from goods.models import Goods, GoodsCategory, Banner
from goods.serializers import GoodsSerializer, CategorySerializer, BannerSerializer, IndexCategorySerializer


class GoodsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = "p"


class GoodsListViewSet(viewsets.ReadOnlyModelViewSet):
    """
    这么少的代码，实现了 商品列表，分页，搜索，过滤，排序
    """
    # def get_queryset(self):  # 内里原理，重写get_queryset方法
    #     queryset=Goods.objects.all() # 这里只是拼接了sql，并不会查询数据库所有数据
    #     price_min=self.request.query_params.get("price_min",0)
    #     if price_min:
    #         queryset=queryset.filter(shop_price__gt=int(price_min))
    #     return queryset
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer

    # authentication_classes = (TokenAuthentication,)
    pagination_class = GoodsPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filter_class = GoodsFilter

    search_fields = ['name', 'goods_brief', 'goods_desc']

    ordering_fields = ['sold_num', 'shop_price']

    # 重写retrieve方法：增加商品点击数
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.click_num += 1  # 对点击数加1并保存
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CategoryViewset(viewsets.ReadOnlyModelViewSet):
    """
       list:
           商品分类列表数据
       retrieve:
           获取商品分类详情
    """
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = CategorySerializer


class BannerViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    获取轮播图列表
    """
    queryset = Banner.objects.all().order_by("index")
    serializer_class = BannerSerializer


class IndexCategoryViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    首页商品分类数据（主要是序列化类写得复杂）
    """
    # is_tab等于True就是顶部的快捷标签显示那些，我们这里就显示那些
    queryset = GoodsCategory.objects.filter(is_tab=True, name__in=["生鲜食品", "酒水饮料"])
    serializer_class = IndexCategorySerializer
