from django.core.management.base import BaseCommand

from apps.core.models import Movie

# Os três primeiros são os filmes que aparecem no slide "Um exemplo do dia a dia".
# São todos do Tarantino de propósito: na demo, digitar "tarantino" na busca
# filtra a lista em tempo real, sem nenhuma ida ao servidor.
MOVIES = [
    {
        'title': 'Pulp Fiction',
        'director': 'Quentin Tarantino',
        'year': 1994,
        'genre': 'Crime',
        'rating': 5,
        'status': Movie.Status.WATCHED,
    },
    {
        'title': 'Kill Bill',
        'director': 'Quentin Tarantino',
        'year': 2003,
        'genre': 'Ação',
        'rating': 4,
        'status': Movie.Status.WATCHING,
    },
    {
        'title': 'Django Livre',
        'director': 'Quentin Tarantino',
        'year': 2012,
        'genre': 'Faroeste',
        'rating': None,
        'status': Movie.Status.WANT,
    },
    {
        'title': 'Cidade de Deus',
        'director': 'Fernando Meirelles',
        'year': 2002,
        'genre': 'Drama',
        'rating': 5,
        'status': Movie.Status.WATCHED,
    },
    {
        'title': 'Parasita',
        'director': 'Bong Joon-ho',
        'year': 2019,
        'genre': 'Suspense',
        'rating': 5,
        'status': Movie.Status.WATCHED,
    },
    {
        'title': 'Duna: Parte Dois',
        'director': 'Denis Villeneuve',
        'year': 2024,
        'genre': 'Ficção Científica',
        'rating': 4,
        'status': Movie.Status.WATCHING,
    },
    {
        'title': 'O Auto da Compadecida',
        'director': 'Guel Arraes',
        'year': 2000,
        'genre': 'Comédia',
        'rating': 5,
        'status': Movie.Status.WATCHED,
    },
    {
        'title': 'Ainda Estou Aqui',
        'director': 'Walter Salles',
        'year': 2024,
        'genre': 'Drama',
        'rating': None,
        'status': Movie.Status.WANT,
    },
]


class Command(BaseCommand):
    help = 'Popula o banco com os filmes usados na demonstração da palestra.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Apaga todos os filmes antes de popular.',
        )

    def handle(self, *args, **options):
        if options['clear']:
            deleted, _ = Movie.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'{deleted} filme(s) removido(s).'))

        created = 0
        for data in MOVIES:
            _, was_created = Movie.objects.get_or_create(
                title=data['title'], defaults=data
            )
            created += was_created

        self.stdout.write(
            self.style.SUCCESS(
                f'{created} filme(s) criado(s). Total: {Movie.objects.count()}.'
            )
        )
