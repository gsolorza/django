from django.shortcuts import render, redirect
import csv
from io import StringIO
from . import allowed_commands

# Create your views here.
def index(request):
    context = {
        "commands": allowed_commands.commands
    }
    return render(request, "forms/index.html", context)

def commands(request):
    context = {}
    return render(request, "forms/commands.html", context)
