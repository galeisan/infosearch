from django.shortcuts import render
import sys
sys.path.append('../')
import task5
from .forms import SearchForm


def search_view(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = get_links(query)
            return render(request, 'web/search.html', {'form': form, 'results': results})
    else:
        form = SearchForm()
    return render(request, 'web/search.html', {'form': form})


def get_links(query):
    result_links = []
    try :
        result = task5.calculate_similarities(query)
        dict_items = result.items()
        with open('../pages/index.txt', 'r') as file:
            links = file.read().splitlines()
            for key, value in dict_items:
                if value > 0:
                    result_links.append(links[int(key) - 1].split(" ")[1])
        return result_links[:10]
    except Exception as e:
        return result_links
