# -*- coding: utf-8 -*-

# 独立使用django的model

import django
import sys
import os


pwd = os.path.dirname(os.path.realpath(__file__))  # 获得当前路径
sys.path.append(pwd + "../")  # 将上一级路径，也就是系统搜索路径加入了上一级目录
# 将setting放入环境变量中，这一句和wsgi.py中的是一样的
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WpShop.settings')

django.setup()

from goods.models import GoodsCategory  # 注意这一句不能够放到上面去（比想象中重要），应该是在WpShop.settings有关于apps的设置

from db_tools.data.category_data import row_data

# allCategory= GoodsCategory.objects.all()  # 首先我们可以点击右键运行测试一下上面from是否OK
for lev1_cat in row_data:
    lev1_instance = GoodsCategory()  # 初始一个对象并赋值，赋值后save
    lev1_instance.code = lev1_cat["code"]
    lev1_instance.name = lev1_cat["name"]
    lev1_instance.category_type = 1
    lev1_instance.save()

    for lev2_cat in lev1_cat["sub_categorys"]:
        lev2_instance = GoodsCategory()
        lev2_instance.code = lev2_cat["code"]
        lev2_instance.name = lev2_cat["name"]
        lev2_instance.category_type = 2
        lev2_instance.parent_category = lev1_instance
        lev2_instance.save()

        for lev3_cat in lev2_cat["sub_categorys"]:
            lev3_instance = GoodsCategory()
            lev3_instance.code = lev3_cat["code"]
            lev3_instance.name = lev3_cat["name"]
            lev3_instance.category_type = 3
            lev3_instance.parent_category = lev2_instance
            lev3_instance.save()
