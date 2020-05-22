from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.

class StudyDashboardPage(TemplateView):
    template_name = 'studymode/study_dashboard.html'
