from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from .models import Chat


def Talk(request):
    c = Chat.objects.all()
    return render(request, "chat/home.html", {'home': 'active', 'chat': c})


def Post(request):
    if request.method == "POST":
        msg = request.POST.get('msgbox', None)
        c = Chat(user=request.user.personne_set.get(), message=msg)
        if msg != '':
            c.save()
        return JsonResponse({'msg': msg, 'user': c.user.usager.username})
    else:
        return HttpResponse('Request must be POST.')


def Messages(request):
    c = Chat.objects.all()
    return render(request, 'chat/messages.html', {'chat': c})
