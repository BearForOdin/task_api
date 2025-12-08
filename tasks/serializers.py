from rest_framework import serializers
from .models import Task, PRIORITY_CHOICES, STATUS_CHOICES
from django.utils import timezone

class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    priority = serializers.ChoiceField(choices=[c[0] for c in PRIORITY_CHOICES])
    status = serializers.ChoiceField(choices=[c[0] for c in STATUS_CHOICES], default='pending')
    completed_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'owner', 'title', 'description', 'due_date',
            'priority', 'status', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'completed_at', 'owner']

    def validate_due_date(self, value):
        # Ensure due date is in future
        if value <= timezone.now():
            raise serializers.ValidationError("Due date must be in the future.")
        return value

    def update(self, instance, validated_data):
        # Prevent editing completed tasks unless status is being reverted to 'pending'
        if instance.status == 'completed':
            # allow status change to pending, but disallow other fields changes
            new_status = validated_data.get('status', instance.status)
            if new_status != 'pending':
                raise serializers.ValidationError("Completed tasks cannot be edited unless reverted to 'pending'.")
            # If user wants to revert to pending, clear completed_at and allow other updates
        return super().update(instance, validated_data)

class TaskStatusSerializer(serializers.ModelSerializer):
    """
    Dedicated serializer for toggling status (complete/incomplete)
    """
    status = serializers.ChoiceField(choices=[c[0] for c in STATUS_CHOICES])
    class Meta:
        model = Task
        fields = ['status']
