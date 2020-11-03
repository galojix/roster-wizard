"""URLs."""

from rest_framework.routers import SimpleRouter
from .views import LeaveViewSet, TimeSlotViewSet

router = SimpleRouter()
router.register("leaves", LeaveViewSet, basename="leaves")
router.register("timeslots", TimeSlotViewSet, basename="timeslots")
urlpatterns = router.urls
