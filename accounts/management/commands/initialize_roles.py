from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User

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

        # Assigner l'utilisateur au groupe Administrators
        user.groups.add(admin_group)

        # Afficher le résultat
        self.stdout.write(self.style.SUCCESS(f"Utilisateur {'créé' if created else 'récupéré'} et ajouté au groupe Administrators."))
