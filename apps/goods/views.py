# from django.shortcuts import render

# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination

from goods.filters import GoodsFilter
from goods.models import Goods, GoodsCategory
from goods.serializers import GoodsSerializer, CategorySerializer


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
    pagination_class = GoodsPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filter_class = GoodsFilter

    search_fields = ['name', 'goods_brief', 'goods_desc']

    ordering_fields = ['sold_num', 'shop_price']


class CategoryViewset(viewsets.ReadOnlyModelViewSet):
    """
       list:
           商品分类列表数据
       retrieve:
           获取商品分类详情
    """
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = CategorySerializer