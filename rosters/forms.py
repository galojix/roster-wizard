from django import forms
from django.forms import ModelForm

from .models import Leave, TimeSlot, StaffRule


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


class SelectRosterForm(forms.Form):
    start_date = forms.DateTimeField(widget=DateInput())


class StaffRuleUpdateForm(ModelForm):
    class Meta:
        model = StaffRule
        fields = ("staff_rule_name", "day_group", "staff")
        widgets = {"staff": forms.CheckboxSelectMultiple()}


class StaffRuleCreateForm(ModelForm):
    class Meta:
        model = StaffRule
        fields = ("staff_rule_name", "day_group", "staff")
        widgets = {"staff": forms.CheckboxSelectMultiple()}


class DaySetCreateForm(forms.Form):
    number_of_days = forms.IntegerField(initial=28)
