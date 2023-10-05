from django.http.response import HttpResponse
import logging
from django.contrib.auth.decorators import login_required


logger = logging.getLogger(__name__)

@login_required
def secure(request, file):
        response = HttpResponse()
        response.status_code = 200
        protected_uri = request.path_info.replace("/media", "/protected")
        response['X-Accel-Redirect'] = protected_uri
        del response['Content-Type']
        del response['Content-Disposition']
        del response['Accept-Ranges']
        del response['Set-Cookie']
        del response['Cache-Control']
        del response['Expires']
        print("protected uri served " + protected_uri)
        #logger.debug("protected uri served " + protected_uri)
        return response

