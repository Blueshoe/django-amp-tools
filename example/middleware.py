# -*- coding: utf-8 -*-
from amp_tools.middleware import AmpCssMiddleware


class ExampleAmpMiddleware(AmpCssMiddleware):

    def site_id_validation(self, request):
        amp = request.GET.get('amp_on')
        request.is_amp = amp == '1'

