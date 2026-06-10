from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """
    Form for creating a new CustomUser.
    Includes 'email', 'username', 'password1', and 'password2'.
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'fullname',
            'nickname',
            'password1',
            'password2',
        ]



class ProfileForm(forms.ModelForm):
    """
    Form for updating a CustomUser's profile fields.
    """
    class Meta:
        model = User  
        fields = ['fullname', 'nickname']

# class StudentAttendance(forms.ModelForm):
#     """
#     Form for updating a user's attendance per course
#     """
#     class Meta:
#         model = User
#         fields = []