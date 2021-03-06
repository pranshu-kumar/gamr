# chat/urls.py
from django.urls import path
from . import views
from .views import (
    CreateMeeting,
    ListMeetings,
    JoinMeeting,
    DashboardView,
    LeaveMeeting,
    html_to_pdf_view
)
app_name = 'meetingmode'

urlpatterns = [
    path('', ListMeetings.as_view(), name='all'),
    path('new-meeting/', CreateMeeting.as_view(), name='create'),
    path('join/<slug>', JoinMeeting.as_view(), name="join"),
    path('dashboard/<slug>', DashboardView.as_view(), name='room'),
    path('leave-meeting/<slug>', LeaveMeeting.as_view(), name='leave'),
    path('leave-meeting/<slug>', LeaveMeeting.as_view(), name='leave'),
    path('download/<slug>', html_to_pdf_view, name="download"),
]