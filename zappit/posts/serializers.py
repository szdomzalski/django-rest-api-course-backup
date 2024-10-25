from rest_framework import serializers

from .models import Post, Vote


class PostSerializer(serializers.ModelSerializer):
    poster = serializers.ReadOnlyField(source='poster.email')
    poster_id = serializers.ReadOnlyField(source='poster.pk')
    votes = serializers.SerializerMethodField('get_votes')

    class Meta:
        model = Post
        fields = ('id', 'title', 'url', 'poster_id', 'poster', 'created', 'votes')

    def get_votes(self, post: Post) -> int:
        return Vote.objects.filter(post=post).count()


class VoteSerializer(serializers.ModelSerializer):
    # poster = serializers.ReadOnlyField(source='poster.email')
    # poster_id = serializers.ReadOnlyField(source='poster.pk')

    class Meta:
        model = Vote
        fields = ('id',)
