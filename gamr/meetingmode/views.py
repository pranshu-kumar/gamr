from django.contrib import messages
from django.shortcuts import render, HttpResponse, reverse
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.generic import (
    TemplateView,
    CreateView,
    ListView,
    RedirectView,
    DetailView)

from weasyprint import HTML

from django.core.files.storage import FileSystemStorage

from django.urls import reverse_lazy

from django.shortcuts import get_object_or_404

from django.contrib.auth import get_user_model

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Meeting, MeetingMember, MeetingInfo

from googletrans import Translator

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


def html_to_pdf_view(request, **kwargs):
    slug = kwargs.get('slug')
    meeting = Meeting.objects.get(slug=slug)
    meetingInfo = MeetingInfo.objects.get(meeting=meeting)
    transcript = meetingInfo.transcript
    translator = Translator()
    translation = translator.translate(transcript, dest='hi')
    translated_text = translation.text
    translated_sentences = translated_text.split('\n')
    sentences = transcript.split('\n')
    paragraphs = {
        'transcript':sentences,
        'translated_transcript':translated_sentences,
        'summary':meetingInfo.summary, 
        'translated_summary':meetingInfo.translated_summary,
        'description':meeting.description
    }
    html_string = render_to_string('meetingmode/pdf_template.html', paragraphs)

    html = HTML(string=html_string)
    html.write_pdf(target='/tmp/meeting_'+slug+'.pdf')
    fs = FileSystemStorage('/tmp')
    filename = 'meeting_'+slug+'.pdf'
    with fs.open('meeting_'+slug+'.pdf') as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="meeting.pdf"'
        return response

    return response

