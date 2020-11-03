"""URLs."""

from rest_framework.routers import SimpleRouter
from .views import LeaveViewSet, TimeSlotViewSet

router = SimpleRouter()
router.register("leave", LeaveViewSet, basename="leave")
router.register("timeslots", TimeSlotViewSet, basename="timeslots")
urlpatterns = router.urls
