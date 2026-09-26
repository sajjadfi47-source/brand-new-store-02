from .models import StoreSettings,Category
def store_settings(request):
 try: settings=StoreSettings.current()
 except Exception: settings=None
 return {"store":settings,"nav_categories":Category.objects.filter(active=True)[:12]}
