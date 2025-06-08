from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from math import ceil
from .models import *
from django.contrib.auth.decorators import login_required
from datetime import date

from django.contrib.auth.models import User
from django.http import HttpResponse


def create_superuser_if_not_exists():
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'your_secure_password')
        return HttpResponse("Superuser created.")
    return HttpResponse("Superuser already exists.")

def createadmin(request):
    create_superuser_if_not_exists()
    return HttpResponse("Superuser creation triggered.")


def index(request):
    allprods = []
    for category in Category.objects.all():
        products = Product.objects.filter(P_catid=category.id)
        products = [p for p in products if p.id !=""]
        dit = [
            {
                'Pid': p.id,
                'Pname': p.Pname,
                'P_image': p.P_image,
                'P_desc': p.P_desc,
                'P_brand': p.P_brand,
                'P_price': p.P_price,
            } for p in products
        ]
        n = len(dit)
        nslides = n // 4 + ceil((n / 4) - (n // 4))
        allprods.append([dit, range(1, nslides), nslides, category.Catname])

    l = []
    if request.user.is_authenticated:
        cust = request.user.email
        cart_items = Cart.objects.filter(cust_id=cust)
        l = [item.product_id for item in cart_items]

    param = {'allprods': allprods, 'len': l}
    return render(request, 'shop/index.html', param)


