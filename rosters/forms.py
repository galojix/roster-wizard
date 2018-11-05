from django import forms
from django.forms import ModelForm

from .models import Leave


class DateInput(forms.DateInput):
    input_type = 'date'


class LeaveCreateForm(ModelForm):

    class Meta:
        model = Leave
        fields = ('date', 'staff_member')
        widgets = {
            'date': DateInput(),
        }


class LeaveUpdateForm(ModelForm):

    class Meta:
        model = Leave
        fields = ('date', 'staff_member')
        widgets = {
            'date': DateInput(),
        }
