from django.db import models


class Settings(models.Model):
    token = models.CharField(max_length=150, verbose_name="token")
    chat_id = models.IntegerField(default=0)
    chunk_size = models.IntegerField(default=1024)
    cycle = models.BooleanField(default=False, verbose_name="cycle")
    dont_use_proxy = models.BooleanField(default=True, verbose_name="don't use proxy")


class Links(models.Model):
    link = models.CharField(max_length=150, verbose_name="link")


class Posts(models.Model):
    id_post = models.CharField(max_length=150)
    group = models.CharField(max_length=150)
