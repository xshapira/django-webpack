# Django CRUD app on Docker

Django + Nginx + Gunicorn + Docker repository. Support for Django 3.2 with reference to the following sources: It also has a flexible configuration with docker-compose.

- Django Textbooks "Basics" that can be used in the field
- "Django Textbooks That Can Be Used in the Field"
- <a href="https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/" target="_blank">Dockerizing Django with Postgres, Gunicorn, and Nginx</a>


### Best Practices for "Field-Based Django Textbooks, Basics"

🎉　🎉 10 Best Practices

1. Easy-to-understand project structure
2. Deploy urls.py for each application
3. Extend the User model
4. See which queries are published
5. select_related the number prefetch_related queries in the query/ database
6. Prepare a base template
7. Inherit ModelForm in such a time
8. Use the Message Framework
9. Set up your personal development environment local_settings.py in the settings
10. Write secret variables in .env file

#### Extra Use a convenient Django package (django-debug-toolbar)

```bash
pipenv install django-debug-toolbar
```

```python[config/settings.py]
if DEBUG:
  def show_toolbar(request):
    return True

  INSTALLED_APPS += (
    'debug_toolbar',
  )
  MIDDLEWARE += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
  )
  DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
  }
```

```python[config/urls.py]
if settings.DEBUG:
  import debug_toolbar

  urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
```


#### BP1 Easy-to-understand project configuration

・Problems
- The base directory and the configuration directory name are the same whcich makes them confusing and difficult.
- Templates and static files are placed separately for each application。

・Practices
- Change the directory name generated by startproject. "config", "default", "root", etc.
- In production, the collectstatic command is used to organize them into staticfiles directories. The development environment (runserver) is automatically distributed.

```bash[bash]
mkdir mysite && cd mysite
django-admin startproject config .

tree
mysite
 |-- manage.py
 `-- config
    |-- __init__.py
