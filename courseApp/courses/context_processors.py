def group_check(request):
    user = request.user
    return {
        'is_teacher': user.is_authenticated and user.groups.filter(name='Teacher').exists(),
        'is_superuser': user.is_authenticated and user.is_superuser,
    }