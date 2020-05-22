from django.urls import path
from .views import StudyDashboardPage

app_name = 'studymode'

urlpatterns = [
    path('<username>/dashboard/', StudyDashboardPage.as_view(), name='dashboard'),
]