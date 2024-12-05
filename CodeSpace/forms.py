from django import forms
from .models import Project, Profile
from django.contrib.auth.models import User
from .models import VideoTutorial

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo']  # Only photo field for Profile

    photo = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'file_type']  # Fields for project name and file type

    name = forms.CharField(max_length=255,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter project name'}))
    file_type = forms.ChoiceField(choices=Project.FILE_TYPE_CHOICES,
                                  widget=forms.Select(attrs={'class': 'form-control'}))

    def save(self, commit=True):
        project = super().save(commit=False)

        # Automatically set the user to the logged-in user
        if not project.user:
            project.user = self.instance.user  # If user not set, set it to the logged-in user

        if commit:
            project.save()

        return project

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = VideoTutorial
        fields = ['title', 'video']

class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class EditProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name']