"""Admin module."""

from django.contrib import admin
from rangefilter.filters import DateRangeFilter

from .models import (
    Leave,
    Role,
    Shift,
    SkillMixRule,
    SkillMixRuleRole,
    ShiftSequence,
    ShiftSequenceShift,
    TimeSlot,
    DayGroup,
    Day,
    DayGroupDay,
    StaffRequest,
)

admin.site.site_header = "Roster Wizard Database Administration"
admin.site.site_title = "Database Admin"
admin.site.index_title = "Roster"


class LeaveAdmin(admin.ModelAdmin):
    """Customise admin for Leave."""

    model = Leave
    list_display = (
        "date",
        "staff_member",
        "description",
    )
    list_filter = (
        ("date", DateRangeFilter),
        ("staff_member", admin.RelatedOnlyFieldListFilter),
    )


class TimeSlotAdmin(admin.ModelAdmin):
    """Customise admin for Timeslot."""

    model = TimeSlot
    list_display = (
        "date",
        "shift",
    )
    list_filter = (
        ("date", DateRangeFilter),
        ("shift", admin.RelatedOnlyFieldListFilter),
    )


class StaffRequestAdmin(admin.ModelAdmin):
    """Customise admin for StaffRequest."""

    model = StaffRequest
    list_display = (
        "date",
        "staff_member",
        "shift",
        "like",
        "priority",
    )
    list_filter = (
        ("date", DateRangeFilter),
        ("staff_member", admin.RelatedOnlyFieldListFilter),
    )


admin.site.register(Leave, LeaveAdmin)
admin.site.register(Role)
admin.site.register(Shift)
admin.site.register(SkillMixRule)
admin.site.register(SkillMixRuleRole)
admin.site.register(ShiftSequence)
admin.site.register(ShiftSequenceShift)
admin.site.register(TimeSlot, TimeSlotAdmin)
admin.site.register(DayGroup)
admin.site.register(Day)
admin.site.register(DayGroupDay)
admin.site.register(StaffRequest, StaffRequestAdmin)
