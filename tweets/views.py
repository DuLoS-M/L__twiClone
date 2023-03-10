from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, JsonResponse
from .models import Tweet
import random
from .forms import TweetForm
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# Create your views here.
def home_view(request, *args, **kwargs):
    return render(request, "pages/home.html", context={}, status=200)

@csrf_exempt
def tweet_create_view(request, *args, **kwargs):
    user = request.user
    if not request.user.is_authenticated:
        user = None
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({}, status=401)
        return redirect(settings.LOGIN_URL)
    form = TweetForm(request.POST or None)
    next_url = request.POST.get("next") or None
    print("next_url", next_url)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = user
        obj.save()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(obj.serialize(), status=201)
        if next_url != None:
            return redirect(next_url) 
        form = TweetForm()

    if form.errors:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(form.errors, status=400)

    return render(request, 'components/form.html', context={"form":form})

def tweet_detail_view(request, tweet_id, *args, **kwargs):
    data = {
        "id": tweet_id,
        #"image_path": obj.image.url
    }
    status = 200
    try:
        obj = Tweet.objects.get(id=tweet_id)
        data['content'] = obj.content
    except:
        data['message'] = "Not found"
        status = 404
    
    return JsonResponse(data=data, status=status)

def tweet_list_view(request, *args, **kwargs):
    qs = Tweet.objects.all()
    tweets_list = [x.serialize() for x in qs]
    data = {
        "isUser": False,
        "response": tweets_list
    }

    return JsonResponse(data=data)