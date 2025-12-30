from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth import get_user_model,authenticate, login, logout
from django.contrib import messages



CustomUser = get_user_model()

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

      
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'signup.html')
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'signup.html')

      
        user = CustomUser.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Account created successfully! You can now log in.')
        return redirect('signin') 

    return render(request, 'signup.html')



def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return HttpResponse('home')  
        else:
            messages.error(request, "Invalid email or password!")

    return render(request, 'signin.html')
def signout(request):
    logout(request)
    return redirect('signin')
def home(request):
    return render(request,'home.html')