def register(request):
    if request.method == "POST":
        name = request.POST.get('name', '')
        password = request.POST.get('password', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        adrs = request.POST.get('address', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        pincode = request.POST.get('pincode', '')

        f = -1
        try:
            isexits = User.objects.get(username=name)
            f = 1
            user_profile = UserProfile.objects.filter(Name=isexits.username)
            if not user_profile.exists():
                isexits.delete()
                f = 0
        except User.DoesNotExist:
            f = 2
            user = User.objects.create_user(name, email, password)
            user.save()

        exists = UserProfile.objects.filter(Phone=phone).exists() or UserProfile.objects.filter(Email=email).exists()

        if exists or f == 1:
            messages.error(request, 'Email already exists')
            return redirect('/shop/register')

        UserProfile.objects.create(
            Name=name,
            Password=password,
            Email=email,
            Address=adrs,
            City=city,
            State=state,
            Phone=phone,
            Pincode=pincode
        )
        messages.success(request, 'Registration successful')
        return redirect('/shop/login_check')
    else:
        return render(request, 'register.html')


def login_check(request):
    if request.method == "POST":
        name = request.POST.get('name', '')
        pwd = request.POST.get('password', '')

        us = authenticate(username=name, password=pwd)

        if us is not None:
            login(request, us)
            messages.success(request, "Successfully logged in")
            return redirect('shop')
        else:
            messages.error(request, "Wrong password or user_id")
            return redirect('/shop/login_check/')

    return render(request, 'login.html')


def logout_check(request):
    logout(request)
    return redirect('/')


def contact(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        address = request.POST["address"]
        city = request.POST["city"]
        state = request.POST["state"]
        pincode = request.POST["pincode"]
        feedback_desc = request.POST["desc"]

        ContactUs.objects.create(
            name=name,
            email=email,
            address=address,
            city=city,
            state=state,
            phone=phone,
            pincode=pincode,
            feedback_desc=feedback_desc
        )
        messages.success(request, "Your feedback submitted successfully")
        return redirect('/shop')

    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')


def prod_view(request, myid):
    product = Product.objects.get(id=myid)
    d = {
        'Pid': product.id,
        'Pname': product.Pname,
        'P_image': product.P_image,
        'P_desc': product.P_desc,
        'P_brand': product.P_brand,
        'P_price': product.P_price
    }

    l = []
    rev = {}
    r_exist = False
    oth_exist = False
    oth_rev = []

    if request.user.is_authenticated:
        cust = request.user.email
        l = list(Cart.objects.filter(cust_id=cust).values_list('product_id', flat=True))

        top_rev = Review.objects.filter(cust_id=cust, product=product)
        other_rev = Review.objects.filter(product=product).exclude(cust_id=cust)

        if other_rev.exists():
            oth_exist = True
            for i, rat in enumerate(other_rev[:2]):
                oth_rev.append({
                    'P_name': rat.username,
                    'P_desc': rat.description,
                    'P_star': rat.stars
                })

        if top_rev.exists():
            r_exist = True
            rat = top_rev.first()
            rev = {
                    'P_name': rat.username,
                    'P_desc': rat.description,
                    'P_star': rat.stars
                }

    return render(request, 'prodview.html', {
        'dict': d,
        'len': l,
        'rev': rev,
        'r_exist': r_exist,
        'range': range(0, 5),
        'oth_exist': oth_exist,
        'oth_rev': oth_rev
    })


def cart(request, myid):
    if myid != 9481:
        if request.user.is_authenticated:
            cust = request.user.email
            try:
                product = Product.objects.get(id=myid)
                Cart.objects.create(cust_id=cust, product=product, quantity=1)
                return redirect('/shop')
            except Product.DoesNotExist:
                messages.error(request, "Product does not exist.")
        else:
            messages.error(request, "Login to add the items to cart")
            return redirect('/shop')

    if request.user.is_authenticated:
        cust = request.user.email
        cart_items = Cart.objects.filter(cust_id=cust).select_related('product')
        n = cart_items.count()
        d = []
        total = 0
        for item in cart_items:
            p = item.product
            d.append({
                'Pid': p.id,
                'Pname': p.Pname,
                'P_image': p.P_image,
                'P_desc': p.P_desc,
                'P_brand': p.P_brand,
                'P_price': p.P_price,
                'P_quantity': item.quantity
            })
            total += item.quantity * p.P_price
    else:
        n = 0
        d = []
        total = 0

    if total > 1000:
        tot = total - 100
        dis = 100
    else:
        tot = total
        dis = 0

    return render(request, 'cart.html', {
        "len": n,
        "dict": d,
        "total": total,
        "tot": tot,
        "dis": dis
    })


def remove(request, myid):
    cust = request.user.email
    Cart.objects.filter(cust_id=cust, product_id=myid).delete()
    return redirect('/shop')


def search_items(request):
    if request.method == 'POST':
        desc1 = request.POST['desc1']
        allprods = []
        categories = Category.objects.all()
        for cat in categories:
            products = Product.objects.filter(P_catid=cat.id)
            dit = []
            for p in products:
                s = f"{p.Pname} {p.P_desc} {p.P_brand} {p.P_price} {cat.Catname}"
                if desc1.lower() in s.lower():
                    dit.append({
                        'Pid': p.id,
                        'Pname': p.Pname,
                        'P_image': p.P_image,
                        'P_desc': p.P_desc,
                        'P_brand': p.P_brand,
                        'P_price': p.P_price
                    })
            if dit:
                n = len(dit)
                nslides = n // 4 + ceil((n / 4) - (n // 4))
                allprods.append([dit, range(1, nslides), nslides, cat.Catname])

        if not allprods:
            messages.error(request, "No product found")
            return redirect('/shop')

        return render(request, 'shop/index.html', {'allprods': allprods, 'len': 1})

@login_required
def order(request):
    cust = request.user.email
    try:
        # Fetch user details from UserProfile
        user_profile = UserProfile.objects.get(Email=cust)
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect('/shop')

    # Ensure 'total' is included in the defaults
    order_obj, created = Order.objects.get_or_create(
        cust_id=cust,
        defaults={
            'C_name': user_profile.Name,  # Fetch name from UserProfile
            'ord_date': date.today(),
            'C_phone': user_profile.Phone,  # Fetch phone from UserProfile
            'city': user_profile.City,  # Fetch city from UserProfile
            'state': user_profile.State,  # Fetch state from UserProfile
            'address': user_profile.Address,  # Fetch address from UserProfile
            'pincode': user_profile.Pincode,  # Fetch pincode from UserProfile
            'total': 0  # Set a default value for 'total'
        }
    )

    cart_items = Cart.objects.filter(cust_id=cust).select_related('product')
    d = []
    total = 0

    for item in cart_items:
        p = item.product
        d.append({
            'Pid': p.id,
            'Pname': p.Pname.capitalize(),
            'P_image': p.P_image.url if p.P_image else None,
            'P_desc': p.P_desc,
            'P_brand': p.P_brand,
            'P_price': p.P_price,
            'P_quantity': item.quantity
        })
        total += p.P_price * item.quantity

    dis = 100 if total > 1000 else 0
    order_obj.total = total - dis
    order_obj.save()

    customer = {
        'C_name': order_obj.C_name.capitalize(),
        'C_Email': order_obj.cust_id,
        'C_Addr1': order_obj.address,
        'C_city': order_obj.city,
        'C_state': order_obj.state,
        'C_phone': order_obj.C_phone,
        'ord_id': order_obj.id
    }

    quant = 8
    return render(request, 'order.html', {
        'dit': d,
        'total': total - dis,
        'dis': dis,
        'cust': customer,
        'quant': quant
    })


@login_required
def inc_item(request, myid):
    cust = request.user.email
    try:
        cart_item = Cart.objects.get(product_id=myid, cust_id=cust)
        cart_item.quantity += 1
        cart_item.save()
    except Cart.DoesNotExist:
        pass
    return redirect('/shop/cart/9481')


@login_required
def dec_item(request, myid):
    cust = request.user.email
    try:
        cart_item = Cart.objects.get(product_id=myid, cust_id=cust)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
    except Cart.DoesNotExist:
        pass
    return redirect('/shop/cart/9481')


@login_required
def change_address(request):
    if request.method == "POST":
        cust = request.user.email
        name2 = request.POST['name2']
        phone2 = request.POST['phone2']
        city2 = request.POST['city2']
        address2 = request.POST['address2']
        pincode2 = request.POST['pincode2']

        try:
            order = Order.objects.get(cust_id=cust)
            order.C_name = name2
            order.ord_date = date.today()
            order.C_phone = phone2
            order.city = city2
            order.address = address2
            order.pincode = pincode2
            order.save()
        except Order.DoesNotExist:
            messages.error(request, "Order not found.")
        return redirect('/shop/order')


@login_required
def order_complete(request):
    messages.success(request, "Order placed successfully")
    cust_email = request.user.email

    try:
        order = Order.objects.get(cust_id=cust_email)
    except Order.DoesNotExist:
        messages.error(request, "No order found to complete.")
        return redirect('/shop')

    cart_items = Cart.objects.filter(cust_id=cust_email)
    for item in cart_items:
        OrderItem.objects.create(
            ord_id=order,
            product=item.product,
            quantity=item.quantity
        )
    cart_items.delete()
    return redirect('/shop')


@login_required
def buy_now(request, myid):
    cust_email = request.user.email
    cart_item, created = Cart.objects.get_or_create(
        product_id=myid,
        cust_id=cust_email,
        defaults={'quantity': 1}
    )
    return redirect('/shop/cart/9481')


@login_required
def review_star(request, myid):
    if request.method == "POST":
        cust = request.user.email
        rev_desc = request.POST['rev_desc']
        rev_star = request.POST['rev_star']
        us_name = request.user.username
        Review.objects.create(
            cust_id=cust,
            username=us_name,
            description=rev_desc,
            stars=rev_star,
            product_id=myid
        )
        return redirect('/shop/prodview/' + str(myid))
    messages.error(request, "Login to add reviews")
    return redirect('/shop')


@login_required
def order_history(request):
    cust_email = request.user.email
    orders = OrderHistory.objects.filter(cust_id=cust_email)
    dit = []
    item_ordered = orders.exists()

    for order in orders:
        params = {
            'ord_id': order.ord_id,
            'cust_id': order.cust_id,
            'c_name': order.C_name,
            'ord_date': order.ord_date,
            'c_phone': order.C_phone,
            'city': order.city,
            'state': order.state,
            'total': order.total,
            'address': order.address,
            'pincode': order.pincode
        }

        items = OrderItem.objects.filter(ord_id=order.ord_id).select_related('product')
        ord_item = [[item.product.Pname, item.quantity] for item in items]
        dit.append([params, ord_item])

    return render(request, 'order_history.html', {'dict': dit, 'ord_exist': item_ordered})


# def admin_page(request):
#     if request.method == 'POST':
#         P_id = request.POST['Pid']
#         P_name = request.POST['Pname']
#         P_desc = request.POST['desc']
#         P_brand = request.POST['P_brand']
#         P_price = request.POST['Price']
#         P_catid = request.POST['cat_id']
#         P_quantity = request.POST['quantity']

#         image = request.FILES.get("image")
#         instance = ImageModel(image=image)
#         instance.save()

#         P_image = 'shop/uploads/' + str(image)

#         Product.objects.create(
#             id=P_id,
#             Pname=P_name.upper(),
#             P_image=P_image,
#             P_desc=P_desc,
#             P_brand=P_brand,
#             P_price=P_price,
#             cat_id=P_catid
#         )

#     return render(request, 'admin_page.html')

def admin_page(request):
    if request.method == 'POST':
        P_id = request.POST['Pid']
        P_name = request.POST['Pname']
        P_desc = request.POST['desc']
        P_brand = request.POST['P_brand']
        P_price = request.POST['Price']
        cat_name = request.POST['cat_id']  # Accepting cat_name instead of cat_id
        P_quantity = request.POST['quantity']

        # Get the Category ID based on the cat_name
        try:
            category = Category.objects.get(Catname=cat_name)  # Fetch the category by name
            P_catid = category.id  # Get the corresponding category ID
            print(f"Category ID for {cat_name}: {P_catid}")
        except Category.DoesNotExist:
            # Handle the case if the category doesn't exist
            messages.error(request, "Category does not exist.")
            return render(request, 'admin_page.html')

        # Handle image upload
        image = request.FILES.get("image")
        instance = ImageModel(image=image)
        instance.save()

        # Set image path
        P_image = 'shop/uploads/' + str(image)

        # Create the product
        Product.objects.create(
            id=P_id,
            Pname=P_name.upper(),
            P_image=P_image,
            P_desc=P_desc,
            P_brand=P_brand,
            P_price=P_price,
            P_catid=category
        )

    return render(request, 'admin_page.html')

