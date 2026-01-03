from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth import get_user_model,authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *


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

    return render(request,'signup.html')



def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user :
            login(request, user)
            messages.success(request, "Login successful!")
            return render(request,'home.html')
        else:
           messages.error(request, "Invalid username or password!")

    return render(request, 'signin.html')
def signout(request):
    logout(request)
    return redirect('signin')
def home(request):
    courses = Course.objects.all()
    return render(request, "home.html", {"courses": courses})



def course_list(request):
    courses = Course.objects.all()
    return render(request, "courses.html", {
        "courses": courses
    })
def course_detail(request, slug):
    course = Course.objects.filter(slug=slug).first()
    if not course:
        return redirect('course_list')

    return render(request, "course_detail.html", {
        "course": course
    })


def add_course(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        short_description = request.POST.get('short_description')
        full_description = request.POST.get('full_description')
        price_original = request.POST.get('price_original')
        price_discounted = request.POST.get('price_discounted')
        discount_percentage = request.POST.get('discount_percentage')
        language = request.POST.get('language')
        schedule = request.POST.get('schedule')
        course_validity = request.POST.get('course_validity')
        image = request.FILES.get('image')

       
        base_slug = slugify(title)
        unique_slug = base_slug
        num = 1
        while Course.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{num}"
            num += 1

       
        Course.objects.create(
            title=title,
            slug=unique_slug,
            short_description=short_description,
            full_description=full_description,
            price_original=price_original,
            price_discounted=price_discounted,
            discount_percentage=discount_percentage,
            language=language,
            schedule=schedule,
            course_validity=course_validity,
            image=image
        )

        messages.success(request, "Course added successfully!")
        return redirect('home')

    return render(request, 'add_course.html')

def add_to_cart(request, course_id):

    course = Course.objects.filter(id=course_id).first()
    if not course:
        return redirect('course_list')   # or any page you want

    # ===============================
    # LOGGED-IN USER (DB CART)
    # ===============================
    if request.user.is_authenticated:

        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            course=course
        )

        if not created:
            cart_item.quantity += 1
        cart_item.save()

        # ---------- MERGE SESSION CART ----------
        session_cart = request.session.get('cart')

        if session_cart:
            for cid, qty in session_cart.items():
                session_course = Course.objects.filter(id=cid).first()
                if not session_course:
                    continue

                item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    course=session_course
                )

                if not created:
                    item.quantity += qty
                else:
                    item.quantity = qty

                item.save()

            del request.session['cart']

        return redirect('cart_page')
    #seesion cart
    cart = request.session.get('cart', {})

    cid = str(course.id)

    if cid in cart:
        cart[cid] += 1
    else:
        cart[cid] = 1

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart_page')
def cart_page(request):
    cart_items = []
    total_items = 0
    total_price = 0

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            items = CartItem.objects.filter(cart=cart)
            for item in items:
                price = item.course.price_discounted or 0
                subtotal = price * item.quantity   # ✅ define subtotal

                cart_items.append({
                    "course": item.course,
                    "quantity": item.quantity,
                    "price": price,
                    "subtotal": subtotal
                })

                total_items += item.quantity
                total_price += subtotal

    else:
        session_cart = request.session.get('cart', {})
        for course_id, quantity in session_cart.items():
            course = Course.objects.filter(id=course_id).first()
            if not course:
                continue

            price = course.price_discounted or 0
            subtotal = price * quantity

            cart_items.append({
                "course": course,
                "quantity": quantity,
                "price": price,
                "subtotal": subtotal
            })

            total_items += quantity
            total_price += subtotal

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total_items": total_items,
        "total_price": total_price
    })

def update_cart(request, course_id, action):
 
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return redirect('cart_page')

        item = CartItem.objects.filter(cart=cart, course_id=course_id).first()
        if not item:
            return redirect('cart_page')

        if action == 'inc':
            item.quantity += 1
            item.save()

        elif action == 'dec':
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
            else:
                item.delete()

        elif action == 'remove':
            item.delete()

   
    else:
        cart = request.session.get('cart', {})
        cid = str(course_id)

        if cid not in cart:
            return redirect('cart_page')

        if action == 'inc':
            cart[cid] += 1

        elif action == 'dec':
            if cart[cid] > 1:
                cart[cid] -= 1
            else:
                del cart[cid]

        elif action == 'remove':
            del cart[cid]

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart_page')
from django.shortcuts import render, redirect
from .models import Cart, CartItem, Course

def checkout_page(request):
    cart_items = []
    total_items = 0
    total_price = 0

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            items = CartItem.objects.filter(cart=cart)
            for item in items:
                price = item.course.price_discounted or 0
                subtotal = price * item.quantity
                cart_items.append({
                    "course": item.course,
                    "quantity": item.quantity,
                    "price": price,
                    "subtotal": subtotal
                })
                total_items += item.quantity
                total_price += subtotal
    else:
        session_cart = request.session.get('cart', {})
        for course_id, quantity in session_cart.items():
            course = Course.objects.filter(id=course_id).first()
            if not course:
                continue
            price = course.price_discounted or 0
            subtotal = price * quantity
            cart_items.append({
                "course": course,
                "quantity": quantity,
                "price": price,
                "subtotal": subtotal
            })
            total_items += quantity
            total_price += subtotal

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "total_items": total_items,
        "total_price": total_price
    })

@login_required(login_url='signin')
def confirm_order(request):
    
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
          
            cart.cartitem_set.all().delete()
    
    else:
        request.session['cart'] = {}
        request.session.modified = True

    return render(request, "order_success.html")

