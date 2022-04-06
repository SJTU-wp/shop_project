# from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated

from .models import UserFav, UserLeavingMessage
from .permissions import IsOwnerOrNone
from .serializers import UserFavSerializer, UserFavDetailSerializer, LeavingMessageSerializer


# 添加收藏，删除收藏；ListModelMixin是列表页的get，RetrieveModelMixin是详情页的get
class UserFavViewset(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    用户收藏功能
    list: 获取用户收藏列表
    retrieve: 获取用户收藏信息（判断某个商品是否已经收藏），当前设置并未显示详细信息
    create: 收藏商品
    """
    queryset = UserFav.objects.all()  # 查询数据集合，任何类都要拿到数据才能操作
    # serializer_class = UserFavSerializer  # 序列化类；修改为：先判断，再选取相应的序列化器

    permission_classes = (IsAuthenticated, IsOwnerOrNone, )

    lookup_field = "goods_id"  # 修改默认，传递商品id

    # 重载get_queryset方法
    def get_queryset(self):
        """
        让每个人只看到自己的收藏（比设置权限更牛逼）
        :return:
        """
        return UserFav.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """
        操作分流
        :return: 对应的序列化器
        """
        if self.action == "list":
            return UserFavDetailSerializer  # 获取用户收藏列表
        # elif self.action == "create":
        #     return UserFavSerializer

        return UserFavSerializer


class LeavingMessageViewset(mixins.ListModelMixin, mixins.CreateModelMixin,
                            mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    list: 获取用户留言
    create: 添加留言
    delete: 删除留言
    """
    permission_classes = (IsAuthenticated, IsOwnerOrNone)
    serializer_class = LeavingMessageSerializer

    def get_queryset(self):
        """
        让每个人只看到自己的留言
        :return:
        """
        return UserLeavingMessage.objects.filter(user=self.request.user)
