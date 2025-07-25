"""Models."""

from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse


class RosterSettings(models.Model):
    """Roster settings."""

    roster_name = models.CharField(
        max_length=15, null=False, blank=False, default="No Roster Name Set"
    )
    not_used = models.CharField(
        max_length=15, null=False, blank=False, default="Not Used"
    )

    class Meta:
        """Permissions."""

        permissions = (("change_roster", "Can change rosters"),)


class LeaveManager(models.Manager):
    """Leave Manager."""

    def get_queryset(self):
        """Select additional related object data."""
        query_set = super().get_queryset()
        return query_set.select_related("staff_member")


class Leave(models.Model):
    """Leave."""

    objects = LeaveManager()
    date = models.DateField(null=False, blank=False)
    description = models.CharField(
        max_length=15, null=False, blank=False, default="Leave"
    )
    staff_member = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    class Meta:
        """Meta."""

        ordering = ("staff_member", "date")

    def __str__(self):
        """How a leave object is displayed."""
        return str(self.staff_member) + " " + str(self.date)

    def get_absolute_url(self):
        """URL."""
        return reverse("leave_detail", args=[str(self.id)])


class Role(models.Model):
    """Role (Designation/Level/Rank)."""

    role_name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        """Return a meaningful string representation."""
        return str(self.role_name)

    def get_absolute_url(self):
        """URL."""
        return reverse("role_detail", args=[str(self.id)])


class DayGroup(models.Model):
    """Day Group."""

    name = models.CharField(max_length=20, unique=True, null=False, blank=False)

    def __str__(self):
        """Return a meaningful string representation."""
        return str(self.name)

    def get_absolute_url(self):
        """URL."""
        return reverse("daygroup_detail", args=[str(self.id)])


class Day(models.Model):
    """Day."""

    number = models.IntegerField(null=False, blank=False)

    class Meta:
        """Meta."""

        ordering = ("number",)

    def __str__(self):
        """Return a meaningful string representation."""
        return str(self.number)

    def get_absolute_url(self):
        """URL."""
        return reverse("day_detail", args=[str(self.id)])


class DayGroupDayManager(models.Manager):
    """DayGroupDay Manager."""

    def get_queryset(self):
        """Select additional related object data."""
        query_set = super().get_queryset()
        return query_set.select_related("daygroup", "day")


class DayGroupDay(models.Model):
    """Day Group Day."""

    objects = DayGroupDayManager()
    daygroup = models.ForeignKey(DayGroup, on_delete=models.CASCADE)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)

    class Meta:
        """Meta."""

        ordering = ("day__number",)
        unique_together = (
            "daygroup",
            "day",
        )

    def __str__(self):
        """Return a meaningful string representation."""
        return str(self.daygroup.name) + str(self.day.number)

    def get_absolute_url(self):
        """URL."""
        return reverse("daygroupday_detail", args=[str(self.id)])


class ShiftManager(models.Manager):
    """Shift Manager."""

    def get_queryset(self):
        """Select additional related object data."""
        query_set = super().get_queryset()
        return query_set.select_related("daygroup")


class Shift(models.Model):
    """Shift."""

    objects = ShiftManager()
    shift_type = models.CharField(max_length=20, null=False, blank=False)
    daygroup = models.ForeignKey(
        DayGroup, null=True, blank=False, on_delete=models.SET_NULL
    )

    class Meta:
        """Meta."""

        ordering = ("shift_type",)

    def __str__(self):
        """Return a meaningful string representation."""
        return str(self.shift_type)

    def get_absolute_url(self):
        """URL."""
        return reverse("shift_detail", args=[str(self.id)])


class SkillMixRuleManager(models.Manager):
    """ShiftRule Manager."""

    def get_queryset(self):
        """Select additional related object data."""
        query_set = super().get_queryset()
        return query_set.select_related("shift").prefetch_related("roles")


class SkillMixRule(models.Model):
    """Skill Mix Rule."""

    objects = SkillMixRuleManager()
    skillmixrule_name = models.CharField(
        max_length=20, null=False, blank=False, unique=True
    )
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    roles = models.ManyToManyField(Role, through="SkillMixRuleRole")

    def __str__(self):
        """Return a meaningful string representation."""
        return str(self.skillmixrule_name)

    def get_absolute_url(self):
        """URL."""
        return reverse("skillmixrule_detail", args=[str(self.id)])


