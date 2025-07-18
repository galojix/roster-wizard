"""URLs."""

from django.urls import path

from .views import (
    LeaveListView,
    LeaveUpdateView,
    LeaveDetailView,
    LeaveDeleteView,
    LeaveCreateView,
    RoleListView,
    RoleUpdateView,
    RoleDetailView,
    RoleDeleteView,
    RoleCreateView,
    RosterSettingsView,
    ShiftListView,
    ShiftUpdateView,
    ShiftDetailView,
    ShiftDeleteView,
    ShiftCreateView,
    ShiftRuleListView,
    ShiftRuleUpdateView,
    ShiftRuleDetailView,
    ShiftRuleDeleteView,
    ShiftRuleCreateView,
    ShiftRuleRoleListView,
    ShiftRuleRoleUpdateView,
    ShiftRuleRoleDetailView,
    ShiftRuleRoleDeleteView,
    ShiftRuleRoleCreateView,
    StaffRuleListView,
    StaffRuleUpdateView,
    StaffRuleDetailView,
    StaffRuleDeleteView,
    StaffRuleCreateView,
    StaffRuleShiftListView,
    StaffRuleShiftUpdateView,
    StaffRuleShiftDetailView,
    StaffRuleShiftDeleteView,
    StaffRuleShiftCreateView,
    TimeSlotListView,
    TimeSlotUpdateView,
    TimeSlotDetailView,
    TimeSlotDeleteView,
    TimeSlotCreateView,
    GenerateRosterView,
    edit_roster,
    SelectRosterPeriodView,
    SelectBulkDeletionPeriodView,
    RosterByStaffView,
    StaffRequestListView,
    StaffRequestDeleteView,
    StaffRequestCreateView,
    StaffRequestUpdateView,
    StaffRequestDetailView,
    download_csv,
    DayGroupListView,
    DayGroupUpdateView,
    DayGroupDetailView,
    DayGroupDeleteView,
    DayGroupCreateView,
    DayGroupDayListView,
    DayGroupDayUpdateView,
    DayGroupDayDetailView,
    DayGroupDayDeleteView,
    DayGroupDayCreateView,
    DayListView,
    DayUpdateView,
    DayDetailView,
    DayDeleteView,
    DayCreateView,
    DaySetCreateView,
    roster_generation_status,
    staff_request_status,
)

