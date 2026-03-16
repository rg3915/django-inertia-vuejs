import json

from django.http import QueryDict
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from inertia import render

from .forms import MovieForm
from .models import Movie


def _get_post_data(request):
    """O Inertia v2 envia JSON, mas o Django ModelForm espera QueryDict."""
    if request.content_type == 'application/json':
        return QueryDict(mutable=True) | json.loads(request.body)
    return request.POST


def _index_props():
    """Props comuns para a página Index."""
    movies = Movie.objects.all()
    data = [movie.serializable_values(exclude=['added_at']) for movie in movies]
    return {
        'movies': data,
        'stats': {
            'total': movies.count(),
            'want': movies.filter(status='want').count(),
            'watching': movies.filter(status='watching').count(),
            'watched': movies.filter(status='watched').count(),
        },
    }


def movie_list(request):
    return render(request, 'Movies/Index', props=_index_props())


def movie_create(request):
    data = _get_post_data(request)
    form = MovieForm(data)

    if form.is_valid():
        form.save()
        messages.success(request, 'Filme criado com sucesso!')
        return redirect('movie_list')

    props = _index_props()
    props['errors'] = form.errors
    props['showDialog'] = 'create'
    props['formData'] = dict(data)
    return render(request, 'Movies/Index', props=props)


def movie_update(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    data = _get_post_data(request)
    form = MovieForm(data, instance=movie)

    if form.is_valid():
        form.save()
        messages.success(request, 'Filme atualizado com sucesso!')
        return redirect('movie_list')

    props = _index_props()
    props['errors'] = form.errors
    props['showDialog'] = 'edit'
    props['editMovie'] = movie.serializable_values(exclude=['added_at'])
    props['formData'] = dict(data)
    return render(request, 'Movies/Index', props=props)


def movie_delete(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    movie.delete()
    messages.success(request, 'Filme excluído com sucesso!')
    return redirect('movie_list')
