"""Views."""
from django.views.generic import TemplateView


class HomePageView(TemplateView):
    """Specify template name."""

    template_name = "home.html"
