# author: wp
# 2022年04月06日 14:54
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import UserFav
from .models import UserLeavingMessage, UserAddress  # models前面不加.会报错
from goods.serializers import GoodsSerializer


class UserFavSerializer(serializers.ModelSerializer):
    # 使用隐藏字段的原因：用户收藏时，我们在后台直接获取对应用户即可，不需要每次收藏都让前端还把用户传递过来
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(), error_messages={
                                     "required": "匿名用户无法收藏"}
    )  # CurrentUserDefault()少写了个括号，debug了半个小时；不需要前端提交用户id，因为JWT token中带了

    class Meta:
        model = UserFav
        validators = [
            UniqueTogetherValidator(
                queryset=UserFav.objects.all(),
                fields=('user', 'goods'),
                message="已经收藏",
            )
        ]  # 用户不能重复收藏某个商品

        fields = ("user", "goods", "id")


class UserFavDetailSerializer(serializers.ModelSerializer):
    """
    用户收藏列表显示 序列化类
    """
    goods = GoodsSerializer()  # 嵌套关联

    class Meta:
        model = UserFav
        fields = ("goods", "id")


class LeavingMessageSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    # read_only的作用就是只返回，不提交，也就是post时不需要用户提交
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')

    class Meta:
        model = UserLeavingMessage
        fields = ("user", "message_type", "subject", "message", "file", "id", "add_time")  # 重名文件：序列化器会自动改别名


class AddressSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')

    class Meta:
        model = UserAddress
        fields = ("id", "user", "province", "city", "district", "address", "signer_name", "signer_mobile", "add_time")
