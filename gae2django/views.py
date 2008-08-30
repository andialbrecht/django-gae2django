from django.http import HttpResponse
from django.template import Context, Template

def test(request):
    t = Template('Test view')
    c = Context({'user': request.user})
    return HttpResponse(t.render(c))