```

```python[config/settings.py]
STATIC_URL = '/staticfiles/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/mediafiles/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')
```


#### Deploy urls.py BP2 application

If you add url pattern settings only urls.py the settings generated at startproject run, the settings will become more and more bloated and management will be difficult. urls.py the application and place one system urls.py application directory.

```python[config/urls.py]
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
  path('admin/', admin.site.urls),
  path('item/', include('item.urls)),
]
```

Use the include function to load urls.py-by-application data. Leave all URL patterns starting with "/item/" to the item/urls .py "item" application. The application urls.py focus only on setting the URL pattern inside the application.

```python[item/urls.py]
from django.urls import path

from . import views

app_name = 'item'
urlpatterns = [
  path('', views.itemList, name='item.list'),
  path('/<int:pk>', views.itemShow, name='item.show'),
]
```

・Caveats
- The startapp command does not generate any urls.py application directory. Create your own.
- app_name (namespace) in the user.


#### Extending the BP3 User Model

The User model provided by default has the following fields:

<a href="https://docs.djangoproject.com/en/3.2/ref/contrib/auth/" target="_blank">django.contrib.auth</a>

class models.User

|field|
|---|
|username|
|first_name|
|last_name|
|email|
|password|
|groups|
|user_permissions|
|is_staff|
|is_active|
|is_superuser|
|last_login|
|date_joined|


If there are more fields than the default field, it needs to be extended. There are three most ways to extend it.

1. Inherit abstract class AbstractBaseUser - > to change before release
2. Inherit abstract class AbstractUser - > add it before release
3. Create a different model and make it relevant in OneToOneField - > after release

ex: Inheriting AbstractUser

1. Edit accounts/models.py
2. Edit config/settings.py

```python[accounts/models.py]
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
  class Meta:
    db_table = 'custom_user'

  login_count = models.IntegerField(varbose_name='Number of logins', default=0)
```

```python[settings.py]
AUTH_USER_MODEL = 'accounts.CustomUser' # <Application name>. <Model class name>
```


#### BP4 Check published queries

What queries are issued when an object is searched - is the model used in a good way? Does it affect performance? check

1. Use django shell
2. Change logging settings
3. Use django-debug-toolbar SQL panel


#### select_related prefetch_related query count in BP5 /bp5

Avoid N+1 problems. Used to retrieve relation data in a model.

|METHOD|NOTE|
|---|---|
|select_related|「 "1" object is obtained by JOIN from the "1" and "|
|prefetch_related|「 Get "many" objects from the "one" and "many" sides and keep them in the |

```python
Book.objects.all().select_related('publisher')
SELECT * FROM book INNER JOIN publisher ON book.publisher_id = publisher.id
```

```python
Book.objects.all().prefetch_related('authors')
```


#### Prepare a BP6 base template

The common parts of the template (JavaScript before the head tag and body tag) .html the base tag and inherited within each template.

```bash
`-- templates
    |-- accounts
    |   `-- login.html
    `-- base.html
```


#### BP7 Let's inherit ModelForm in such a time

You can reuse field definitions for a particular model by inheriting django.forms.models.ModelForm instead of the django.forms.Form that a regular form inherits. In addition to the default form validation, the model validation runs.

```python[accounts/forms.py]
from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.ModelForm):
  class Meta:
    model = User
    fields = ('username', 'email', 'password',)
    widgets = {
      'password': forms.PasswordInput(attrs={'placeholder': 'Password'}),
    }
  password_confirm = forms.CharField(
    label='Password confirmation',
    required=True,
    strip=False,
    widget=forms.PasswordInput(attrs={'placeholder': 'Password confirmation'}),
  )

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['username'].widget.attrs = {'placeholder': 'User name'}
    self.fields['email'].required = True
    self.fields['email'].widget.attrs = {'placeholder': 'Email address'}

  # Unique constraint check
  def clean(self):
    super().clean()
    password = self.cleaned_data['password']
    password_confirm = self.cleaned_data['password_confirm']
    if password != password_confirm:
      raise forms.ValidationError('Password and password confirmation do not match')
```

```python[accounts/views.py]
form = RegisterForm(request.POST)
# save
user = form.save()
# or
user = form.save(commit=False)
user.set_password(form.cleaned_data['password'])
user.save()
```


#### Using the BP8 Message Framework

Also known as flash messages. Use MessageMiddleware. startproject
enabled by default when By default, cookies are used, but cookies may not display a message when redirected, so change them to use Session.

```python[config/settings.py]
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
```

```python[accounts/views.py]
from django.contrib import messages
from django.urls import reverse
from django.views import View

class LoginView(View):
  def post(self, *args, **kwargs):
  ...
  messages.info(request, "You have logged in.")

  return redirect(reverse('item:index'))
```

templates_ in directory message.html Create.

```python[templates/_messages.html]
{% if messages %}
<div class="ui relazed divided list">
  {% for message in messages %}
  <div class="ui {% if message.tags %}{{ message.tags }}{% endif %} message">
    {{ message }}
  </div>
  {% endfor %}
</div>
{% endif %}
```


#### BP9 Personal Development Environment Settings local_settings.py in the article

This repository is omitted because it divides the environment between docker-composer.yml and production (docker-composer.prod.yml). By the way, the composition of "Django in the field" is as follows.

```bash
config/settings
|-- __init__.py
|-- base.py
|-- local.py
|-- production.py
`-- test.py
```

#### BP10 Secret Variables To Write in .env File

Do not place sensitive variables, such as passwords, under Git control. In the field, Django uses the django-environ package, but this repository has set environment variables on the container OS. As mentioned above, docker-composer.yml (container) is used in this repository because it is different from the development environment.



### Development flow of Django textbook "Practice edition" that can be used in the field

1. Quickly implement around authentication (djangp-allauth)
2. Development Tips (Bootstrap4 Compatible) < - Don't Do It
3. Development Tips (Ajax Support and JSON Response)
4. Development Tips (File Upload)
5. Unit Testing
6. Deploy
7. Security TIPS
8. TIPS for speeding up
9. Send email


#### Quick implementation around authentication (djangp-allauth)

1. Install django-allauth
2. Update settings.py
3. Update urls.py


#### Development Tips (Ajax Support and JSON Response)

There are three main ways to use Ajax in Django.

1. Send Ajax requests to the server using ajax methods in templates
2. Get the request parameter in the view and return the JSON response object
3. Receive JSON objects in ajax() callbacks

```python[templates/form.html]
<script src="https://cdnjs.cloudflare.com/ajax/libs/axios/0.21.1/axios.min.js"></script>
<script>
  const form = document.querySelector("form");
  form.addEventListener('submit', (event) => {
    event.preventDefault()

    let data = new FormData();

    data.append('title', document.querySelector('input[name="title"]').value)
    data.append('note', document.querySelector('input[name="note"]').value)
    data.append('cstfmiddlewaretoken', '{{csrf_token}}')

    axios.post('create_post/', data)
      .then(res => alert("Form submitted"))
      .catch(error => console.log(error))
  })
</script>
```

```python[views.py]
from django.http import JsonResponse

def createPost(request):
  if request.method == 'POST':
    title = request.POST.get('title')
    note = request.POST.get('note')
    Note.objects.create(
      title=title,
      note=note
    )

  return JsonResponse({"status": 'Success'})
  Specify safe=False when returning objects other than # dict
  # return JsonResponse([{'a': 1}, {'b': 2}], safe=False)
```

To define a function to retrieve CSRFtoken from cookies in JavaScript.

```javascript[static/js/common.js]
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken'))
      .split('=')[1];
  }

  return cookieValue
}
```


#### Development Tips (File Upload)

In Django, a static file uploaded by a user is called a media file. There are useful packages related to upload files.

1. Pillow
2. python-magic <- check file headers
3. django-imagekit <-sumne generation
4. djnago-cleanup <- Delete original files
5. django-storage <- S3
6. boto3 <- S3


#### Unit Testing

|NAME|NOTE|
|---|---|
| unit test |manage.py the test command. This is |
| automatically | test classes and methods for test runners, |
| TestCase class| Django standard test class. |
| simulator | behaves like a browser within a test client or test method. |


##### How to write a test class test method

If the test.py startapp, delete and cut the tests directory.

```bash
|-- app
|   |-- __init__.py
|   |-- tests
|       |-- _init__.py
|       |-- test_forms.py
|       |-- test_models.py
|       `-- test_views.py
```

