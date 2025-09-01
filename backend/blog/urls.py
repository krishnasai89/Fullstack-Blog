from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, PostViewSet, CommentViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('posts', PostViewSet, basename='post')
router.register("comments", CommentViewSet, basename='comments')

urlpatterns = [
    path('', include(router.urls)),
]
