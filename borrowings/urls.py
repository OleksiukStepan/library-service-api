from rest_framework.routers import DefaultRouter
from borrowings.views import BorrowingViewSet


router = DefaultRouter()
router.register("", BorrowingViewSet, basename="borrowings")

urlpatterns = router.urls

app_name = "borrowings"
