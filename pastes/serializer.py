from rest_framework import serializers

class PasteCreateSerializer(serializers.Serializer):
    content = serializers.CharField(allow_blank=False)
    ttl_seconds = serializers.IntegerField(required=False, min_value=1)
    max_views = serializers.IntegerField(required=False, min_value=1)
