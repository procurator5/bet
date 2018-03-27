from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django_bitcoin.models import Wallet, currency

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)
    wallet = models.ForeignKey("django_bitcoin.Wallet", on_delete=models.DO_NOTHING, null=True)
    # this is not needed if small_image is created at set_image
    def save(self, *args, **kwargs):
        self.wallet, created = Wallet.objects.get_or_create(label=self.user.username)
        recv_address = self.wallet.receiving_address(fresh_addr=False)
        super(Profile, self).save(*args, **kwargs)
        
@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save() 
    