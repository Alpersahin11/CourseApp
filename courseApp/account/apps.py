from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_groups(sender, **kwargs):
    from django.contrib.auth.models import Group, Permission
    teacher_group, created = Group.objects.get_or_create(name='Teacher')
    student_group, created = Group.objects.get_or_create(name='Student')

    add_course_perm = Permission.objects.get(codename='add_course')
    teacher_group.permissions.add(add_course_perm)

    delete_course_perm = Permission.objects.get(codename='delete_course')
    teacher_group.permissions.add(delete_course_perm)

    change_course_perm = Permission.objects.get(codename='change_course') 
    teacher_group.permissions.add(change_course_perm)

class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'

    def ready(self):
        post_migrate.connect(create_groups, sender=self)