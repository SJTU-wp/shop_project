# from django.shortcuts import render

# Create your views here.
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response

from .models import VerifyCode

User = get_user_model()


class CustomBackend(ModelBackend):
    """
    自定义用户验证，既可以用用户名，也用手机号登录
    """
    # 重写authenticate方法
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(mobile=username))  # 用户名或手机号均可作为用户名登录
            if user.check_password(password):
                return user
        except Exception as e:
            return None


from .serializers import UserRegSerializer, SmsSerializer
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler


class UserViewset(CreateModelMixin, viewsets.GenericViewSet):
    """
    用户
    """
    serializer_class = UserRegSerializer

    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        """
        新增后默认的给用户的返回是序列化类中的fields决定的，当你需要改变返回的效果时，重写create
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        # 拿到serializer.data然后将name和token填写进去
        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        re_dict["token"] = jwt_encode_handler(payload)  # 这步就做好了header，payload，签名
        re_dict["name"] = user.name if user.name else user.username

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)


from random import choice
from WpShop.settings import APIKEY
from utils.yunpian import YunPian


class SmsCodeViewset(CreateModelMixin, viewsets.GenericViewSet):
    """
    发送短信验证码
"""
# 设置序列化类
    serializer_class = SmsSerializer

    # 产生随机数
    def generate_code(self):
        """
        生成四位数字的验证码
        :return:
        """
        seeds = "1234567890"
        random_str = []
        for i in range(4):
            random_str.append(choice(seeds))

        return "".join(random_str)

    # 重写CreateModelMixin的create方法
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # 这里如果raise_exception设置为True，那么如果序列化过程中发生异常，那么会自动帮我们给客户端返回400异常，比较方便
        serializer.is_valid(raise_exception=True)
        # 拿到手机号
        mobile = serializer.validated_data["mobile"]

        yun_pian = YunPian(APIKEY)
        # 生产随机验证码
        code = self.generate_code()
        # 发送短信
        sms_status = yun_pian.send_sms(code=code, mobile=mobile)
        # 云片网的响应，返回0代表成功
        if sms_status["code"] != 0:
            return Response({
                "mobile": sms_status["msg"]
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 保存验证码
            code_record = VerifyCode(code=code, mobile=mobile)
            code_record.save()
            return Response({
                "mobile": mobile
            }, status=status.HTTP_201_CREATED)
