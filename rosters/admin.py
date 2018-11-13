"""Admin module."""
from django.contrib import admin

from .models import (
    Leave,
    Role,
    Shift,
    ShiftRule,
    ShiftRuleRole,
    StaffRule,
    StaffRuleShift,
    TimeSlot,
)

admin.site.register(Leave)
admin.site.register(Role)
admin.site.register(Shift)
admin.site.register(ShiftRule)
admin.site.register(ShiftRuleRole)
admin.site.register(StaffRule)
admin.site.register(StaffRuleShift)
admin.site.register(TimeSlot)


# class CommentInLine(admin.TabularInline):
#     model = Comment
#
#
# class ArticleAdmin(admin.ModelAdmin):
#     inlines = [
#         CommentInLine,
#     ]
#
# admin.site.register(Article, ArticleAdmin)
# admin.site.register(Comment)
