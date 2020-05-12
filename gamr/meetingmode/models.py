from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()
# Create your models here.

class Meeting(models.Model):
    meeting_name = models.CharField(max_length=250)
    meeting_code = models.CharField(max_length=10)
    slug = models.SlugField(allow_unicode=True, unique=True)
    members = models.ManyToManyField(User, through="MeetingMember")
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.meeting_code)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.meeting_code

    def get_absolute_url(self):
        return reverse('meeting:join', kwargs={'slug':self.slug})


class MeetingTranscript(models.Model):
    transcript = models.TextField()
    author = models.ForeignKey(User, related_name='user_transcript', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    meeting = models.ForeignKey(Meeting, related_name='transcript_meeting', on_delete=models.CASCADE)

    def __str__(self):
        return self.author.username

    def get_last_transcript(self):
        return self.objects.order_by('-timestamp').all()


class MeetingMember(models.Model):
    meeting = models.ForeignKey(Meeting, related_name='memberships', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user_meetings', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


    class Meta:
        unique_together = ('meeting','user')



