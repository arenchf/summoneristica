from django.db import models

# Create your models here.


class Summoner(models.Model):
    summonerName = models.CharField(verbose_name="Summoner Name", max_length=50, null=True)
    accountId = models.CharField(verbose_name="Account ID", max_length=56, null=True)
    summonerId = models.CharField(verbose_name="Summoner ID",max_length=64,null=True)
    puuid = models.CharField(verbose_name="PUUID",max_length=78,null=True)
    profileIconId = models.IntegerField(verbose_name="Profile Icon ID", null=True)
    revisionDate = models.BigIntegerField(verbose_name="Revision Date", null=True)
    summonerLevel = models.IntegerField(verbose_name="Summoner Level", null=True)
    server = models.CharField(verbose_name="Server",max_length=5,null=True)

    def __str__(self):
        return '{}'.format(self.summonerName)

    class Meta:
        verbose_name = 'Summoner'
        verbose_name_plural = 'Summoners'


class Matchlist(models.Model):
    platformid=models.CharField(verbose_name="Platform ID",max_length=4,null=True)
    gameid = models.BigIntegerField(verbose_name="Game ID",null=True)
    championid = models.IntegerField(verbose_name="Champion ID",null=True)
    queue = models.IntegerField(verbose_name="Queue",null=True)
    season = models.IntegerField(verbose_name="Season",null=True)
    timestamp = models.BigIntegerField(verbose_name="Timestamp",null=True)
    role = models.CharField(verbose_name="Role",max_length=20,null=True)
    lane = models.CharField(verbose_name="Lane",max_length=20,null=True)
    def __str__(self):  
        x = str(self.gameid)
        return x




class Deneme(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Company(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Programmer(models.Model):
    name = models.CharField(max_length=20)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    deneme = models.ManyToManyField(Deneme)
    def __str__(self):
        return self.name