# -*- coding: utf-8 -*-
import os
import tempfile
from subprocess import call, check_output

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.deprecation import MiddlewareMixin


class AmpCssMiddleware(MiddlewareMixin):

    def process_request(self, request):

        if settings.AMP_SITE_MODE is None:
            raise ImproperlyConfigured('AMP_SITE_MODE is not set!')
        if settings.AMP_SITE_MODE not in settings.AMP_SITE_MODES:
            raise ValueError('AMP_SITE_MODE is set to unknown value!')

        if settings.AMP_SITE_MODE == settings.AMP_SITE_ID_MODE:
            self.site_id_validation(request)
        elif settings.AMP_SITE_MODE == settings.AMP_SUBDOMAIN_MODE:
            self.subdomain_validation(request)

    def site_id_validation(self, request):
        return NotImplemented()

    def subdomain_validation(self, request):
        return NotImplemented()

    def process_template_response(self, request, response):
        # check if is_amp request
        if not request.is_amp:
            return response
        start = response.rendered_content.find('<style amp-custom>')
        end = response.rendered_content.find('</style>', start)

        tmpdir = tempfile.mkdtemp()
        predictable_filename = 'amp_css'

        saved_umask = os.umask(0077)

        path = os.path.join(tmpdir, predictable_filename)
        try:
            with open(path, "w") as tmp:
                tmp.write(response.rendered_content)
        except IOError as e:
            print 'IOError'
        else:
            css = check_output([settings.CSS_COMPILER_COMMAND,
                                settings.STATIC_ROOT + u'/' + request.amp_css_path, path, '--min'])

            css = css.replace('!important', '')
            response.content = response.rendered_content[:start + 18] + css + response.rendered_content[end:]
            os.remove(path)
        finally:
            os.umask(saved_umask)
            os.rmdir(tmpdir)

        return response
