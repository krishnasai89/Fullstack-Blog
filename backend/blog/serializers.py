from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Post, Comment

class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "author", "author", "content", "created_at"]
        read_only_fields = ["author", "created_at"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')

class PostSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    likes_count = serializers.IntegerField(source="total_likes", read_only=True)
    comments_count = serializers.IntegerField(source="comments.count",read_only= True)

    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'author', 'category', 'category_id', 'created_at', 'updated_at', 'likes_count', "comments_count")

