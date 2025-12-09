from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Task
from .serializers import TaskSerializer, TaskStatusSerializer
from .permissions import IsOwner



class TaskViewSet(viewsets.ModelViewSet):

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsOwner]

    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['due_date', 'priority']

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.filter(owner=user)

        status_filter = self.request.GET.get("status")
        priority_filter = self.request.GET.get("priority")

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # Mark task complete/incomplete
    @action(detail=True, methods=['patch'])
    def status(self, request, pk=None):
        task = self.get_object()
        serializer = TaskStatusSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(TaskSerializer(task).data)
