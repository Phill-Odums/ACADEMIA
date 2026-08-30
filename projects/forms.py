from django import forms
from .models import ProjectMaterial
from departments.models import Department

FORM_CLASS = 'form-control'

class ProjectMaterialUploadForm(forms.ModelForm):
    class Meta:
        model = ProjectMaterial
        fields = ('title', 'department', 'abstract', 'keywords', 'file', 'price', 'year_defended', 'pages_count')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': FORM_CLASS,
                'placeholder': 'e.g. Machine Learning Approaches for Automated Medical Diagnosis'
            }),
            'department': forms.Select(attrs={'class': FORM_CLASS}),
            'abstract': forms.Textarea(attrs={
                'rows': 5, 'class': FORM_CLASS,
                'placeholder': 'Summary of methodology, key findings, and academic contributions…'
            }),
            'keywords': forms.TextInput(attrs={
                'class': FORM_CLASS,
                'placeholder': 'AI, Healthcare, Neural Networks, Python'
            }),
            'file': forms.FileInput(attrs={
                'class': FORM_CLASS + ' file:mr-4 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-brand-50 file:text-brand-700 hover:file:bg-brand-100',
                'accept': '.pdf,.docx,.doc'
            }),
            'price': forms.NumberInput(attrs={
                'class': FORM_CLASS, 'placeholder': '5000.00', 'step': '500'
            }),
            'year_defended': forms.NumberInput(attrs={
                'class': FORM_CLASS, 'placeholder': '2024'
            }),
            'pages_count': forms.NumberInput(attrs={
                'class': FORM_CLASS, 'placeholder': '65'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.role == 'STAFF' and user.department:
            self.fields['department'].initial = user.department
