from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task
from .serializers import TaskSerializer, TaskStatusSerializer
from .permissions import IsOwner

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['status', 'priority', 'due_date']
    ordering_fields = ['due_date', 'priority', 'created_at']

    def get_queryset(self):
        # Ensure users only see their own tasks
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'], url_path='set-status', serializer_class=TaskStatusSerializer)
    def set_status(self, request, pk=None):
        """
        Endpoint to mark as complete/incomplete.
        POST payload: {"status": "completed"} or {"status": "pending"}
        """
        task = self.get_object()
        serializer = self.get_serializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data['status']

        # If setting to completed: set completed_at in model save()
        if task.status == 'completed' and new_status == 'completed':
            return Response({"detail": "Task is already completed."}, status=status.HTTP_400_BAD_REQUEST)

        task.status = new_status
        task.save()
        return Response(TaskSerializer(task, context={'request': request}).data)
