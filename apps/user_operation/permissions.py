# author: wp
# 2022年04月06日 16:06
from rest_framework import permissions


class IsOwnerOrNone(permissions.BasePermission):
    """
    查找/删除时，用户仅能操作他自己的收藏
    """

    def has_object_permission(self, request, view, obj):
        # IsOwnerOrReadOnly
        # # Read permissions are allowed to any request,
        # # so we'll always allow GET, HEAD or OPTIONS requests.
        # if request.method in permissions.SAFE_METHODS:
        #     return True

        # Instance must have an attribute named `owner`.
        return obj.user == request.user
