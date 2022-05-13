from rest_framework import routers

import chat.urls

router = routers.DefaultRouter()

router.registry.extend(chat.urls.router.registry)

urlpatterns = router.urls