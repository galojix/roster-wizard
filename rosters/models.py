"""Models."""

from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse


class Leave(models.Model):
    """Leave."""

    date = models.DateField(null=False, blank=False)
    description = models.CharField(
        max_length=15, null=False, blank=False, default="Leave"
    )
    staff_member = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE
    )

    class Meta:
        """Meta."""

        ordering = ("staff_member", "date")

    def __str__(self):
        """How a leave object is displayed."""
        leave_display = (
            self.staff_member.last_name
            + ", "
            + self.staff_member.first_name
            + " "
            + str(self.date)
        )
        return leave_display

    def get_absolute_url(self):
        """URL."""
        return reverse("leave_detail", args=[str(self.id)])


class Role(models.Model):
    """Role (Designation/Level/Rank)."""

    role_name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        """Return a meaningful string representation."""
        return self.role_name

    def get_absolute_url(self):
        """URL."""
        return reverse("role_detail", args=[str(self.id)])


class DayGroup(models.Model):
    """Day Group."""

    name = models.CharField(max_length=20, null=False, blank=False)

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


class DayGroupDay(models.Model):
    """Day Group Day."""

    daygroup = models.ForeignKey(DayGroup, on_delete=models.CASCADE)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)

    class Meta:
        """Meta."""

        ordering = ("day__number",)

    def __str__(self):
        """Return a meaningful string representation."""
        return str(self.daygroup.name) + str(self.day.number)

    def get_absolute_url(self):
        """URL."""
        return reverse("daygroupday_detail", args=[str(self.id)])


class Shift(models.Model):
    """Shift."""

    shift_type = models.CharField(max_length=20, null=False, blank=False)
    daygroup = models.ForeignKey(
        DayGroup, null=True, blank=False, on_delete=models.SET_NULL
    )
    max_staff = models.IntegerField(null=False, blank=False, default=5)

    class Meta:
        """Meta."""

        ordering = ("shift_type",)

    def __str__(self):
        """Return a meaningful string representation."""
        return self.shift_type

    def get_absolute_url(self):
        """URL."""
        return reverse("shift_detail", args=[str(self.id)])


class ShiftRule(models.Model):
    """Shift Rule (Skill Mix Rule)."""

    shiftrule_name = models.CharField(
        max_length=20, null=False, blank=False, unique=True
    )
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    roles = models.ManyToManyField(Role, through="ShiftRuleRole")

    def __str__(self):
        """Return a meaningful string representation."""
        return self.shiftrule_name

    def get_absolute_url(self):
        """URL."""
        return reverse("shiftrule_detail", args=[str(self.id)])


class ShiftRuleRole(models.Model):
    """ShiftRuleRole."""

    shiftrule = models.ForeignKey(ShiftRule, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    count = models.IntegerField(null=False, blank=False)

    def __str__(self):
        """Return a meaningful string representation."""
        return (
            self.shiftrule.shiftrule_name
            + " "
            + self.role.role_name
            + ":"
            + str(self.count)
        )

    def get_absolute_url(self):
        """Next URL to display after updating."""
        return reverse("shiftrule_list")


class StaffRule(models.Model):
    """Staff Rule (Shift Sequence Rule)."""

    staffrule_name = models.CharField(max_length=40, null=False, blank=False)
    staff = models.ManyToManyField(get_user_model(), blank=True)
    shifts = models.ManyToManyField(Shift, through="StaffRuleShift")
    daygroup = models.ForeignKey(
        DayGroup, null=True, blank=False, on_delete=models.SET_NULL
    )

    def __str__(self):
        """Return a meaningful string representation."""
        return self.staff_name

    def get_absolute_url(self):
        """URL."""
        return reverse("staffrule_detail", args=[str(self.id)])


class StaffRuleShift(models.Model):
    """StaffRuleShift."""

    staffrule = models.ForeignKey(StaffRule, on_delete=models.CASCADE)
    shift = models.ForeignKey(
        Shift, on_delete=models.CASCADE, null=True, blank=True
    )
    position = models.IntegerField(null=False, blank=False)

    class Meta:
        """Meta."""

        ordering = ("position", "shift__shift_type")

    def __str__(self):
        """Return a meaningful string representation."""
        return (
            self.staffrule.staff_name
            + ":"
            + self.shift.shift_type
            + ":"
            + str(self.position)
        )

    def get_absolute_url(self):
        """URL."""
        return reverse("staffrule_list")


class TimeSlot(models.Model):
    """Time Slot."""

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


class StaffRequest(models.Model):
    """StaffRequest."""

    priority = models.IntegerField(null=False, blank=False)
    date = models.DateField(null=False, blank=False)
    like = models.BooleanField(null=False, blank=False, default=True)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)

    staff_member = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE
    )

    class Meta:
        """Meta."""

        ordering = ("staff_member", "date", "shift", "like")

    def __str__(self):
        """How a StaffRequest object is displayed."""
        staff_request_display = (
            self.staff_member.last_name
            + ", "
            + self.staff_member.first_name
            + " "
            + self.shift.shift_type
            + " "
            + str(self.date)
        )
        return staff_request_display

    def get_absolute_url(self):
        """URL."""
        return reverse("staffrequest_detail", args=[str(self.id)])
