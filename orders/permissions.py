from rest_framework.permissions import BasePermission, SAFE_METHODS

class OrderPermission(BasePermission):
  
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True  
        if request.method == 'POST':
            
            is_buyer = not user.is_staff and getattr(user, 'role', None) != 'producer'
            return is_buyer
        if request.method in ['PUT', 'PATCH']:
            return user.is_staff or getattr(user, 'role', None) == 'producer'
        if request.method == 'DELETE':
            return False  
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class WasteClaimPermission(BasePermission):
  
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'POST':
            return getattr(user, 'role', None) == 'recycler'
        if request.method in ['PUT', 'PATCH']:
            return user.is_staff or getattr(user, 'role', None) == 'producer'
        if request.method == 'DELETE':
            return False
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
