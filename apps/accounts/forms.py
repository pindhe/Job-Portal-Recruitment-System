from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

from .models import Role

User = get_user_model()

INPUT = (
    "w-full rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 "
    "px-4 py-3 text-slate-800 dark:text-slate-100 focus:border-primary focus:ring-2 "
    "focus:ring-primary/30 outline-none transition"
)


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": INPUT, "placeholder": "Password"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": INPUT, "placeholder": "Confirm password"}))
    role = forms.ChoiceField(
        choices=[(Role.CANDIDATE, "I'm a Job Seeker"), (Role.EMPLOYER, "I'm an Employer / Recruiter")],
        widget=forms.RadioSelect,
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": INPUT, "placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"class": INPUT, "placeholder": "Last name"}),
            "email": forms.EmailInput(attrs={"class": INPUT, "placeholder": "you@example.com"}),
            "phone": forms.TextInput(attrs={"class": INPUT, "placeholder": "Phone (optional)"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            raise forms.ValidationError("Passwords do not match.")
        if len(cleaned.get("password1", "")) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.role = self.cleaned_data["role"]
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": INPUT, "placeholder": "you@example.com", "autofocus": True})
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": INPUT, "placeholder": "Password"}))
    remember_me = forms.BooleanField(required=False)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "avatar", "locale", "dark_mode"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": INPUT}),
            "last_name": forms.TextInput(attrs={"class": INPUT}),
            "phone": forms.TextInput(attrs={"class": INPUT}),
            "locale": forms.Select(attrs={"class": INPUT}),
        }


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": INPUT, "placeholder": "you@example.com"}))


class ResetPasswordForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={"class": INPUT, "placeholder": "6-digit code"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": INPUT, "placeholder": "New password"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": INPUT, "placeholder": "Confirm password"}))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned
