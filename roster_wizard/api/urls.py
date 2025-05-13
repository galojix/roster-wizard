"""URLs."""

from rest_framework.routers import SimpleRouter
from .views import LeaveViewSet, TimeSlotViewSet, GenerateRosterViewSet

router = SimpleRouter()
router.register("leave", LeaveViewSet, basename="leave")
router.register("timeslots", TimeSlotViewSet, basename="timeslots")
router.register("generate", GenerateRosterViewSet, basename="generate")
urlpatterns = router.urls
