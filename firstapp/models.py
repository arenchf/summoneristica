from django.db import models

# Create your models here.


class Summoner(models.Model):
    summoner_name = models.CharField(max_length=30)

    def __str__(self):
        return '{}'.format(self.summoner_name)

    class Meta:
        verbose_name = 'Summoner'
        verbose_name_plural = 'Summoners'
