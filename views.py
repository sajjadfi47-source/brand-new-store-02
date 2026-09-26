from decimal import Decimal
from urllib.parse import quote
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail
from .models import Product,Category,Order,OrderItem,StoreSettings
def home(request):
 products=Product.objects.filter(active=True).select_related("category").prefetch_related("images")
 return render(request,"store/home.html",{"featured":products.filter(featured=True)[:8],"latest":products.order_by("-created_at")[:12],"products":products[:12]})
def shop(request):
 qs=Product.objects.filter(active=True).select_related("category").prefetch_related("images")
 q=request.GET.get("q","").strip()
 if q: qs=qs.filter(Q(name__icontains=q)|Q(description__icontains=q)|Q(category__name__icontains=q))
 if request.GET.get("category"): qs=qs.filter(category__slug=request.GET["category"])
 if request.GET.get("size"): qs=qs.filter(sizes__icontains=request.GET["size"])
 if request.GET.get("color"): qs=qs.filter(colors__icontains=request.GET["color"])
 if request.GET.get("stock"): qs=qs.filter(stock__gt=0)
 if request.GET.get("discount"): qs=qs.filter(old_price__gt=0)
 try:
  if request.GET.get("min"): qs=qs.filter(price__gte=Decimal(request.GET["min"]))
  if request.GET.get("max"): qs=qs.filter(price__lte=Decimal(request.GET["max"]))
 except: pass
 return render(request,"store/shop.html",{"products":qs,"categories":Category.objects.filter(active=True)})
def product_detail(request,slug):
 p=get_object_or_404(Product.objects.prefetch_related("images"),slug=slug,active=True)
 return render(request,"store/detail.html",{"product":p})
def cart_data(request): return request.session.get("cart",{})
def add_cart(request,pk):
 if request.method!="POST": return redirect("shop")
 p=get_object_or_404(Product,pk=pk,active=True)
 qty=max(1,min(int(request.POST.get("quantity",1)),max(p.stock,1)))
 size=request.POST.get("size",""); color=request.POST.get("color","")
 cart=cart_data(request); key=f"{p.pk}|{size}|{color}"
 old=cart.get(key,{}).get("qty",0)
 if p.stock<=0 or old+qty>p.stock:
  messages.error(request,"দুঃখিত, পর্যাপ্ত স্টক নেই।"); return redirect(request.META.get("HTTP_REFERER","shop"))
 cart[key]={"product_id":p.pk,"qty":old+qty,"size":size,"color":color}
 request.session["cart"]=cart; request.session.modified=True
 messages.success(request,"কার্টে পণ্য যোগ হয়েছে।")
 return redirect("cart")
def cart(request):
 cart=cart_data(request); rows=[]; subtotal=Decimal("0")
 for key,item in list(cart.items()):
  p=Product.objects.filter(pk=item["product_id"],active=True).first()
  if not p: continue
  line=p.price*item["qty"]; subtotal+=line
  rows.append({"key":key,"product":p,"qty":item["qty"],"size":item.get("size",""),"color":item.get("color",""),"line":line})
 return render(request,"store/cart.html",{"rows":rows,"subtotal":subtotal})
def cart_update(request):
 if request.method=="POST":
  cart=cart_data(request); key=request.POST.get("key")
  if key in cart:
   try:
    qty=int(request.POST.get("quantity",1))
    p=Product.objects.get(pk=cart[key]["product_id"])
    if qty<=0: cart.pop(key)
    elif qty<=p.stock: cart[key]["qty"]=qty
    else: messages.error(request,"স্টকের চেয়ে বেশি পরিমাণ নেওয়া যাবে না।")
   except (ValueError,Product.DoesNotExist): cart.pop(key,None)
  request.session["cart"]=cart; request.session.modified=True
 return redirect("cart")
def checkout(request):
 cart=cart_data(request)
 if not cart: messages.info(request,"আপনার কার্ট খালি।"); return redirect("shop")
 rows=[]; subtotal=Decimal("0")
 for key,item in cart.items():
  p=get_object_or_404(Product,pk=item["product_id"],active=True)
  if item["qty"]>p.stock: messages.error(request,f"{p.name}: স্টক পর্যাপ্ত নয়।"); return redirect("cart")
  line=p.price*item["qty"]; subtotal+=line
  rows.append((p,item,line))
 s=StoreSettings.current()
 if request.method=="POST":
  data={k:request.POST.get(k,"").strip() for k in ["customer_name","phone","district","area","address","note","payment_method"]}
  if not all(data[k] for k in ["customer_name","phone","district","area","address","payment_method"]):
   messages.error(request,"সব আবশ্যক তথ্য পূরণ করুন।")
  elif data["payment_method"] not in dict(Order.PAYMENT):
   messages.error(request,"পেমেন্ট পদ্ধতি সঠিক নয়।")
  else:
   delivery=Decimal("0") if s.free_delivery_minimum and subtotal>=s.free_delivery_minimum else (s.inside_delivery if data["district"].lower() in ["ঢাকা","dhaka"] else s.outside_delivery)
   with transaction.atomic():
    order=Order.objects.create(**data,subtotal=subtotal,delivery_charge=delivery,total=subtotal+delivery)
    for p,item,line in rows:
     locked=Product.objects.select_for_update().get(pk=p.pk)
     if locked.stock<item["qty"]:
      raise ValueError("Stock changed")
     locked.stock-=item["qty"]; locked.save(update_fields=["stock"])
     OrderItem.objects.create(order=order,product=p,product_name=p.name,unit_price=p.price,quantity=item["qty"],size=item.get("size",""),color=item.get("color",""))
   request.session["cart"]={}; request.session.modified=True
   # Optional SMS provider integration: configure a provider-specific endpoint/key in environment.
   messages.success(request,f"অর্ডার সম্পন্ন! আপনার Order ID: {order.order_id}")
   return render(request,"store/order_success.html",{"order":order})
 return render(request,"store/checkout.html",{"rows":rows,"subtotal":subtotal,"settings":s})
def whatsapp(request,pk):
 p=get_object_or_404(Product,pk=pk)
 s=StoreSettings.current()
 number="".join(c for c in s.whatsapp if c.isdigit())
 text=quote(f"আমি এই পণ্যটি অর্ডার করতে চাই: {p.name} | মূল্য: ৳{p.price} | {request.build_absolute_uri(p.get_absolute_url()) if hasattr(p,'get_absolute_url') else request.build_absolute_uri('/')}")
 return redirect(f"https://wa.me/{number}?text={text}" if number else "shop")
