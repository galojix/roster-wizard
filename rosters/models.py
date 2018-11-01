"""Models."""
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse


class Leave(models.Model):
    """Leave."""

    date = models.DateField(null=False, blank=False)
    staff_member = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )

    def __str__(self):
        """String."""
        return self.date

    def get_absolute_url(self):
        """URL."""
        return reverse('leave_detail', args=[str(self.id)])


class Role(models.Model):
    """Role."""

    role_name = models.CharField(max_length=50, null=False, blank=False)
    staff = models.ManyToManyField(get_user_model())

    def __str__(self):
        """String."""
        return self.role_name

    def get_absolute_url(self):
        """URL."""
        return reverse('role_detail', args=[str(self.id)])


class Shift(models.Model):
    """Shift."""

    shift_type = models.CharField(max_length=20, null=False, blank=False)
    days_of_week = models.CharField(max_length=20, null=False, blank=False)

    def __str__(self):
        """String."""
        return self.shift_type

    def get_absolute_url(self):
        """URL."""
        return reverse('shift_detail', args=[str(self.id)])


class ShiftRule(models.Model):
    """Shift Rule."""

    shift_rule_name = models.CharField(max_length=20, null=False, blank=False)
    hard_constraint = models.BooleanField(null=False, blank=False)
    shift = models.ForeignKey(
        Shift,
        on_delete=models.CASCADE,
    )
    roles = models.ManyToManyField(Role, through='ShiftRuleRole')

    def __str__(self):
        """String."""
        return self.shift_rule_name

    def get_absolute_url(self):
        """URL."""
        return reverse('shift_rule_detail', args=[str(self.id)])


class ShiftRuleRole(models.Model):
    """ShiftRuleRole."""

    shift_rule = models.ForeignKey(ShiftRule, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    count = models.IntegerField(null=False, blank=False)

    def __str__(self):
        """String."""
        return self.shift_rule.shift_rule_name + self.role.role_name


class StaffRule(models.Model):
    """Staff Rule."""

    staff_rule_name = models.CharField(max_length=20, null=False, blank=False)
    hard_constraint = models.BooleanField(null=False, blank=False)
    staff = models.ManyToManyField(get_user_model())
    shifts = models.ManyToManyField(Shift, through='StaffRuleShift')

    def __str__(self):
        """String."""
        return self.staff_rule_name

    def get_absolute_url(self):
        """URL."""
        return reverse('staff_rule_detail', args=[str(self.id)])


class StaffRuleShift(models.Model):
    """StaffRuleShift."""

    staff_rule = models.ForeignKey(StaffRule, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    position = models.IntegerField(null=False, blank=False)

    def __str__(self):
        """String."""
        return self.staff_rule.staff_rule_name + self.shift.shift_name


class TimeSlot(models.Model):
    """Time Slot."""

    date = models.DateField(null=False, blank=False)
    staff = models.ManyToManyField(get_user_model())
    shifts = models.ManyToManyField(Shift)

    def __str__(self):
        """String."""
        return self.date

    def get_absolute_url(self):
        """URL."""
        return reverse('timeslot_detail', args=[str(self.id)])
