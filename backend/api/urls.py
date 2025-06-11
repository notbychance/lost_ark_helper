from api.addons.router import CustomRouter

from .views import *

router = CustomRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'group', GroupViewSet, basename='group')
