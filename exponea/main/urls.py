from django.urls import include, path

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
from .views import AllView

urlpatterns = [
    path('all/', AllView.as_view(), name='all'),
]
