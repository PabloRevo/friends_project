"""
Файл - описание моделей БД
"""

from peewee import *
from settings.settings import DATABASE, USER, PASSWORD, HOST, PORT


db = PostgresqlDatabase(
    database=DATABASE,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    autorollback=True
)


class BaseModel(Model):
    id = PrimaryKeyField(unique=True)

    class Meta:
        database = db


class Users(BaseModel):
    created_at = DateTimeField()
    user_id = BigIntegerField()
    username = CharField(max_length=200, null=True)
    first_name = CharField(max_length=200, null=True)
    referral = BooleanField(default=False)
    friends = IntegerField(default=0)
    my_referral = IntegerField(default=0)
    percent = FloatField(default=0.0)
    get_status = IntegerField(default=0)
    send_status = IntegerField(default=0)
    last_status = DateTimeField(null=True)
    last_active = DateTimeField(null=True)
    real_active = DateTimeField(null=True)
    free = BooleanField(null=True)

    class Meta:
        db_table = 'users'


class Friends(BaseModel):
    user = ForeignKeyField(Users, related_name='friends_user', on_delete='CASCADE')
    referral = ForeignKeyField(Users, related_name='friends_referral', on_delete='CASCADE')

    class Meta:
        db_table = 'friends'


class Statuses(BaseModel):
    weight = IntegerField(default=0)
    user = CharField(max_length=30)
    title = CharField(max_length=100)
    quantity = IntegerField(default=0)
    pay_status = BooleanField(default=False)

    class Meta:
        db_table = 'statuses'


class SendStatuses(BaseModel):
    created_at = DateTimeField()
    user = ForeignKeyField(Users, related_name='send_statuses', on_delete='CASCADE')
    status = ForeignKeyField(Statuses, related_name='send_statuses', on_delete='CASCADE')
    message_id = BigIntegerField(default=0)
    message_text = TextField(null=True)
    image = CharField(max_length=100, null=True)

    class Meta:
        db_table = 'send_statuses'


class SendReactions(BaseModel):
    created_at = DateTimeField()
    send_status = ForeignKeyField(SendStatuses, related_name='send_reactions', on_delete='CASCADE')
    user = ForeignKeyField(Users, related_name='send_reactions', on_delete='CASCADE')
    reaction = CharField(max_length=100)

    class Meta:
        db_table = 'send_reactions'


class DeleteMessage(BaseModel):
    chat_id = BigIntegerField()
    message_id = CharField(max_length=200)

    class Meta:
        db_table = 'delete_message'


class Reactions(BaseModel):
    user = CharField(max_length=30)
    reaction = CharField(max_length=30)

    class Meta:
        db_table = 'reactions'
