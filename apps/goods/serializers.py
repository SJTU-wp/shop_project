# author: wp
# 2022年04月04日 22:37
from rest_framework import serializers

from goods.models import Goods, GoodsCategory


class GoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = '__all__'


# 最底层的类
class CategorySerializer3(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = "__all__"


class CategorySerializer2(serializers.ModelSerializer):
    sub_cat = CategorySerializer3(many=True)  # 序列化字段名字必须是模型类中的parent_category

    class Meta:
        model = GoodsCategory
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    sub_cat = CategorySerializer2(many=True)  # 嵌套关联

    class Meta:
        model = GoodsCategory
        fields = "__all__"
