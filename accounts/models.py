from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

CONTENT_RATING_CHOICES = [
    ('G', 'G'),
    ('PG', 'PG'),
    ('PG-13', 'PG-13'),
    ('R', 'R'),
]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    city = models.CharField(max_length=128, blank=True, default="")
    state = models.CharField(max_length=64, blank=True, default="")
    region_code = models.CharField(max_length=64, blank=True, default="")  # e.g., "GA-Atlanta", "NY-NYC"
    max_content_rating = models.CharField(
        max_length=5,
        choices=CONTENT_RATING_CHOICES,
        default='R',
        blank=True,
    )
    def __str__(self):
        return f"Profile({self.user.username})"

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()
