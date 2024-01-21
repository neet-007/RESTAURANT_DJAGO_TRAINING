from rest_framework.permissions import BasePermission, SAFE_METHODS

class CanManageStaff(BasePermission):
    message = 'You are not authrized for this view'

    def has_permission(self, request, view):
        return request.user.groups.filter(name__iexact='manager').exists() or request.user.is_admin