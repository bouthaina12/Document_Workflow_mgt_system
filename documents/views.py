from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import permission_required
from transformers import pipeline
import PyPDF2
from .models import Document, Workflow
from .serializers import DocumentSerializer, WorkflowSerializer
from django.core.exceptions import PermissionDenied

# Initialize the HuggingFace pipelines
classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')
summarizer = pipeline('summarization', model='sshleifer/distilbart-cnn-12-6')


def test_permission_view(request):
    user = request.user

    if user.has_perm('documents.change_workflow'):
        return HttpResponse("You have permission to change workflows.")
    raise PermissionDenied("You do not have permission to change workflows.")




class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
  
    def perform_create(self, serializer):
       
       
        # Check if the file is uploaded
        file = self.request.FILES.get('file')
        if not file:
            raise ValidationError("A file must be uploaded.")

        # Extract text from the PDF file
        pdf_reader = PyPDF2.PdfReader(file)
        document_content = ""
        for page in pdf_reader.pages:
            document_content += page.extract_text() or ""
        print("Extracted Content:", document_content)

        # Summarize the content using HuggingFace pipeline
        summarized_content = summarizer(document_content, max_length=10, min_length=5, do_sample=False)
        summary_text = summarized_content[0]['summary_text']

        # Classify the summarized content
        result = classifier(summary_text, candidate_labels=['Invoice', 'Contract', 'Report'])
        document_type = result['labels'][0]  # Get the most likely label

        # Save the document with extracted details
        serializer.save(
            uploaded_by=self.request.user,
            content=summary_text,
            type=document_type,
        )

    def get_queryset(self):
        user = self.request.user
        queryset = Document.objects.all()
        if user.groups.filter(name="Employees").exists():
            queryset = queryset.filter(uploaded_by=user)
        return queryset

    @permission_required('documents.change_document', raise_exception=True)
    def update_status(self, request, pk):
        document = get_object_or_404(Document, pk=pk)

        # Only managers and admins can update status
        if request.user.groups.filter(name__in=['Managers', 'Administrators']).exists():
            if request.method == 'POST':
                new_status = request.POST.get('status')
                if new_status in dict(Document.STATUS_CHOICES):
                    document.status = new_status
                    document.save()
                    return redirect('document_list')  # Correctly inside the method
                else:
                    return HttpResponseForbidden("Invalid status selected.")
        return HttpResponseForbidden("You don't have permission to update status.")

def delete_document(request, pk):
    document = get_object_or_404(Document, pk=pk)

    # Allow employees to delete their own documents
    if request.user == document.uploaded_by and request.user.has_perm('documents.delete_document'):
        document.delete()
        return redirect('document_list')  # Correctly inside the method

    return HttpResponseForbidden("You don't have permission to delete this document.")

class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='assign-workflow')
    def assign_to_workflow(self, request, pk=None):
        """Assigns a document to a specified workflow."""
        document = self.get_object()
        workflow_id = request.data.get('workflow_id')

        try:
            workflow = Workflow.objects.get(id=workflow_id)
            document.workflows.add(workflow)
            document.save()
            return Response({'message': f'Document {document.title} assigned to workflow {workflow.name}.'})
        except Workflow.DoesNotExist:
            return Response({'error': 'Workflow not found.'}, status=404)
