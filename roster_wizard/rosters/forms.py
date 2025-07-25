"""Forms."""

import datetime
from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError

from .models import (
    Leave,
    RosterSettings,
    TimeSlot,
    ShiftSequence,
    DayGroupDay,
    DayGroup,
    ShiftSequenceShift,
)


class RosterSettingsForm(ModelForm):
    """Roster Settings Form."""

    def __init__(self, roster_name, not_used, *args, **kwargs):
        """Set initial form values."""
        super().__init__(*args, **kwargs)
        self.fields["roster_name"].initial = roster_name
        self.fields["not_used"].initial = not_used

    class Meta:
        """Meta."""

        model = RosterSettings
        fields = (
            "roster_name",
            "not_used",
        )


class DateInput(forms.DateInput):
    """Date Input Widget for Forms."""

    input_type = "date"


class LeaveCreateForm(ModelForm):
    """Leave Create Form."""

    start_date = forms.DateTimeField(widget=DateInput())
    end_date = forms.DateTimeField(widget=DateInput())

    class Meta:
        """Meta."""

        model = Leave
        fields = ("staff_member", "description")
        widgets = {"date": DateInput()}


class LeaveUpdateForm(ModelForm):
    """Leave Update Form."""

    class Meta:
        """Meta."""

        model = Leave
        fields = ("date", "staff_member", "description")
        widgets = {"date": DateInput()}


class TimeSlotCreateForm(ModelForm):
    """Time Slot Create Form."""

    class Meta:
        """Meta."""

        model = TimeSlot
        fields = ("date", "shift", "staff")
        widgets = {"date": DateInput()}


class TimeSlotUpdateForm(ModelForm):
    """Time Slot Update Form."""

    class Meta:
        """Meta."""

        model = TimeSlot
        fields = ("date", "shift", "staff")
        widgets = {
            "date": DateInput(),
            "staff": forms.CheckboxSelectMultiple(),
        }


class GenerateRosterForm(forms.Form):
    """Generate Roster Form."""

    def __init__(self, request, *args, **kwargs):
        """Get default start date from session."""
        super().__init__(*args, **kwargs)
        if "start_date" in request.session:
            start_date = datetime.datetime.strptime(
                request.session["start_date"], "%d-%b-%Y"
            )
        else:
            start_date = datetime.datetime.now()
        self.fields["start_date"] = forms.DateTimeField(
            widget=DateInput(), initial=start_date
        )


class EditRosterForm(forms.Form):
    """Edit Roster Form."""

    def __init__(self, num_days, shift_types, *args, **kwargs):
        """Create form fields."""
        super().__init__(*args, **kwargs)
        choices = [(shift_type, shift_type) for shift_type in shift_types]
        for day in range(num_days):
            self.fields["day-" + str(day)] = forms.ChoiceField(
                choices=choices,
                label="",
                initial="X",
                required=False,
            )


class SelectRosterForm(forms.Form):
    """Select Roster Form."""

    start_date = forms.DateTimeField(widget=DateInput())


class SelectBulkDeletionPeriodForm(forms.Form):
    """Select Bulk Deltion Period Form."""

    start_date = forms.DateTimeField(widget=DateInput())
    end_date = forms.DateTimeField(widget=DateInput())


class ShiftSequenceUpdateForm(ModelForm):
    """Shift Sequence Update Form."""

    class Meta:
        """Meta."""

        model = ShiftSequence
        fields = ("shiftsequence_name", "daygroup", "staff")
        widgets = {"staff": forms.CheckboxSelectMultiple()}


class ShiftSequenceCreateForm(ModelForm):
    """Shift Sequence Create Form."""

    class Meta:
        """Meta."""

        model = ShiftSequence
        fields = ("shiftsequence_name", "daygroup", "staff")
        widgets = {"staff": forms.CheckboxSelectMultiple()}


class DaySetCreateForm(forms.Form):
    """Day Set Create Form."""

    number_of_days = forms.IntegerField(initial=28)


class StaffRequestUpdateForm(forms.Form):
    """Staff Requests Update Form."""

    def __init__(self, requests, priorities, *args, **kwargs):
        """Add fields for each shift."""
        super().__init__(*args, **kwargs)
        for i, request in enumerate(requests):
            choices = (
                ("Yes", "Yes"),
                ("No", "No"),
                ("Don't Care", "Don't Care"),
            )
            self.fields[f"request_{i}"] = forms.ChoiceField(
                choices=choices,
                label="",
                initial=requests[i],
                required=False,
            )
            self.fields[f"priority_{i}"] = forms.IntegerField(
                label="", initial=priorities[i], required=False
            )


class DayGroupDayCreateForm(ModelForm):
    """Day Group Day Create Form."""

    def __init__(self, daygroup, *args, **kwargs):
        """Get daygroup."""
        super().__init__(*args, **kwargs)
        self.daygroup = daygroup

    class Meta:
        """Meta."""

        model = DayGroupDay
        fields = ("day",)

    def clean(self):
        """Ensure day not already in day group."""
        cleaned_data = super().clean()
        day = cleaned_data["day"]
        daygroup = DayGroup.objects.get(id=self.daygroup)
        # if day already in day group raise Validation error
        if DayGroupDay.objects.filter(day=day, daygroup=daygroup):
            raise ValidationError(
                f"Day {day} is already in the Day Group {daygroup.name}."
            )
        return cleaned_data


class ShiftSequenceShiftCreateForm(ModelForm):
    """Shift Sequence Shift Create Form."""

    class Meta:
        """Meta."""

        model = ShiftSequenceShift
        fields = ("shift", "position")

    def __init__(self, *args, **kwargs):
        """Set empty label."""
        super().__init__(*args, **kwargs)
        self.fields["shift"].empty_label = "X"
