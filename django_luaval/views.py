from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
import tidy

def validate(request):
	if "src" in request.POST:
		src = tidy.prettify(request.POST['src'])
		return render_to_response("index.html", {"src":src})
	else:
		return render_to_response("index.html", {})
