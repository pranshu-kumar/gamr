from django.contrib import messages
from django.shortcuts import render, HttpResponse, reverse
from django.views.generic import (
    TemplateView,
    CreateView,
    ListView,
    RedirectView,
    DetailView)

from django.urls import reverse_lazy

from django.shortcuts import get_object_or_404

from django.contrib.auth import get_user_model

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Meeting, MeetingMember

User = get_user_model()

class DashboardView(DetailView):
    model = Meeting

class CreateMeeting(LoginRequiredMixin, CreateView):
    fields = ('meeting_name', 'meeting_code', 'description')
    model = Meeting

class ListMeetings(ListView):
    model = Meeting

class JoinMeeting(LoginRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse('meeting:all')

    def get(self, request, *args, **kwargs):
        meeting = get_object_or_404(Meeting, slug = self.kwargs.get('slug'))

        try:
            MeetingMember.objects.create(user=self.request.user, meeting=meeting)

        except IntegrityError:
            messages.warning(self.request,("Warning, already a member of {}".format(meeting.meeting_name)))
        
        else:
            messages.success(self.request, "You are now a member of the {} Meeting.".format(meeting.meeting_name))

        return super().get(request, *args, **kwargs)

class LeaveMeeting(LoginRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse('meeting:all')

    def get(self, request, *args, **kwargs):

        try:
            membership = MeetingMember.objects.filter(
                user=self.request.user,
                meeting__slug = self.kwargs.get('slug')
            ).get()

        except MeetingMember.DoesNotExist:
            messages.warning(
                self.request,
                "You can't leave this meeting because you aren't in it."
            )

        else:
            membership.delete()
            messages.success(
                self.request,
                "You have successfully left this meeting."
            )
        return super().get(request, *args, **kwargs)