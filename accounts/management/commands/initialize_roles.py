from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group, User
from django.contrib.contenttypes.models import ContentType
from documents.models import Document, Workflow

class Command(BaseCommand):
    help = 'Initialiser les rôles et ajouter un utilisateur aux groupes'

    def handle(self, *args, **kwargs):
        # Créer les groupes s'ils n'existent pas
        admin_group, _ = Group.objects.get_or_create(name='Administrators')
        manager_group, _ = Group.objects.get_or_create(name='Managers')
        employee_group, _ = Group.objects.get_or_create(name='Employees')

        # Créer l'utilisateur ou le récupérer s'il existe déjà
        user, created = User.objects.get_or_create(
            username='bouthaina',  # Remplace par le vrai nom d'utilisateur
            defaults={
                'email': 'bouthainabouchagraoui@gmail.com',  # Remplace par l'email réel
                'password': 'changeme'  # Utilise une méthode sécurisée pour définir le mot de passe
            }
        )
        
        # Set up content types
        document_ct = ContentType.objects.get_for_model(Document)
        workflow_ct = ContentType.objects.get_for_model(Workflow)
        
        # Fetch permissions
        admin_permissions = Permission.objects.filter(content_type__in=[document_ct, workflow_ct])

        # Manager permissions: Can manage workflows, but also change documents
        manager_permissions = Permission.objects.filter(
            content_type=document_ct,
            codename='change_document'
        ) | Permission.objects.filter(content_type=workflow_ct)  # Add workflow-related permissions

        # Employee permissions: Limited to uploading, viewing, changing, and deleting their own documents
        employee_permissions = Permission.objects.filter(
            content_type=document_ct,
            codename__in=['add_document', 'view_document', 'change_document', 'delete_document']
        )| Permission.objects.filter(content_type=workflow_ct, codename='change_workflow')

        # Set permissions for each group
        admin_group.permissions.set(admin_permissions)
        manager_group.permissions.set(manager_permissions)
        employee_group.permissions.set(employee_permissions)

        print("Permissions and groups have been set up successfully.")

        # Assigner l'utilisateur au groupe Administrators
        user.groups.add(admin_group)

        # Afficher le résultat
        self.stdout.write(self.style.SUCCESS(f"Utilisateur {'créé' if created else 'récupéré'} et ajouté au groupe Administrators."))
