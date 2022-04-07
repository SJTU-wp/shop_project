from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, mixins
from trade.models import ShoppingCart, OrderInfo, OrderGoods
from rest_framework.permissions import IsAuthenticated
from trade.serializers import ShopCartSerializer, ShopCartDetailSerializer, OrderSerializer, OrderDetailSerializer
from utils.permissions import IsOwnerOrReadOnly


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
        order_amount = 0
        for shop_cart in shop_carts:
            order_goods = OrderGoods()
            order_goods.goods = shop_cart.goods
            order_goods.goods_num = shop_cart.nums
            order_amount += order_goods.goods.shop_price * shop_cart.nums
            order_goods.order = order
            # 订单商品信息保存
            order_goods.save()
            # 清空购物车
            shop_cart.delete()

        # 把我们自己算出的订单金额保存进去——防黑客攻击，传递虚假金额
        print(order_amount)
        order.order_amount = order_amount
        order.save()

        return order