#### TIPS for Speedup

##### Make the session backend a cache server

1. sudo apt install -y memcached
2. (venv) pipenv install python-memcached
3. Update settings.py for CACHES


##### Cache responses for any view

Views that return JSON can make effective use of the cache.


##### Clear Cache

1. pipenv install django-extensions
2. Add INSTALLED_APPS in settings.py


##### Other ways to speed up

1. CONN_MAX_AGE <- Set db connection time
2. Reduce middleware handling
3.JS/CSS file compression, CDN of static files <-django-compressor


#### Send Email

Locally, it is output to console.

```bash
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

```bash
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_USE_LOCALTIME = False
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None  EMAIL_TIMEOUT = None  DEFAULT_FROM_EMAIL = 'webmaster@localhost'
SERVER_EMAIL = 'root@localhost'
```


## Setup environment

1. Make Pipfile
2. Install pipenv and packages

```bash[bash]
cd app
pip install pipenv
pipenv install
pipenv shell
(app) django-admin.py startproject config .
(app) python manage.py migrate
(app) python manage.py runserver
```

## Setup docker

1. Make Dockerfile for Django
2. Make dokcer-compose.yml for Django

## Update settings.py

1. SECRET_KEY
2. DEBUG
3. ALLOWED_HOSTS

## Start via docker-compose

```bash[bash]
docker-compose up -d --build
```

## Setup postgres

1. Add postgres service in docker-compose.yml
2. Update .env for postgresql
3. Update settings.py
4. Update Dockerfile for psycopg2

Up docker-compose and migrate. So we can see welcome page on localhost:8000.

```bash[bash]
docker-compose down -v
docker-compose up -d --build
docker-compose exec django python manage.py migrate
```

### Setup auto migrate

1. Add entrypoint.sh
2. chmod +x entrypoint.sh
3. Update Dockerfile

```bash[bash]
chmod +x app/entrypoint.sh
```


## Setup Gunicorn

1. Add gunicorn in Pipfile
2. Add docker-compose.prod.yml and update
3. Add entrypoint.prod.sh
4. Add Dockerfile.prod
5. Update docker-compose.prod.yml for new Dockerfile.prod
6. CMD and check localhost:8000/admin

```bash[bash]
docker-compose down -v
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml exec django python manage.py migrate --noinput
```


## Setup Nginx

1. Make nginx dir to root
2. Add Dockerfile
3. Add nginx.conf
4. Add nginx in docker-compose.prod.yml
5. Check connection of nginx

```bash[bash]
docker-compose down -v
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml exec django python manage.py migrate --noinput
```


## Setup static file

1. Update settings.py
2. Update entrypoint.sh for collectstatic command
3. Update docker-compose.prod.yml for staticfiles
4. Update nginx.conf for staticfiles

```bash[bash]
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml exec django python manage.py migrate --noinput
docker-compose -f docker-compose.prod.yml exec django python manage.py collectstatic
```
