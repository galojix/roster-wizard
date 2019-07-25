from django import forms
from django.forms import ModelForm

from .models import Leave, TimeSlot, StaffRule, Preference


class DateInput(forms.DateInput):
    input_type = "date"


class LeaveCreateForm(ModelForm):
    start_date = forms.DateTimeField(widget=DateInput())
    end_date = forms.DateTimeField(widget=DateInput())

    class Meta:
        model = Leave
        fields = ("staff_member",)
        widgets = {"date": DateInput()}


class LeaveUpdateForm(ModelForm):
    class Meta:
        model = Leave
        fields = ("date", "staff_member")
        widgets = {"date": DateInput()}


class PreferenceCreateForm(ModelForm):
    class Meta:
        model = Preference
        fields = ("staff_member", "date", "shift", "priority")
        widgets = {"date": DateInput()}


class PreferenceUpdateForm(ModelForm):
    class Meta:
        model = Preference
        fields = ("date", "shift", "priority")
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
        widgets = {
            "date": DateInput(),
            "staff": forms.CheckboxSelectMultiple(),
            }


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
