from django.shortcuts import redirect

# Create your views here.
from rest_framework import viewsets, mixins
from trade.models import ShoppingCart, OrderInfo, OrderGoods
from rest_framework.permissions import IsAuthenticated
from trade.serializers import ShopCartSerializer, ShopCartDetailSerializer, OrderSerializer, OrderDetailSerializer
from utils.permissions import IsOwnerOrReadOnly
from rest_framework.views import APIView


class ShoppingCartViewset(viewsets.ModelViewSet):
    """
    购物车功能
    list:
        获取购物车详情
    create：
        加入购物车
    delete：
        删除购物记录
    """
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    # queryset = ShoppingCart.objects.all()  # 不合理：不同用户均可以看到全部用户的购物车
    serializer_class = ShopCartSerializer  # 此句实际上已失效

    lookup_field = "goods_id"  # 为查询，修改，删除提供的id，默认是主键，现在改变了

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return ShopCartDetailSerializer
        else:
            return ShopCartSerializer


class OrderViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin, mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """
    订单管理
    list:
        获取个人订单
    delete:
        删除订单
    create：
        新增订单
    """
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    serializer_class = OrderSerializer  # 要失效了，后面有重写xx方法

    def get_queryset(self):
        """
        每个人只能看到自己的订单
        :return:
        """
        return OrderInfo.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderDetailSerializer
        return OrderSerializer

    # perform_create用于对我们的实例进行修改
    def perform_create(self, serializer):
        order = serializer.save()
        # 拿到购物车中的信息
        shop_carts = ShoppingCart.objects.filter(user=self.request.user)
        # 遍历购物车
        order_mount = 0
        for shop_cart in shop_carts:
            order_goods = OrderGoods()
            order_goods.goods = shop_cart.goods
            order_goods.goods_num = shop_cart.nums
            order_mount += order_goods.goods.shop_price * shop_cart.nums
            order_goods.order = order
            # 生成订单的时候，库存要减去相应数量
            order_goods.goods.goods_num -= order_goods.goods_num
            # 订单商品信息保存
            order_goods.save()
            # 清空购物车
            shop_cart.delete()

        # 把我们自己算出的订单金额保存进去——防黑客攻击，传递虚假金额
        print(order_mount)
        order.order_mount = order_mount
        order.save()

        return order

    # 删除订单，库存恢复
    def perform_destroy(self, instance):
        goods = instance.goods
        goods.goods_num += instance.goods_num
        goods.save()
        instance.delete()

    # 订单设置不允许修改


from utils.alipay import AliPay
from WpShop.settings import ali_pub_key_path, private_key_path
from rest_framework.response import Response
from datetime import datetime


class AlipayView(APIView):
    """
    验签部分代码：可复用
    """
    server_ip = "34.210.197.159:8000"  # 云服务器公网IP
    alipay = AliPay(
        appid="2021000119658870",
        # app_notify_url="http://127.0.0.1:8000/alipay/return/",
        app_notify_url="http://" + server_ip + "/alipay/return/",
        app_private_key_path=private_key_path,
        alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，注意不是自己的公钥
        debug=True,  # 默认False，True为开发者模式
        return_url="http://" + server_ip + "/alipay/return/"
    )  # 生成对象，直接将其作为类属性

    def get(self, request):
        """
        处理支付宝的return_url返回
        :param request:
        :return:
        """
        processed_dict = {}
        for key, value in request.GET.items():  # 同步请求的消息在GET里面
            processed_dict[key] = value

        sign = processed_dict.pop("sign", None)

        verify_re = self.alipay.verify(processed_dict, sign)  # 验签，类似alipay.py中的相应部分
        # 这里可以调试看一下，如果verify_re为真，说明验证成功
        if verify_re is True:
            # 为什么注释掉这一部分？这是未改版前的支付宝，现在：支付宝的同步请求(get)不再含有支付成功的状态信息
            # order_sn = processed_dict.get('out_trade_no', None)  # 订单号
            # trade_no = processed_dict.get('trade_no', None)  # 支付宝交易号
            # trade_status = processed_dict.get('trade_status', None)  # 交易状态
            #
            # existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
            # for existed_order in existed_orders:
            #     existed_order.pay_status = trade_status  # 更新交易状态
            #     existed_order.trade_no = trade_no
            #     existed_order.pay_time = datetime.now()
            #     existed_order.save()

            # 验签通过，订单没支付？跳转到支付页面
            response = redirect("/index/#/app/home/member/order")
            # response.set_cookie("nextPath","pay", max_age=3)
            return response
        else:
            # 验签不通过，订单支付？跳转到首页
            response = redirect("/index")
            return response

    def post(self, request):
        """
        处理支付宝的notify_url，异步的，支付宝发过来的是post请求
        :param request:
        :return:
        """
        processed_dict = {}

        for key, value in request.POST.items():  # 异步请求的消息在POST里面
            processed_dict[key] = value

        sign = processed_dict.pop("sign", None)

        verify_re = self.alipay.verify(processed_dict, sign)

        if verify_re is True:
            order_sn = processed_dict.get('out_trade_no', None)  # 我们的订单，订单号为什么赋了out_trade_no呢？
            trade_no = processed_dict.get('trade_no', None)  # 阿里那边会随机生成一个交易号
            trade_status = processed_dict.get('trade_status', None)  # 交易状态

            existed_orders = OrderInfo.objects.filter(order_sn=order_sn)

            for existed_order in existed_orders:
                # 一旦订单完成支付，我们查询订单中的所有商品，对商品销量进行增加
                order_goods = existed_order.goods.all()
                for order_good in order_goods:
                    goods = order_good.goods
                    # 支付后，销量增加
                    goods.sold_num += order_good.goods_num
                    goods.save()

                existed_order.pay_status = trade_status
                existed_order.trade_no = trade_no
                existed_order.pay_time = datetime.now()
                existed_order.save()

            return Response("success")  # 要给阿里response一个success，否则它会一直给我们消息
