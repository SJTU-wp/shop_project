# author: wp
# 2022年04月06日 17:36
from rest_framework import permissions


class IsOwnerOrNone(permissions.BasePermission):
    """
    用户仅能操作他自己的用户信息详情页
    """

    def has_object_permission(self, request, view, obj):
        # IsOwnerOrReadOnly
        # # Read permissions are allowed to any request,
        # # so we'll always allow GET, HEAD or OPTIONS requests.
        # if request.method in permissions.SAFE_METHODS:
        #     return True

        # Instance must have an attribute named `owner`.
        return obj == request.user  # 困惑
