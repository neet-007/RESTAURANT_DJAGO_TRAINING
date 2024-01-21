from rest_framework.permissions import BasePermission, SAFE_METHODS

class CartPermissions(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_admin or request.user.groups.filter(name__iexact='manager')
        return True

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_admin