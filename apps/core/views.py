from django.shortcuts import get_object_or_404, redirect
from inertia import render

from .forms import MovieForm
from .models import Movie


def movie_list(request):
    movies = Movie.objects.all()
    data = [movie.serializable_values(exclude=['added_at']) for movie in movies]
    return render(request, 'Movies/Index', props={
            'movies': data,
            'stats': {
                'total': movies.count(),
                'want': movies.filter(status='want').count(),
                'watching': movies.filter(status='watching').count(),
                'watched': movies.filter(status='watched').count(),
            },
        },
    )


def movie_create(request):
    form = MovieForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('movie_list')

    return render(request, 'Movies/Create', props={'errors': form.errors})


def movie_update(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    form = MovieForm(request.POST or None, instance=movie)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('movie_list')

    data = movie.serializable_values(exclude=['added_at'])
    return render(request, 'Movies/Edit', props={
            'movie': data,
            'errors': form.errors,
        },
    )


def movie_delete(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    movie.delete()
    return redirect('movie_list')
