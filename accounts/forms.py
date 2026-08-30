from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from departments.models import Department

FORM_CLASS = 'form-control'

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': FORM_CLASS, 'placeholder': 'John'
    }))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': FORM_CLASS, 'placeholder': 'Doe'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': FORM_CLASS, 'placeholder': 'john.doe@university.edu'
    }))
    role = forms.ChoiceField(
        choices=[(User.Role.BUYER, "Student / Researcher (Buyer)"), (User.Role.STAFF, "Faculty / Department Staff")],
        initial=User.Role.BUYER,
        widget=forms.Select(attrs={'class': FORM_CLASS, 'id': 'role-select'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label="Select Department (Staff only)",
        widget=forms.Select(attrs={'class': FORM_CLASS, 'id': 'department-field'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'department')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': FORM_CLASS, 'placeholder': 'johndoe12'
        })
        for fieldname in ['password1', 'password2']:
            if fieldname in self.fields:
                self.fields[fieldname].widget.attrs.update({
                    'class': FORM_CLASS, 'placeholder': '••••••••'
                })

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        department = cleaned_data.get('department')
        if role == User.Role.STAFF and not department:
            self.add_error('department', 'Faculty/Department Staff must select an academic department.')
        return cleaned_data

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': FORM_CLASS, 'placeholder': 'Username or Email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': FORM_CLASS, 'placeholder': '••••••••'
    }))

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'bio', 'department')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': FORM_CLASS}),
            'last_name': forms.TextInput(attrs={'class': FORM_CLASS}),
            'email': forms.EmailInput(attrs={'class': FORM_CLASS}),
            'phone_number': forms.TextInput(attrs={'class': FORM_CLASS}),
            'bio': forms.Textarea(attrs={'rows': 3, 'class': FORM_CLASS}),
            'department': forms.Select(attrs={'class': FORM_CLASS}),
        }
