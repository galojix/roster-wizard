"""Admin module."""
from django.contrib import admin

from .models import (
    Leave,
    Role,
    Shift,
    ShiftRule,
    StaffRule,
    TimeSlot,
)

admin.site.register(Leave)
admin.site.register(Role)
admin.site.register(Shift)
admin.site.register(ShiftRule)
admin.site.register(StaffRule)
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
