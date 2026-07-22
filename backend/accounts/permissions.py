from rest_framework import permissions

class IsResponsible(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # It only allows it if the user is on the list of responsible parties.
        return request.user in obj.responsible.all()
