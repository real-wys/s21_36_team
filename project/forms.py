from django import forms

from django.contrib.auth import authenticate
from .models import User, ChatMessage
import re


MAX_UPLOAD_SIZE = 2500000


class LoginForm(forms.Form):
    username = forms.CharField(max_length = 20,
                     widget = forms.TextInput(attrs={'class': 'input-material', 'placeholder': 'Input your username', 'id': 'username'}))
    password = forms.CharField(max_length = 200, 
                     widget = forms.PasswordInput(attrs={'class': 'input-material', 'placeholder': 'Input your password', 'id': 'password'}))

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            #raise forms.ValidationError("Invalid username/password")
            self.add_error('username', error='Invalid username/password')
            self.add_error('password', error='Invalid username/password')

        # We must return the cleaned data we got from our parent.
        return cleaned_data


class RegisterForm(forms.Form):
    username            = forms.CharField(max_length = 20, 
                                widget = forms.TextInput(attrs={'class': 'input-material', 'placeholder': 'Input your username', 'id': 'username'}))
    password            = forms.CharField(max_length = 200, 
                                 widget = forms.PasswordInput(attrs={'class': 'input-material', 'placeholder': 'Input your password', 'id': 'password'}))
    confPassword        = forms.CharField(max_length = 200,  
                                 widget = forms.PasswordInput(attrs={'class': 'input-material', 'placeholder': 'Confirm your password', 'id': 'confPassword'}))
    email               = forms.CharField(max_length=50,
                                 widget = forms.EmailInput(attrs={'class': 'input-material', 'placeholder': 'Input your email', 'id': 'email'}))
    firstname           = forms.CharField(max_length=20,
                                 widget = forms.TextInput(attrs={'class': 'input-material', 'placeholder': 'Input your firstname', 'id': 'firstname'}))
    lastname            = forms.CharField(max_length=20,
                                 widget = forms.TextInput(attrs={'class': 'input-material', 'placeholder': 'Input your lastname', 'id': 'lastname'}))
    role                = forms.CharField(widget=forms.Select(choices=[(0,"user"),(1,"lawyer"),]), initial = 0,)


    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        password = cleaned_data.get('password')
        confPassword = cleaned_data.get('confPassword')
        if password and confPassword and password != confPassword:
            #raise forms.ValidationError("Passwords did not match.")
            self.add_error('password', error='Passwords dismatch')
            self.add_error('confPassword', error='Passwords dismatch')
        
        email = cleaned_data.get('email')
        if not re.match(r'[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z_]{0,19}.[com|edu]',email):  
            self.add_error('email', error='email format error')
        
        # We must return the cleaned data we got from our parent.
        return cleaned_data

    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username


# class ChatMessageForm(forms.ModelForm):
#     class Meta:
#         model = ChatMessage
#         exclude = (
#             'from_user',
#             'to_user',
#             'message_creation_time',
#         )
#     widgets = {
#         'message_text': forms.CharField(),
#         'message_image': forms.FileField(),
#     }

# class ImageMessageForm(forms.Form):
# 	image = forms.ImageField(label='')