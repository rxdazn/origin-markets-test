from rest_framework import routers
from bonds import views

router = routers.SimpleRouter()
router.register("bonds", views.BondViewSet, "bonds")

urlpatterns = router.urls
