from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.utils.safestring import mark_safe

from .models import Users, Friends, Statuses, SendStatuses, SendReactions, Reactions


class UsersAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'created_at', 'user_id', 'username', 'first_name', 'referral', 'friends', 'my_referral',
        'percent', 'get_status', 'send_status', 'last_status', 'real_active'
    ]
    list_display_links = [
        'id', 'created_at', 'user_id', 'username', 'first_name', 'referral', 'friends', 'my_referral',
        'percent', 'get_status', 'send_status', 'last_status', 'real_active'
    ]
    search_fields = ['user_id', 'username', 'first_name']
    list_filter = ['created_at', 'referral']


class FriendsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'referral']
    list_display_links = ['id', 'user', 'referral']


class StatusesAdmin(admin.ModelAdmin):
    list_display = ['id', 'weight', 'user', 'title', 'quantity', 'pay_status']
    list_display_links = ['id', 'user', 'title', 'quantity', 'pay_status']
    list_editable = ['weight']


class SendStatusesAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'user', 'status', 'get_image']
    list_display_links = ['id', 'created_at', 'user', 'status', 'get_image']

    def get_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src={obj.image.url} width="140" height="140"')
        else:
            return None

    get_image.short_description = 'Изображение'


class SendReactionsAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'send_status', 'user', 'reaction']
    list_display_links = ['id', 'created_at', 'send_status', 'user', 'reaction']


class ReactionsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'reaction']
    list_display_links = ['id', 'user', 'reaction']


admin.site.register(Users, UsersAdmin)
admin.site.register(Friends, FriendsAdmin)
admin.site.register(Statuses, StatusesAdmin)
admin.site.register(SendStatuses, SendStatusesAdmin)
admin.site.register(SendReactions, SendReactionsAdmin)
admin.site.register(Reactions, ReactionsAdmin)


admin.site.unregister(User)
admin.site.unregister(Group)
