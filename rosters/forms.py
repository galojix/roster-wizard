from django import forms
from django.forms import ModelForm

from .models import Leave, TimeSlot


class DateInput(forms.DateInput):
    input_type = "date"


class LeaveCreateForm(ModelForm):
    class Meta:
        model = Leave
        fields = ("date", "staff_member")
        widgets = {"date": DateInput()}


class LeaveUpdateForm(ModelForm):
    class Meta:
        model = Leave
        fields = ("date", "staff_member")
        widgets = {"date": DateInput()}


class TimeSlotCreateForm(ModelForm):
    class Meta:
        model = TimeSlot
        fields = ("date", "shift", "staff")
        widgets = {"date": DateInput()}


class TimeSlotUpdateForm(ModelForm):
    class Meta:
        model = TimeSlot
        fields = ("date", "shift", "staff")
        widgets = {"date": DateInput()}


class GenerateRosterForm(forms.Form):
    start_date = forms.DateTimeField(widget=DateInput())
    num_days = forms.IntegerField(initial=28)


class SelectRosterForm(forms.Form):
    start_date = forms.DateTimeField(widget=DateInput())
    num_days = forms.IntegerField(initial=28)