urlpatterns = [
    path(
        "leave/<int:pk>/update/",
        LeaveUpdateView.as_view(),
        name="leave_update",
    ),
    path("leave/<int:pk>/", LeaveDetailView.as_view(), name="leave_detail"),
    path(
        "leave/<int:pk>/delete/",
        LeaveDeleteView.as_view(),
        name="leave_delete",
    ),
    path("leave/create/", LeaveCreateView.as_view(), name="leave_create"),
    path("leave/", LeaveListView.as_view(), name="leave_list"),
    path("role/<int:pk>/update/", RoleUpdateView.as_view(), name="role_update"),
    path("role/<int:pk>/", RoleDetailView.as_view(), name="role_detail"),
    path("role/<int:pk>/delete/", RoleDeleteView.as_view(), name="role_delete"),
    path("role/create/", RoleCreateView.as_view(), name="role_create"),
    path("role/", RoleListView.as_view(), name="role_list"),
    path(
        "shift/<int:pk>/update/",
        ShiftUpdateView.as_view(),
        name="shift_update",
    ),
    path("shift/<int:pk>/", ShiftDetailView.as_view(), name="shift_detail"),
    path(
        "shift/<int:pk>/delete/",
        ShiftDeleteView.as_view(),
        name="shift_delete",
    ),
    path("shift/create/", ShiftCreateView.as_view(), name="shift_create"),
    path("shift/", ShiftListView.as_view(), name="shift_list"),
    path(
        "shiftrule/<int:pk>/update/",
        ShiftRuleUpdateView.as_view(),
        name="shiftrule_update",
    ),
    path(
        "shiftrule/<int:pk>/",
        ShiftRuleDetailView.as_view(),
        name="shiftrule_detail",
    ),
    path(
        "shiftrule/<int:pk>/delete/",
        ShiftRuleDeleteView.as_view(),
        name="shiftrule_delete",
    ),
    path(
        "shiftrule/create/",
        ShiftRuleCreateView.as_view(),
        name="shiftrule_create",
    ),
    path("shiftrule/", ShiftRuleListView.as_view(), name="shiftrule_list"),
    path(
        "shiftrulerole/<int:pk>/update/",
        ShiftRuleRoleUpdateView.as_view(),
        name="shiftrulerole_update",
    ),
    path(
        "shiftrulerole/<int:pk>/",
        ShiftRuleRoleDetailView.as_view(),
        name="shiftrulerole_detail",
    ),
    path(
        "shiftrulerole/<int:pk>/delete/",
        ShiftRuleRoleDeleteView.as_view(),
        name="shiftrulerole_delete",
    ),
    path(
        "shiftrulerole/<int:shiftrule>/create/",
        ShiftRuleRoleCreateView.as_view(),
        name="shiftrulerole_create",
    ),
    path(
        "shiftrulerole/",
        ShiftRuleRoleListView.as_view(),
        name="shiftrulerole_list",
    ),
    path(
        "staffrule/<int:pk>/update/",
        StaffRuleUpdateView.as_view(),
        name="staffrule_update",
    ),
    path(
        "staffrule/<int:pk>/",
        StaffRuleDetailView.as_view(),
        name="staffrule_detail",
    ),
    path(
        "staffrule/<int:pk>/delete/",
        StaffRuleDeleteView.as_view(),
        name="staffrule_delete",
    ),
    path(
        "staffrule/create/",
        StaffRuleCreateView.as_view(),
        name="staffrule_create",
    ),
    path("staffrule/", StaffRuleListView.as_view(), name="staffrule_list"),
    path(
        "staffruleshift/<int:pk>/update/",
        StaffRuleShiftUpdateView.as_view(),
        name="staffruleshift_update",
    ),
    path(
        "staffruleshift/<int:pk>/",
        StaffRuleShiftDetailView.as_view(),
        name="staffruleshift_detail",
    ),
    path(
        "staffruleshift/<int:pk>/delete/",
        StaffRuleShiftDeleteView.as_view(),
        name="staffruleshift_delete",
    ),
    path(
        "staffruleshift/<int:staffrule>/create/",
        StaffRuleShiftCreateView.as_view(),
        name="staffruleshift_create",
    ),
    path(
        "staffruleshift/",
        StaffRuleShiftListView.as_view(),
        name="staffruleshift_list",
    ),
    path(
        "timeslot/<int:pk>/update/",
        TimeSlotUpdateView.as_view(),
        name="timeslot_update",
    ),
    path(
        "timeslot/<int:pk>/",
        TimeSlotDetailView.as_view(),
        name="timeslot_detail",
    ),
    path(
        "timeslot/<int:pk>/delete/",
        TimeSlotDeleteView.as_view(),
        name="timeslot_delete",
    ),
    path(
        "timeslot/create/",
        TimeSlotCreateView.as_view(),
        name="timeslot_create",
    ),
    path("timeslot/", TimeSlotListView.as_view(), name="timeslot_list"),
    path("daygroup/", DayGroupListView.as_view(), name="daygroup_list"),
    path(
        "daygroup/<int:pk>/update/",
        DayGroupUpdateView.as_view(),
        name="daygroup_update",
    ),
    path(
        "daygroup/<int:pk>/",
        DayGroupDetailView.as_view(),
        name="daygroup_detail",
    ),
    path(
        "daygroup/<int:pk>/delete/",
        DayGroupDeleteView.as_view(),
        name="daygroup_delete",
    ),
    path(
        "daygroup/create/",
        DayGroupCreateView.as_view(),
        name="daygroup_create",
    ),
    path(
        "daygroupday/",
        DayGroupDayListView.as_view(),
        name="daygroupday_list",
    ),
    path(
        "daygroupday/<int:pk>/update/",
        DayGroupDayUpdateView.as_view(),
        name="daygroupday_update",
    ),
    path(
        "daygroupday/<int:pk>/",
        DayGroupDayDetailView.as_view(),
        name="daygroupday_detail",
    ),
    path(
        "daygroupday/<int:pk>/delete/",
        DayGroupDayDeleteView.as_view(),
        name="daygroupday_delete",
    ),
    path(
        "daygroupday/<int:daygroup>/create/",
        DayGroupDayCreateView.as_view(),
        name="daygroupday_create",
    ),
    path(
        "daygroupday/",
        DayGroupDayListView.as_view(),
        name="daygroupday_list",
    ),
    path("day/<int:pk>/update/", DayUpdateView.as_view(), name="day_update"),
    path("day/<int:pk>/", DayDetailView.as_view(), name="day_detail"),
    path("day/<int:pk>/delete/", DayDeleteView.as_view(), name="day_delete"),
    path("day/create/", DayCreateView.as_view(), name="day_create"),
    path("day/", DayListView.as_view(), name="day_list"),
    path("day_set/create", DaySetCreateView.as_view(), name="day_set_create"),
    path(
        "staffrequest/<int:pk>/delete/",
        StaffRequestDeleteView.as_view(),
        name="staffrequest_delete",
    ),
    path(
        "staffrequest/create/",
        StaffRequestCreateView.as_view(),
        name="staffrequest_create",
    ),
    path(
        "staffrequest/",
        StaffRequestListView.as_view(),
        name="staffrequest_list",
    ),
    path(
        "staffrequest/<int:staffid>/update/",
        StaffRequestUpdateView.as_view(),
        name="staffrequest_update",
    ),
    path(
        "staffrequest/",
        StaffRequestListView.as_view(),
        name="staffrequest_list",
    ),
    path(
        "staffrequest/<int:pk>/",
        StaffRequestDetailView.as_view(),
        name="staffrequest_detail",
    ),
    path("roster_by_staff/", RosterByStaffView.as_view(), name="roster_by_staff"),
    path(
        "select_roster_period/",
        SelectRosterPeriodView.as_view(),
        name="select_roster_period",
    ),
    path(
        "select_bulk_deletion_period/",
        SelectBulkDeletionPeriodView.as_view(),
        name="select_bulk_deletion_period",
    ),
    path(
        "generate_roster/",
        GenerateRosterView.as_view(),
        name="generate_roster",
    ),
    path(
        "edit_roster/",
        edit_roster,
        name="edit_roster",
    ),
    path("download_csv/", download_csv, name="download_csv"),
    path(
        "roster_status/<str:task_id>/",
        roster_generation_status,
        name="roster_generation_status",
    ),
    path(
        "roster_settings/",
        RosterSettingsView.as_view(),
        name="roster_settings",
    ),
    path(
        "staff_request_status/",
        staff_request_status,
        name="staff_request_status",
    ),
]
