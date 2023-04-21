from django.db import models


class Users(models.Model):
    created_at = models.DateTimeField(verbose_name='Дата регистрации')
    user_id = models.BigIntegerField(verbose_name='Телеграм ID')
    username = models.CharField(max_length=200, blank=True, null=True, verbose_name='Имя пользователя')
    first_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='Имя')
    referral = models.BooleanField(default=False, verbose_name='Реферал')
    friends = models.IntegerField(default=0, verbose_name='Количество друзей')
    my_referral = models.IntegerField(default=0, verbose_name='Количество рефералов')
    percent = models.FloatField(default=0.0, verbose_name='Процент реакций')
    get_status = models.IntegerField(default=0, verbose_name='Количество полученных статусов')
    send_status = models.IntegerField(default=0, verbose_name='Количество отправленных статусов')
    last_status = models.DateTimeField(blank=True, null=True, verbose_name='Дата и время последнего статуса')
    last_active = models.DateTimeField(blank=True, null=True, verbose_name='Дата и время последней активности')
    real_active = models.DateTimeField(blank=True, null=True, verbose_name='Активность пользователя')
    free = models.BooleanField(null=True, verbose_name='Бесплатный статус')

    def __str__(self):
        return f"{self.user_id} - {self.username}" if self.username else f"{self.user_id} - Аноним"

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        db_table = 'users'


class Friends(models.Model):
    user = models.ForeignKey(Users, related_name='friends_user', on_delete=models.CASCADE, verbose_name='Пользователь')
    referral = models.ForeignKey(
        Users, related_name='friends_referral', on_delete=models.CASCADE, verbose_name='Реферал')

    def __str__(self):
        return f"{self.user} | {self.referral}"

    class Meta:
        verbose_name = 'Друг'
        verbose_name_plural = 'Друзья'
        db_table = 'friends'


class Statuses(models.Model):
    weight = models.IntegerField(default=0, verbose_name='Сортировка')
    user = models.CharField(max_length=30, null=True, verbose_name='Пользователь')
    title = models.CharField(max_length=100, verbose_name='Статус')
    quantity = models.IntegerField(default=0, verbose_name='Количество использований')
    pay_status = models.BooleanField(default=False, verbose_name='Статус оплаты')

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'
        db_table = 'statuses'


class SendStatuses(models.Model):
    created_at = models.DateTimeField(verbose_name='Дата установки статуса')
    user = models.ForeignKey(Users, related_name='send_statuses', on_delete=models.CASCADE, verbose_name='Пользователь')
    status = models.ForeignKey(Statuses, related_name='send_statuses', on_delete=models.CASCADE, verbose_name='Статус')
    message_id = models.BigIntegerField(default=0, verbose_name='ID Сообщения')
    message_text = models.TextField(null=True, verbose_name='Текст сообщения')
    image = models.ImageField(upload_to='photos/', null=True, verbose_name='Изображение')

    def __str__(self):
        return f"{self.user} | {self.status}"

    class Meta:
        verbose_name = 'Установленный статус'
        verbose_name_plural = 'Установленные статусы'
        db_table = 'send_statuses'


class SendReactions(models.Model):
    created_at = models.DateTimeField(verbose_name='Дата реакции')
    send_status = models.ForeignKey(
        SendStatuses, related_name='send_reactions', on_delete=models.CASCADE, verbose_name='Статус')
    user = models.ForeignKey(
        Users, related_name='send_reactions', on_delete=models.CASCADE, verbose_name='Пользователь')
    reaction = models.CharField(max_length=100, verbose_name='Реакция')

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Реакция на статус'
        verbose_name_plural = 'Реакции на статус'
        db_table = 'send_reactions'


class Reactions(models.Model):
    user = models.CharField(max_length=30, verbose_name='Пользователь')
    reaction = models.CharField(max_length=30, verbose_name='Реакция')

    def __str__(self):
        return f"{self.user} - {self.reaction}"

    class Meta:
        verbose_name = 'Реакция'
        verbose_name_plural = 'Реакции'
        db_table = 'reactions'


class DeleteMessage(models.Model):
    chat_id = models.BigIntegerField(verbose_name='Телеграм ID')
    message_id = models.CharField(max_length=200, verbose_name='ID сообщений')

    def __str__(self):
        return f"{self.chat_id}"

    class Meta:
        verbose_name = 'Удаление сообщений'
        verbose_name_plural = 'Удаление сообщений'
        db_table = 'delete_message'