class SkillMixRuleRoleManager(models.Manager):
    """ShiftRuleRole Manager."""

    def get_queryset(self):
        """Select additional related object data."""
        query_set = super().get_queryset()
        return query_set.select_related("skillmixrule", "role")


class SkillMixRuleRole(models.Model):
    """SkillMixRuleRole."""

    objects = SkillMixRuleRoleManager()
    skillmixrule = models.ForeignKey(SkillMixRule, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    count = models.IntegerField(null=False, blank=False)

    def __str__(self):
        """Return a meaningful string representation."""
        return (
            self.skillmixrule.skillmixrule_name
            + " "
            + self.role.role_name
            + ":"
            + str(self.count)
        )

    def get_absolute_url(self):
        """Next URL to display after updating."""
        return reverse("skillmixrule_list")


class ShiftSequenceManager(models.Manager):
    """ShiftSequence Manager."""

    def get_queryset(self):
        """Select additional related object data."""
        query_set = super().get_queryset()
        return query_set.select_related("daygroup").prefetch_related("staff", "shifts")


class ShiftSequence(models.Model):
    """Shift Sequence Rule."""

    objects = ShiftSequenceManager()
    shiftsequence_name = models.CharField(max_length=40, null=False, blank=False)
    staff = models.ManyToManyField(get_user_model(), blank=True)
    shifts = models.ManyToManyField(Shift, through="ShiftSequenceShift")
    daygroup = models.ForeignKey(
        DayGroup, null=True, blank=False, on_delete=models.SET_NULL
    )

    def __str__(self):
        """Return a meaningful string representation."""
        return str(self.shiftsequence_name)

    def get_absolute_url(self):
        """URL."""
        return reverse("shiftsequence_detail", args=[str(self.id)])


class ShiftSequenceShiftManager(models.Manager):
    """ShiftSequenceShift Manager."""

    def get_queryset(self):
        """Select additional related object data."""
        query_set = super().get_queryset()
        return query_set.select_related("shiftsequence", "shift")


class ShiftSequenceShift(models.Model):
    """ShiftSequenceShift."""

    objects = ShiftSequenceShiftManager()
    shiftsequence = models.ForeignKey(ShiftSequence, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, null=True, blank=True)
    position = models.IntegerField(null=False, blank=False)

    class Meta:
        """Meta."""

        ordering = ("position", "shift__shift_type")

    def __str__(self):
        """Return a meaningful string representation."""
        shift_type = "X" if self.shift is None else self.shift.shift_type
        return (
            self.shiftsequence.shiftsequence_name
            + ":"
            + shift_type
            + ":"
            + str(self.position)
        )

    def get_absolute_url(self):
        """URL."""
        return reverse("shiftsequence_list")


class TimeSlotManager(models.Manager):
    """TimeSlot Manager."""

    def get_queryset(self):
        """Select additional related object data."""
        query_set = super().get_queryset()
        return query_set.select_related("shift").prefetch_related("staff")


class TimeSlot(models.Model):
    """Time Slot."""

    objects = TimeSlotManager()
    date = models.DateField(null=False, blank=False)
    staff = models.ManyToManyField(get_user_model())
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)

    class Meta:
        """Meta."""

        ordering = ("date", "shift__shift_type")

    def __str__(self):
        """Return a meaningful string representation."""
        return str(self.date) + ":" + self.shift.shift_type

    def get_absolute_url(self):
        """URL."""
        return reverse("timeslot_list")


class StaffRequestManager(models.Manager):
    """StaffRequest Manager."""

    def get_queryset(self):
        """Select additional related object data."""
        query_set = super().get_queryset()
        return query_set.select_related("shift", "staff_member")


class StaffRequest(models.Model):
    """StaffRequest."""

    objects = StaffRequestManager()
    priority = models.IntegerField(null=False, blank=False)
    date = models.DateField(null=False, blank=False)
    like = models.BooleanField(null=False, blank=False, default=True)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)

    staff_member = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    class Meta:
        """Meta."""

        ordering = ("staff_member", "date", "shift", "like")

    def __str__(self):
        """How a StaffRequest object is displayed."""
        return (
            str(self.staff_member)
            + " "
            + str(self.shift.shift_type)
            + " "
            + str(self.date)
        )

    def get_absolute_url(self):
        """URL."""
        return reverse("staffrequest_detail", args=[str(self.id)])
