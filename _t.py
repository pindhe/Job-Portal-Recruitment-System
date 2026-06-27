import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from django.test import Client
from django.contrib.auth import get_user_model

U = get_user_model()
u = U.objects.filter(is_superuser=True).first()
c = Client()
c.force_login(u)
r = c.get("/dashboard/admin-panel/")
s = r.content.decode()
print("overview", r.status_code)
print("sub menus", s.count('x-show="sub"'))
for k in ["partners", "job-categories", "companies", "plans", "coupons", "contact-messages", "newsletter"]:
    print(k, ("manage/%s/" % k) in s, c.get("/dashboard/admin-panel/manage/%s/" % k).status_code)
