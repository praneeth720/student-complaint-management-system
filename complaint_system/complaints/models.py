from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Complaint(models.Model):

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        RESOLVED = 'resolved', 'Resolved'
        ESCALATED = 'escalated', 'Escalated'
        CLOSED = 'closed', 'Closed'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_complaints',
        limit_choices_to={'role': 'student'}
    )

    assigned_staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_complaints',
        limit_choices_to={'role': 'staff'}
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='complaints'
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        db_index=True
    )

    solution = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    sla_deadline = models.DateTimeField(null=True, blank=True)
    is_sla_breached = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.title}"

    def save(self, *args, **kwargs):
        creating = self.pk is None

        if creating and not self.sla_deadline:
            from .models import SLA
            sla = SLA.objects.filter(
                priority=self.priority,
                is_active=True
            ).first()

            if sla:
                self.sla_deadline = timezone.now() + timedelta(
                    hours=sla.resolution_time_hours
                )

        if self.status == self.Status.RESOLVED and not self.resolved_at:
            self.resolved_at = timezone.now()

        if (
            self.sla_deadline
            and self.status not in [self.Status.RESOLVED, self.Status.CLOSED]
            and timezone.now() > self.sla_deadline
        ):
            self.is_sla_breached = True

        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return (
            self.sla_deadline
            and self.status not in [self.Status.RESOLVED, self.Status.CLOSED]
            and timezone.now() > self.sla_deadline
        )


class SLA(models.Model):
    name = models.CharField(max_length=100)
    priority = models.CharField(
        max_length=10,
        choices=Complaint.Priority.choices,
        unique=True
    )
    response_time_hours = models.PositiveIntegerField()
    resolution_time_hours = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.priority})"


class Escalation(models.Model):

    class Reason(models.TextChoices):
        SLA_BREACH = 'sla_breach', 'SLA Breach'
        CUSTOMER_REQUEST = 'customer_request', 'Customer Request'
        COMPLEXITY = 'complexity', 'High Complexity'
        UNRESOLVED = 'unresolved', 'Unresolved'
        OTHER = 'other', 'Other'

    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='escalations'
    )

    escalated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='escalations_made'
    )

    escalated_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='escalations_received'
    )

    reason = models.CharField(max_length=20, choices=Reason.choices)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.complaint.status = Complaint.Status.ESCALATED
            self.complaint.save(update_fields=['status'])

        if self.resolved and not self.resolved_at:
            self.resolved_at = timezone.now()

        super().save(*args, **kwargs)


class ComplaintComment(models.Model):
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    content = models.TextField()
    is_internal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
