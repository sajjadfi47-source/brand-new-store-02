from django.db import models
from django.utils.text import slugify
import uuid
class Category(models.Model):
 name=models.CharField(max_length=100, unique=True)
 slug=models.SlugField(max_length=120, unique=True, blank=True)
 active=models.BooleanField(default=True)
 def save(self,*a,**kw):
  if not self.slug: self.slug=slugify(self.name)
  super().save(*a,**kw)
 def __str__(self): return self.name
class Product(models.Model):
 name=models.CharField(max_length=200)
 slug=models.SlugField(unique=True, blank=True)
 category=models.ForeignKey(Category,on_delete=models.PROTECT,related_name="products")
 description=models.TextField(blank=True)
 price=models.DecimalField(max_digits=10,decimal_places=2)
 old_price=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
 stock=models.PositiveIntegerField(default=0)
 sizes=models.CharField(max_length=200,blank=True,help_text="Comma-separated, e.g. S,M,L,XL")
 colors=models.CharField(max_length=200,blank=True,help_text="Comma-separated, e.g. Black,White")
 active=models.BooleanField(default=True)
 featured=models.BooleanField(default=False)
 created_at=models.DateTimeField(auto_now_add=True)
 def save(self,*a,**kw):
  if not self.slug: self.slug=slugify(self.name) or uuid.uuid4().hex[:8]
  super().save(*a,**kw)
 @property
 def discount_percent(self):
  if self.old_price and self.old_price>self.price: return round((self.old_price-self.price)*100/self.old_price)
  return 0
 @property
 def size_list(self): return [x.strip() for x in self.sizes.split(",") if x.strip()]
 @property
 def color_list(self): return [x.strip() for x in self.colors.split(",") if x.strip()]
 def __str__(self): return self.name
class ProductImage(models.Model):
 product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="images")
 image=models.ImageField(upload_to="products/%Y/%m/")
 alt_text=models.CharField(max_length=200,blank=True)
class StoreSettings(models.Model):
 name=models.CharField(max_length=160,default="BRAND NEW STORE 0.2")
 logo=models.ImageField(upload_to="branding/",blank=True,null=True)
 phone=models.CharField(max_length=30,blank=True)
 whatsapp=models.CharField(max_length=30,blank=True)
 address=models.TextField(blank=True)
 facebook=models.URLField(blank=True)
 instagram=models.URLField(blank=True)
 description=models.TextField(blank=True)
 inside_delivery=models.DecimalField(max_digits=8,decimal_places=2,default=60)
 outside_delivery=models.DecimalField(max_digits=8,decimal_places=2,default=120)
 free_delivery_minimum=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
 bkash_number=models.CharField(max_length=40,blank=True)
 nagad_number=models.CharField(max_length=40,blank=True)
 hero_title=models.CharField(max_length=200,default="Style that speaks.")
 hero_subtitle=models.CharField(max_length=300,default="Discover your everyday premium fashion.")
 hero_image=models.ImageField(upload_to="branding/",blank=True,null=True)
 @classmethod
 def current(cls): return cls.objects.first() or cls.objects.create()
class Order(models.Model):
 STATUS=[("new","নতুন অর্ডার"),("confirmed","Confirmed"),("processing","Processing"),("packed","Packed"),("shipped","Shipped"),("delivered","Delivered"),("cancelled","Cancelled")]
 PAYMENT=[("cod","Cash on Delivery"),("bkash","bKash"),("nagad","Nagad")]
 order_id=models.CharField(max_length=24,unique=True,editable=False)
 customer_name=models.CharField(max_length=150)
 phone=models.CharField(max_length=30)
 district=models.CharField(max_length=100)
 area=models.CharField(max_length=150)
 address=models.TextField()
 note=models.TextField(blank=True)
 payment_method=models.CharField(max_length=20,choices=PAYMENT)
 subtotal=models.DecimalField(max_digits=12,decimal_places=2)
 delivery_charge=models.DecimalField(max_digits=10,decimal_places=2)
 total=models.DecimalField(max_digits=12,decimal_places=2)
 status=models.CharField(max_length=20,choices=STATUS,default="new")
 created_at=models.DateTimeField(auto_now_add=True)
 def save(self,*a,**kw):
  if not self.order_id: self.order_id="BNS-"+uuid.uuid4().hex[:10].upper()
  super().save(*a,**kw)
 def __str__(self): return self.order_id
class OrderItem(models.Model):
 order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name="items")
 product=models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)
 product_name=models.CharField(max_length=200)
 unit_price=models.DecimalField(max_digits=10,decimal_places=2)
 quantity=models.PositiveIntegerField()
 size=models.CharField(max_length=40,blank=True)
 color=models.CharField(max_length=50,blank=True)
