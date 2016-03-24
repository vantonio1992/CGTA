from django.conf.urls import url, include, patterns
from . import views

urlpatterns = patterns('CGTA.views',
	url(r'^upload/$', 'upload', name='upload'),
#	url(r'^output/(?P<image_id>\d+)/$', 'output', name='output'),
	url(r'^index/$', 'index', name='index'),
	url(r'^about/$', 'about', name='about'),
	url(r'^docs/$', 'docs', name='docs'),
	
)