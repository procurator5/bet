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
        
    def history(self):
        dict = []
        sql ="""
       with last_state AS(
  select t.id AS tipp_id, max(ts.id) as id  from tippspiel_tipp t
  join tippspiel_tippstate ts ON ts.tipp_id = t.id
  GROUP BY t.id
  
)
SELECT 'in' as class, dt.amount, dt.created_at as time, 'Зачисление&nbsp;-&nbsp;<span class="status">Обработан</span>' as bettitle, 
    dt.txid as paymentid, NULL as bettype, NULL as betchoice
  FROM public.django_bitcoin_wallettransaction bwt
  JOIN django_bitcoin_deposittransaction dt ON bwt.deposit_transaction_id = dt.id
  JOIN bbil_profile p ON bwt.to_wallet_id = p.wallet_id
  WHERE user_id = 12
UNION
  select 
    CASE WHEN ts.state = 'InGame' OR ts.state = 'Lose' THEN 'non' ELSE 'in' END AS class,
    CASE WHEN ts.state = 'InGame' OR ts.state = 'Lose' THEN -bwt.amount ELSE bwt.amount END AS amount,
    bwt.created_at as time,
    home.name || ' - ' || visitor.name AS bettitle,
    NULL paymentid,
    bg.bet_name AS bettype,
    bt.bet_choice as betchoice
  from tippspiel_tipp t
  join bbil_profile p ON t.player_id = p.user_id
  join last_state ls ON ls.tipp_id = t.id
  join tippspiel_tippstate ts ON ls.id = ts.id
  join django_bitcoin_wallettransaction bwt ON bwt.id = ts.transaction_id
  join tippspiel_match m on t.match_id = m.id
  join tippspiel_team home ON home.id = m.team_home_id
  join tippspiel_team visitor ON visitor.id = m.team_visitor_id
  join tippspiel_bettype bt ON bt.id = t.bet_id
  JOIN tippspiel_betgroup bg ON bg.id = bt.bet_group_id
   WHERE user_id = 12
UNION
  SELECT 'non' as class, dt.amount, dt.created_at as time, 'Вывод средств&nbsp;-&nbsp;<span class="status">Обработан</span>' as bettitle, 
    dt.txid as paymentid, NULL as bettype, NULL as betchoice
  FROM public.django_bitcoin_wallettransaction bwt
  JOIN django_bitcoin_outgoingtransaction dt ON bwt.outgoing_transaction_id = dt.id
  JOIN bbil_profile p ON bwt.to_wallet_id = p.wallet_id
  WHERE user_id = 12;
"""
        
        return dict
        
@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save() 
    