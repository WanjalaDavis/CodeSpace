from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='profile_photos/', default='WanjalaTechSolutions_logo.png')
    total_questions = models.PositiveIntegerField(default=0)
    total_answers = models.PositiveIntegerField(default=0)

    @property
    def score(self):
        # Example scoring logic: weight answers more than questions
        return self.total_answers * 2 + self.total_questions

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

class Project(models.Model):
    FILE_TYPE_CHOICES = [
        ('html', 'HTML'),
        ('python', 'Python'),
        ('java', 'Java'),
    ]
    name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50, choices=FILE_TYPE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    created_at = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.name

class File(models.Model):
    name = models.CharField(max_length=255)
    content = models.TextField()
    project = models.ForeignKey('Project', related_name='project_files', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questions")
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Reply(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="replies")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="liked_replies", blank=True)

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="notes/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient}"

class VideoTutorial(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
    ]

    title = models.CharField(max_length=200)
    video = models.FileField(upload_to='videos/')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.CASCADE)
    reply = models.ForeignKey(Reply, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="likes", blank=True)

    class Meta:
        unique_together = ('user', 'question', 'reply')

    def __str__(self):
        return f"Like by {self.user.username} on {'question' if self.question else 'reply'}"

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

class Payment(models.Model):
    phone = models.CharField(max_length=15)
    mpesa_code = models.CharField(max_length=20, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    package = models.CharField(max_length=20)
    date_paid = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone} - {self.mpesa_code}"

class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Skill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(max_length=100)
    level = models.PositiveIntegerField()  # Percentage (0-100)

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="goals")
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
