from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User, Group, Permission
from .models import Profile

@receiver(post_save, sender=User)
def create_profile_and_add_group(sender, instance, created, **kwargs):
    # Profil varsa oluşturma, yoksa oluştur
    profile, created_profile = Profile.objects.get_or_create(user=instance)
    
    if created_profile:
        try:
            student_group = Group.objects.get(name='Student')
            instance.groups.add(student_group)
        except Group.DoesNotExist:
            pass

@receiver(post_migrate)
def create_groups(sender, **kwargs):
    teacher_group, _ = Group.objects.get_or_create(name='Teacher')
    student_group, _ = Group.objects.get_or_create(name='Student')

    perms = ['add_course', 'delete_course', 'change_course']
    for codename in perms:
        try:
            perm = Permission.objects.get(codename=codename)
            teacher_group.permissions.add(perm)
        except Permission.DoesNotExist:
            pass
