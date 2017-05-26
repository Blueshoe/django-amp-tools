# -*- coding: utf-8 -*-
from django.views.generic.base import TemplateView


class IndexView(TemplateView):
    template_name = 'base_normal.html'


class ManualAmpIndexView(TemplateView):
    template_name = 'base_manual.html'


class AmpIndexView(TemplateView):
    template_name = 'base_amp.html'
