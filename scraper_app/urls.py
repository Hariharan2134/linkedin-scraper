from django.urls import path
from .views import login_page, dashboard, run_scraper_view

urlpatterns = [
    path('', login_page, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('run/', run_scraper_view, name='run_scraper'),
]
