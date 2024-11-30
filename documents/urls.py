from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet,WorkflowViewSet
from django.conf import settings


router = DefaultRouter()
router.register('documents', DocumentViewSet)
router.register('workflow', WorkflowViewSet)


urlpatterns = [
    path('', include(router.urls)),
]