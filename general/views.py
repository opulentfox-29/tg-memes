from django.shortcuts import render

from .models import Settings, Links


def index(request):
    return render(request, 'general/index.html', )


def settings(request):
    settings_data = Settings.objects.first()
    if not settings_data:
        settings_data = Settings.objects.create(token='12345:ABCD')

    links = '\n'.join([i.link for i in Links.objects.all()])

    data = {
        'token': settings_data.token,
        'chat_id': settings_data.chat_id,
        'chunk_size': settings_data.chunk_size,
        'cycle': settings_data.cycle,
        'dont_use_proxy': settings_data.dont_use_proxy,
        'links': links,
    }

    return render(request, 'general/settings.html', data)
