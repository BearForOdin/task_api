from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

User = settings.AUTH_USER_MODEL

PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
]

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('completed', 'Completed'),
]

class Task(models.Model):
    owner = models.ForeignKey(User, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['due_date', '-priority']

    def clean(self):
        # Ensure due_date is in the future on creation and update unless already completed
        if self.due_date <= timezone.now():
            raise ValidationError({'due_date': 'Due date must be in the future.'})
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()

    def save(self, *args, **kwargs):
        # If status changed to completed and completed_at not set -> set it.
        if self.status == 'completed' and self.completed_at is None:
            self.completed_at = timezone.now()
        # If status is pending, clear completed_at
        if self.status == 'pending' and self.completed_at is not None:
            self.completed_at = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} ({self.owner})'

