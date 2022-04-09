# -*- coding: utf-8 -*-

# pip install pycryptodome


from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
from urllib.parse import quote_plus
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen
from base64 import decodebytes, encodebytes

import json


class AliPay(object):
    """
    支付宝支付接口
    """
    def __init__(self, appid, app_notify_url, app_private_key_path,
                 alipay_public_key_path, return_url, debug=False):
        self.appid = appid  # 支付宝分配给开发者的应用ID
        self.app_notify_url = app_notify_url  # 回调url
        self.app_private_key_path = app_private_key_path
        self.app_private_key = None
        self.return_url = return_url
        # 读取我们的私钥和alipay的公钥
        with open(self.app_private_key_path) as fp:
            self.app_private_key = RSA.importKey(fp.read())

        self.alipay_public_key_path = alipay_public_key_path
        with open(self.alipay_public_key_path) as fp:
            self.alipay_public_key = RSA.import_key(fp.read())

        if debug is True:
            self.__gateway = "https://openapi.alipaydev.com/gateway.do"
        else:
            self.__gateway = "https://openapi.alipay.com/gateway.do"

    def direct_pay(self, subject, out_trade_no, total_amount, return_url=None, **kwargs):
        # 这里和官方文档中请求参数的必填写项次一样的
        biz_content = {
            "subject": subject,
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "product_code": "FAST_INSTANT_TRADE_PAY",
            # "qr_pay_mode":4
        }

        biz_content.update(kwargs)
        data = self.build_body("alipay.trade.page.pay", biz_content, self.return_url)
        return self.sign_data(data)

    # 这里和我们公共请求参数一样的
    def build_body(self, method, biz_content, return_url=None):
        data = {
            "app_id": self.appid,
            "method": method,
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }

        if return_url is not None:
            data["notify_url"] = self.app_notify_url
            data["return_url"] = self.return_url

        return data

    # 签名，所有的支付宝请求都需要签名
    def sign_data(self, data):
        # 如果data中有sign这个字段我们先清除
        data.pop("sign", None)
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        unsigned_string = "&".join("{0}={1}".format(k, v) for k, v in unsigned_items)
        sign = self.sign(unsigned_string.encode("utf-8"))
        # ordered_items = self.ordered_data(data)
        # quote_plus主要是针对含有冒号双斜杠等进行处理
        quoted_string = "&".join("{0}={1}".format(k, quote_plus(v)) for k, v in unsigned_items)

        # 把sign加上，获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    def ordered_data(self, data):
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将字典类型的数据dump出来
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))

        return sorted([(k, v) for k, v in data.items()])

    # 按照支付宝官方给的手法签名
    def sign(self, unsigned_string):
        # 开始计算签名
        key = self.app_private_key
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(SHA256.new(unsigned_string))
        # base64 编码，转换为unicode表示并移除回车
        sign = encodebytes(signature).decode("utf8").replace("\n", "")
        return sign

    def _verify(self, raw_content, signature):
        # 开始计算签名，使用阿里给我们的公钥，对阿里返回的签名是否正确
        key = self.alipay_public_key
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new()
        digest.update(raw_content.encode("utf8"))
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False

    def verify(self, data, signature):
        if "sign_type" in data:
            sign_type = data.pop("sign_type")
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)
        return self._verify(message, signature)


# 测试代码
# 拿到支付宝返回给我们的url，进行解析，为了防止黑客截获
if __name__ == "__main__":
    IP = "34.210.197.159:8000"  # 云服务器公网IP
    return_url = 'http://'+IP+'/alipay/return/?charset=utf-8&out_trade_no=20230515163741149&method=alipay.trade.page.pay.return&total_amount=100.00&sign=LoPTydwRUOY6uY6NbBOMxQmRT%2BWb2jRrX6v6WiaHcKeD%2F%2FqoPrU4D1yqOjz9DbAwC0nsZeFfJES4er20CZc5uO%2B%2BVuaOS5tfcZTPkdM3dXQOHz5J7lGX9N8u1ht8mLXxxjD5J0SpXSbTfKW2qwGTpnxqp8wmDETEYbL0DunZZaeTm9IrOG0MkJjPH0uTCD0WEe4ThklPnRsYfHhHJRpAbnqezIcd8MJtq6ERXTMsxTrLtgXGKMphTA057f8VMSY%2FEPb3PTPb12KNPU0TZrWEXf0e7LjSJ5J5ObW9ErKRbPFDM%2FmF5tnY9Hpl0OH1wnhbW1%2BB4iTpwYUNSb2AKNeSqA%3D%3D&trade_no=2022040922001406620502150308&auth_app_id=2021000119658870&version=1.0&app_id=2021000119658870&sign_type=RSA2&seller_id=2088621958281329&timestamp=2022-04-09+16%3A24%3A06'
    o = urlparse(return_url)
    query = parse_qs(o.query)
    processed_query = {}
    ali_sign = query.pop("sign")[0]

    # body parts
    alipay = AliPay(
        appid="2021000119658870",  # 放入自己的应用ID
        app_notify_url="http://"+IP+"/alipay/return/",  # 异步的请求接收接口，就是用户扫描后，没支付，然后再次打开支付宝去支付
        app_private_key_path="../trade/keys/private_2048",
        alipay_public_key_path="../trade/keys/alipay_key_2048",  # 支付宝的公钥，验证支付宝回传消息使用，注意不是自己的公钥
        debug=True,  # 默认False
        return_url="http://"+IP+"/alipay/return/"
    )

    for key, value in query.items():
        processed_query[key] = value[0]
    print(alipay.verify(processed_query, ali_sign))

    url = alipay.direct_pay(
        subject="20230515163741149",  # 自己的订单ID
        out_trade_no="20230515163741149",  # 测试时可以随便写一个测试用
        total_amount=100,
        return_url="http://"+IP+"/alipay/return/"  # 支付完成后跳回的页面
    )  # 我们要把这个url拿到我们的alipay的url中
    re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)

    print(re_url)
