import datetime

import requests
from django.db import models
from telegram_bot import utils


class User(models.Model):
    user_id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=32, null=True, blank=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256, null=True, blank=True)
    language_code = models.CharField(max_length=8, null=True, blank=True, help_text="Telegram client's lang")
    deep_link = models.CharField(max_length=64, null=True, blank=True)

    is_blocked_bot = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)

    is_admin = models.BooleanField(default=False)
    is_moderator = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    waiting_for_input = models.BooleanField(default=False)
    waiting_for_announcement = models.BooleanField(default=False)

    anime = models.BooleanField(default=False)
    anime_id = models.CharField(max_length=10, null=True, blank=True)
    anime_code = models.CharField(max_length=50, null=True, blank=True)
    anime_token = models.CharField(max_length=50, null=True, blank=True)
    anime_refresh_token = models.CharField(max_length=50, null=True, blank=True)
    anime_username = models.CharField(max_length=32, null=True, blank=True)
    anime_password = models.CharField(max_length=32, null=True, blank=True)


    def __str__(self):
        return f'@{self.username}' if self.username is not None else f'{self.user_id}'

    @classmethod
    def get_user_and_created(cls, update, context):
        """ python-telegram_bot-bot's Update, Context --> User instance """
        data = utils.extract_user_data_from_update(update)
        u, created = cls.objects.update_or_create(user_id=data["user_id"], defaults=data)

        if created:
            if context is not None and context.args is not None and len(context.args) > 0:
                payload = context.args[0]
                if str(payload).strip() != str(data["user_id"]).strip():  # you can't invite yourself
                    u.deep_link = payload
                    u.save()

        return u, created

    @classmethod
    def get_user(cls, update, context):
        u, _ = cls.get_user_and_created(update, context)
        return u

    @classmethod
    def get_user_by_username_or_user_id(cls, string):
        """ Search user in DB, return User or None if not found """
        username = str(string).replace("@", "").strip().lower()
        if username.isdigit():  # user_id
            return cls.objects.filter(user_id=int(username)).first()
        return cls.objects.filter(username__iexact=username).first()

    def invited_users(self):  # --> User queryset 
        return User.objects.filter(deep_link=str(self.user_id), created_at__gt=self.created_at)


class Logs(models.Model):
    date = models.DateTimeField()
    log_type = models.CharField(max_length=50, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(null=True)

    @classmethod
    def log(cls, log_type, user, text):
        date = datetime.datetime.now()
        cls.objects.create(date=date, log_type=log_type, user=user, text=text)


class UserMessages(models.Model):
    date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(null=True)

    @classmethod
    def log(cls, user, text):
        date = datetime.datetime.now()
        cls.objects.create(date=date, user=user, text=text)
