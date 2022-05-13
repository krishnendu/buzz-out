from rest_framework import routers
from chat.views import UserViewSet, RoomViewSet, MessageViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'messages', MessageViewSet)

urlpatterns = router.urls