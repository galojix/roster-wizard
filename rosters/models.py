"""Models."""
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse


class Leave(models.Model):
    """Leave."""

    date = models.DateField(null=False, blank=False)
    staff_member = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE
    )

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
    """Role."""

    role_name = models.CharField(max_length=50, null=False, blank=False)
    
    def __str__(self):
        """String."""
        return self.role_name

    def get_absolute_url(self):
        """URL."""
        return reverse("role_detail", args=[str(self.id)])


class Shift(models.Model):
    """Shift."""

    shift_type = models.CharField(max_length=20, null=False, blank=False)
    monday = models.BooleanField(null=False, blank=False, default=True)
    tuesday = models.BooleanField(null=False, blank=False, default=True)
    wednesday = models.BooleanField(null=False, blank=False, default=True)
    thursday = models.BooleanField(null=False, blank=False, default=True)
    friday = models.BooleanField(null=False, blank=False, default=True)
    saturday = models.BooleanField(null=False, blank=False, default=True)
    sunday = models.BooleanField(null=False, blank=False, default=True)

    def __str__(self):
        """String."""
        return self.shift_type

    def get_absolute_url(self):
        """URL."""
        return reverse("shift_detail", args=[str(self.id)])


class ShiftRule(models.Model):
    """Shift Rule."""

    shift_rule_name = models.CharField(
        max_length=20, null=False, blank=False, unique=True
    )
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    roles = models.ManyToManyField(Role, through="ShiftRuleRole")

    def __str__(self):
        """String."""
        return self.shift_rule_name

    def get_absolute_url(self):
        """URL."""
        return reverse("shift_rule_detail", args=[str(self.id)])


class ShiftRuleRole(models.Model):
    """ShiftRuleRole."""

    shift_rule = models.ForeignKey(ShiftRule, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    count = models.IntegerField(null=False, blank=False)

    def __str__(self):
        """String."""
        return self.shift_rule.shift_rule_name + self.role.role_name

    def get_absolute_url(self):
        """Next URL to display after updating."""
        return reverse("shift_rule_list")


class StaffRule(models.Model):
    """Staff Rule."""

    staff_rule_name = models.CharField(max_length=20, null=False, blank=False)
    staff = models.ManyToManyField(get_user_model())
    shifts = models.ManyToManyField(Shift, through="StaffRuleShift")

    def __str__(self):
        """String."""
        return self.staff_rule_name

    def get_absolute_url(self):
        """URL."""
        return reverse("staff_rule_detail", args=[str(self.id)])


class StaffRuleShift(models.Model):
    """StaffRuleShift."""

    staff_rule = models.ForeignKey(StaffRule, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    position = models.IntegerField(null=False, blank=False)

    def __str__(self):
        """String."""
        return (
            self.staff_rule.staff_rule_name
            + ":"
            + self.shift.shift_type
            + ":"
            + str(self.position)
        )

    def get_absolute_url(self):
        """URL."""
        return reverse("staff_rule_list")


class TimeSlot(models.Model):
    """Time Slot."""

    date = models.DateField(null=False, blank=False)
    staff = models.ManyToManyField(get_user_model())
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)

    def __str__(self):
        """String."""
        return str(self.date) + ":" + self.shift.shift_type

    def get_absolute_url(self):
        """URL."""
        return reverse("timeslot_list")


class Preference(models.Model):
    """Preference."""

    priority = models.IntegerField(null=False, blank=False)
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    staff_member = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE
    )

    def __str__(self):
        """How a preference object is displayed."""
        preference_display = (
            self.staff_member.last_name
            + ", "
            + self.staff_member.first_name
            + " "
            + self.timeslot.shift.shift_type
            + " "
            + str(self.timeslot.date)
        )
        return preference_display

    def get_absolute_url(self):
        """URL."""
        return reverse("preference_detail", args=[str(self.id)])
