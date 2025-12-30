from django.shortcuts import render
def home(request):
    return render(request,'shreyanshome.html')
def courses(request):
    return render(request,'shreyanscourse.html')
def bootcamp(request):
    return render(request,'bootcamp.html')