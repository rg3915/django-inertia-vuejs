import json

from django.http import QueryDict
from django.shortcuts import get_object_or_404, redirect
from inertia import render

from .forms import MovieForm
from .models import Movie


def _get_post_data(request):
    """O Inertia v2 envia JSON, mas o Django ModelForm espera QueryDict."""
    if request.content_type == 'application/json':
        return QueryDict(mutable=True) | json.loads(request.body)
    return request.POST


def movie_list(request):
    movies = Movie.objects.all()
    data = [movie.serializable_values(exclude=['added_at']) for movie in movies]
    return render(
        request,
        'Movies/Index',
        props={
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
    data = _get_post_data(request) if request.method == 'POST' else None
    form = MovieForm(data)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('movie_list')

    return render(request, 'Movies/Create', props={'errors': form.errors})


def movie_update(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    data = _get_post_data(request) if request.method == 'POST' else None
    form = MovieForm(data, instance=movie)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('movie_list')

    data = movie.serializable_values(exclude=['added_at'])
    return render(
        request,
        'Movies/Edit',
        props={
            'movie': data,
            'errors': form.errors,
        },
    )


def movie_delete(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    movie.delete()
    return redirect('movie_list')
