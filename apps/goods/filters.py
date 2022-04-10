# author: wp
# 2022年04月04日 22:56
from django_filters import rest_framework as filters

from goods.models import Goods


class GoodsFilter(filters.FilterSet):
    """商品过滤，价格区间、名字"""
    min_price = filters.NumberFilter(field_name="shop_price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="shop_price", lookup_expr='lte')
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')  # contains代表包含，i代表不区分大小写

    class Meta:
        model = Goods
        fields = ['min_price', 'max_price', 'name', 'is_hot', 'is_new']
