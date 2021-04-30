from django.urls import include, path

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
from .views import AllView, FirstView, WithinTimeoutView

urlpatterns = [
    path("all/", AllView.as_view(), name="all"),
    path("first/", FirstView.as_view(), name="first"),
    path("within-timeout/", WithinTimeoutView.as_view(), name="within-timeout"),
]
