from django.contrib import admin
from .models import Meeting, MeetingMember
# Register your models here.
admin.site.register(Meeting)
admin.site.register(MeetingMember)