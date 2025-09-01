from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import Category, Post, Comment
from .serializers import CategorySerializer, PostSerializer, CommentSerializer
from .permissions import IsAuthorOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-id")
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        qs = Post.objects.select_related('author', 'category').all()
        category = self.request.query_params.get('category')  # can be name or id
        q = self.request.query_params.get('q')  # search query
        if category:
            if category.isdigit():
                qs = qs.filter(category_id=category)
            else:
                qs = qs.filter(category__name__iexact=category)
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q))
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # Custom action for liking/unliking
    @action(detail=True, methods=["post"], url_path="like")
    def like_post(self, request, pk=None):
        post = self.get_object()
        user = request.user
        if user in post.likes.all():
            post.likes.remove(user)  # unlike
            return Response({"liked": False, "likes_count": post.likes.count()})
        else:
            post.likes.add(user)  # like
            return Response({"liked": True, "likes_count": post.likes.count()})
        
    @action(detail=True, methods=["get", "post"], url_path="comments",
            permission_classes=[IsAuthenticatedOrReadOnly])  # 👈 allow all logged-in users
    def comments(self, request, pk=None):
        post = self.get_object()
        if request.method == "GET":
            comments = Comment.objects.filter(post=post).order_by("-created_at")
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        elif request.method == "POST":
            if not request.user.is_authenticated:   # 👈 double check
                return Response({"detail": "Authentication required."}, status=403)
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(author=request.user, post=post)
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by("-created_at")
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
