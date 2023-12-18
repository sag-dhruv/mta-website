from django.http import HttpResponse
from django.shortcuts import render, redirect


def index(request):
    response = redirect('/mta-line')
    return response