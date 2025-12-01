from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, ScraperForm
from .linkedin_script import run_scraper

def login_page(request):
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"]
            )
            if user:
                login(request, user)
                return redirect("dashboard")
            else:
                return render(request, "login.html", {
                    "form": form,
                    "error": "Invalid login details"
                })

    return render(request, "login.html", {"form": form})


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")

    form = ScraperForm()
    return render(request, "dashboard.html", {"form": form})


def run_scraper_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":
        query = request.POST.get("query")
        pages = request.POST.get("pages")
        max_profiles = request.POST.get("max_profiles")

        output = run_scraper(query, pages, max_profiles)

        return render(request, "result.html", {"output": output})

    return redirect("dashboard")
