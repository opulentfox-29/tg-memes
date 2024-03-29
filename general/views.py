from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.core.cache import cache

from .models import Settings, Links


class Index(TemplateView):
    template_name = 'general/index.html'


class SettingsPage(DetailView):
    model = Settings
    template_name = 'general/settings.html'

    def get_object(self, queryset=None):
        settings_data = Settings.objects.first()
        if not settings_data:
            settings_data = Settings.objects.create(token='12345:ABCD')
        return settings_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cache_data = cache.get('settings_data')
        if cache_data:
            context.update(cache_data)
            return context

        settings_data = context['object']

        links = '\n'.join([i.link for i in Links.objects.all()])
        data = {
            'token': settings_data.token,
            'chat_id': settings_data.chat_id,
            'chunk_size': settings_data.chunk_size,
            'cycle': settings_data.cycle,
            'dont_use_proxy': settings_data.dont_use_proxy,
            'links': links,
        }
        context.update(data)

        cache.set('settings_data', data)
        return context
