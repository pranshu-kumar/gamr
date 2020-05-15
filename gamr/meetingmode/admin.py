from django.contrib import admin
from .models import Meeting, MeetingMember, MeetingInfo
# Register your models here.

admin.site.register(Meeting)
admin.site.register(MeetingMember)
admin.site.register(MeetingInfo)