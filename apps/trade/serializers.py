# author: wp
# 2022年04月07日 21:23
import time

from rest_framework import serializers

from WpShop.settings import private_key_path, ali_pub_key_path
from goods.serializers import GoodsSerializer
from goods.models import Goods
from utils.alipay import AliPay
from .models import ShoppingCart, OrderInfo, OrderGoods


class ShopCartDetailSerializer(serializers.ModelSerializer):
    """
    列表页使用的序列化类，显示商品详情
    """
    goods = GoodsSerializer(many=False, read_only=True)  # 嵌套关联；many=True时会报错：'Goods' object is not iterable

    class Meta:
        model = ShoppingCart
        fields = ("goods", "nums")


class ShopCartSerializer(serializers.Serializer):
    """
    个性化设计字段
    """
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    nums = serializers.IntegerField(required=True, label="数量", min_value=1,
                                    error_messages={
                                        "min_value": "商品数量不能小于1",
                                        "required": "请选择购买数量"
                                    })
    goods = serializers.PrimaryKeyRelatedField(required=True, queryset=Goods.objects.all())

    def create(self, validated_data):
        """
        向购物车中添加商品
        :param validated_data:
        :return:
        """
        # 在序列化类中通过self.context["request"]就可以拿到request对象
        user = self.context["request"].user
        nums = validated_data["nums"]
        goods = validated_data["goods"]

        # 理解该变量
        existed = ShoppingCart.objects.filter(user=user, goods=goods)

        if existed:  # 购物车中原本已经有了，就修改数量，而不是新增一条资料
            existed = existed[0]  # 这一步是为什么
            existed.nums += nums
            existed.save()
        else:
            existed = ShoppingCart.objects.create(**validated_data)

        return existed

    def update(self, instance, validated_data):
        """
        修改购物车中的商品数量，前端直接传输过来最终数目
        :param instance:
        :param validated_data:
        :return:
        """
        instance.nums = validated_data["nums"]
        instance.save()
        return instance


class OrderSerializer(serializers.ModelSerializer):
    """
    订单序列化类
    """
    # 用户信息默认不用提交，因为我们已经登录，当然知道谁提交订单
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    # 订单号每次生成
    def generate_order_sn(self):
        # 当前时间+userid+随机数
        from random import Random
        random_ins = Random()
        order_sn = "{time_str}{userid}{ranstr}".format(time_str=time.strftime("%Y%m%d%H%M%S"),
                                                       userid=self.context["request"].user.id,
                                                       ranstr=random_ins.randint(10, 99))

        return order_sn

    def validate(self, attrs):
        """
        页面不需要提交某个字段，但是后端通过代码来生成这个字段的操作
        :param attrs:
        :return:
        """
        attrs["order_sn"] = self.generate_order_sn()
        return attrs

    alipay_url = serializers.SerializerMethodField(read_only=True)

    def get_alipay_url(self, obj):
        """
        前端拿到支付宝支付链接
        :param obj:
        :return:
        """
        server_ip = "34.210.197.159"  # 云服务器公网IP
        alipay = AliPay(
            appid="2021000119658870",
            # app_notify_url="http://127.0.0.1:8000/alipay/return/",
            app_notify_url="http://" + server_ip + ":8000/alipay/return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用
            debug=True,  # 默认False
            return_url="http://" + server_ip + ":8000/alipay/return/"
        )

        url = alipay.direct_pay(
            subject=obj.order_sn,
            out_trade_no=obj.order_sn,
            total_amount=obj.order_mount,
        )
        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)

        return re_url  # 没有将这个url存到表里，但前端需要时后端可以提供

    class Meta:
        model = OrderInfo
        fields = "__all__"


# 用来显示订单详情中的商品详情
class OrderGoodsDetailSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)  # 一个商品id只会对应一件商品

    class Meta:
        model = OrderGoods
        fields = "__all__"


# 用来显示订单详情
class OrderDetailSerializer(serializers.ModelSerializer):
    goods = OrderGoodsDetailSerializer(many=True)  # 一个订单id可以有多个商品

    # 同上。因为在Detail下面也有个支付按钮，所以也要在该序列化类下写以下方法
    # SerializerMethodField？ get+字段名称  字段得到的值就是以下get_alipay_url方法返回的值；该字段不需要在数据库中有，model类中可以没有
    alipay_url = serializers.SerializerMethodField(read_only=True)

    def get_alipay_url(self, obj):
        """
        前端拿到支付宝支付链接（生成url的方法）
        :param obj:
        :return:
        """
        server_ip = "34.210.197.159"  # 云服务器公网IP
        alipay = AliPay(
            appid="2021000119658870",
            # app_notify_url="http://127.0.0.1:8000/alipay/return/",
            app_notify_url="http://" + server_ip + ":8000/alipay/return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用
            debug=True,  # 默认False
            return_url="http://" + server_ip + ":8000/alipay/return/"
        )

        url = alipay.direct_pay(
            subject=obj.order_sn,
            out_trade_no=obj.order_sn,
            total_amount=obj.order_mount,
        )
        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)

        return re_url  # 没有将这个url存到表里，但前端需要时后端可以提供

    class Meta:
        model = OrderInfo
        fields = "__all__"
