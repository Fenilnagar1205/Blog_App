from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):

    # 1. Pure View/Request level par checking
    def has_permission(self, request, view):
        # User ka logged-in hona compulsory hai
        return request.user and request.user.is_authenticated

    # 2. Specific object (jaise Blog id=5) ke level par checking
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Condition A: Kya request karne wala admin/staff hai?
        if request.user.is_staff:
            return True

        # Condition B: Kya request karne wala hi is object ka owner/author hai?
        # Note: 'author' ki jagah aapke model me jo bhi field name hai (like 'user'), wo likhein
        return obj.author == request.user
