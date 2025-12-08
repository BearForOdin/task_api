from rest_framework import serializers
from .models import Task
from django.utils import timezone


class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    completed_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'owner', 'title', 'description', 'due_date',
            'priority', 'status', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['owner', 'created_at', 'updated_at', 'completed_at']

    def validate_due_date(self, value):
        if self.instance and self.partial:
            return value
        if value <= timezone.now():
            raise serializers.ValidationError("Due date must be in the future.")
        return value

    def update(self, instance, validated_data):
        new_status = validated_data.get('status', instance.status)

        # Cannot update completed task unless reverting to pending
        if instance.status == 'completed' and new_status != 'pending':
            raise serializers.ValidationError(
                "Completed tasks cannot be edited unless status is reverted to 'pending'."
            )

        # Reverted to pending
        if instance.status == 'completed' and new_status == 'pending':
            validated_data['completed_at'] = None

        # Mark as completed
        if new_status == 'completed' and instance.status != 'completed':
            validated_data['completed_at'] = timezone.now()

        return super().update(instance, validated_data)


class TaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['status']
