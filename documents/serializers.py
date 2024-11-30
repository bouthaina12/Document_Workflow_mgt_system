from rest_framework import serializers
from .models import Document, Workflow

class DocumentSerializer(serializers.ModelSerializer):
   class Meta:
        model = Document
        fields = ['id', 'title', 'content', 'type', 'status', 'file', 'uploaded_by', 'workflows']
        read_only_fields = ['uploaded_by','type', 'content']  # These will be set automatically

class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = '__all__'