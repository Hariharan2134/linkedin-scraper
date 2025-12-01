from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class ScraperForm(forms.Form):
    query = forms.CharField(max_length=255)
    pages = forms.IntegerField(min_value=1, max_value=10)
    max_profiles = forms.IntegerField(min_value=1, max_value=50)
