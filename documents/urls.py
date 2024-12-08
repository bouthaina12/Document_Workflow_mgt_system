from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet,WorkflowViewSet, test_permission_view
from django.conf import settings


router = DefaultRouter()
router.register('documents', DocumentViewSet)
router.register('workflow', WorkflowViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('test-permission/', test_permission_view, name='test_permission'),


]