from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage

class Workflow(models.Model):
    STEP_CHOICES = [
        ('Pending', 'Pending'),
        ('Under Review', 'Under Review'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    
    step = models.CharField(max_length=50, choices=STEP_CHOICES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Step: {self.step} - {self.name}"
    
class Document(models.Model):
    DOCUMENT_TYPES = [
        ('Invoice', 'Invoice'),
        ('Contract', 'Contract'),
        ('Report', 'Report'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Modification Requested', 'Modification Requested'),
    ]
    
    title = models.CharField(max_length=255)
    content = models.TextField()
    type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    workflows = models.ManyToManyField('Workflow', related_name='documents')

    file = models.FileField(upload_to='documents/', null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
fs = FileSystemStorage(location='uploads/')  # Change path as needed
