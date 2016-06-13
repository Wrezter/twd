from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from datetime import datetime

from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from rango.helper import decode_url, encode_url


def index(request):
    context = RequestContext(request)
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}

    for category in category_list:
        category.url = encode_url(category.name)

    # #### NEW CODE ####
    # # Obtain our Response object early so we can add cookie information.
    # response = render_to_response('rango/index.html', context_dict, context)
    # # Get the number of visits to the site.
    # # We use the COOKIES.get() function to obtain the visits cookie.
    # # If the cookie exists, the value returned is casted to an integer.
    # # If the cookie doesn't exist, we default to one and cast that.
    # visits = int(request.COOKIES.get('visits', '1'))
    # # Does the cookie last_visit exist?
    # if 'last_visit' in request.COOKIES:
    #     # Yes it does! Get the cookie's value.
    #     last_visit = request.COOKIES['last_visit']
    #     # Cast the value to a Python date/time object.
    #     last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
    #     # If it's been more than a minute since the last visit...
    #     if (datetime.now() - last_visit_time).seconds > 60:
    #         # ...reassign the value of the cookie to +1 of what it was before...
    #         response.set_cookie('visits', visits + 1)
    #         # ...and update the last visit cookie, too.
    #         response.set_cookie('last_visit', datetime.now())
    # else:
    #     # Cookie last_visit doesn't exist, so create it to the current date/time.
    #     response.set_cookie('last_visit', datetime.now())
    #     response.set_cookie('visits', visits)
    # # Return response back to the user, updating any cookies that need changed.
    # return response
    # #### END NEW CODE ####

    if request.session.get('last_visit'):
        last_visit_time = request.session.get('last_visit')
        visits = request.session.get('visits', 1)

        if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).seconds > 5:
            request.session['visits'] = visits + 1
            request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = 1

    context_dict['cat_list'] = get_category_list()

    return render_to_response('rango/index.html', context_dict, context)


def category(request, category_name_url):
    context = RequestContext(request)
    category_name = decode_url(category_name_url)
    context_dict = {'category_name': category_name, 'category_name_url': category_name_url}

    try:
        category = Category.objects.get(name=category_name)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        pass

    context_dict['cat_list'] = get_category_list()

    return render_to_response('rango/category.html', context_dict, context)


@login_required
def add_category(request):
    context = RequestContext(request)

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print form.errors
    else:
        form = CategoryForm()

    return render_to_response('rango/add_category.html', {'form': form, 'cat_list': get_category_list()}, context)


@login_required
def add_page(request, category_name_url):
    context = RequestContext(request)

    category_name = decode_url(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            page = form.save(commit=False)

            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                return render_to_response('rango/add_category.html', {}, context)

            page.views = 0
            page.save()

            return category(request, category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()

    return render_to_response('rango/add_page.html',
            {'category_name_url': category_name_url,
             'category_name': category_name, 'form': form,
             'cat_list': get_category_list()},
             context)


def register(request):
    context = RequestContext(request)
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True
        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render_to_response(
            'rango/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered,
             'cat_list': get_category_list()},
            context)


def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if password == '' or username == '':
            return HttpResponse("Missing username or password!")

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect('/rango/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied!")

    else:
        return render_to_response('rango/login.html', {'cat_list': get_category_list()}, context)


def about(request):
    context = RequestContext(request)
    context_dict = {'boldmessage': "chameleon", 'visit_num': request.session.get('visits', 1),
                    'last_visit': request.session.get('last_visit', datetime.now()), 'cat_list': get_category_list()}
    return render_to_response('rango/about.html', context_dict, context)


@login_required
def user_logout(request):
    logout(request)
    return redirect('/rango/')


def get_category_list():
    cat_list = Category.objects.all()

    for cat in cat_list:
        cat.url = encode_url(cat.name)

    return cat_list


@login_required
def profile(request):
    context = RequestContext(request)
    cat_list = get_category_list()
    context_dict = {'cat_list': cat_list}
    u = User.objects.get(username=request.user)

    try:
        up = UserProfile.objects.get(user=u)
    except:
        up = None

    context_dict['user'] = u
    context_dict['userprofile'] = up
    return render_to_response('rango/profile.html', context_dict, context)


def track_url(request):
    url = '/rango/'
    if request.method == 'GET' and 'page_id' in request.GET:
        page_id = request.GET['page_id']
        try:
            page = Page.objects.get(id=page_id)
            page.views += 1
            page.save()
            url = page.url
        except:
            pass

    return redirect(url)


@login_required
def change_profile(request):
    context = RequestContext(request)
    user_form = UserForm(instance=request.user)
    userprofile_form = UserProfileForm(instance=request.user.userprofile)

    if request.method == 'POST':
        user_form = UserForm(data=request.POST, instance=request.user)
        userprofile_form = UserProfileForm(data=request.POST, instance=request.user.userprofile)

        if user_form.is_valid() and userprofile_form.is_valid():

            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = userprofile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
        else:
            print user_form.errors
            print userprofile_form.errors

        return redirect('/rango/profile/')

    return render_to_response('rango/change_profile.html', {'user_form': user_form,
                                                            'userprofile_form': userprofile_form,
                                                            'cat_list': get_category_list()}, context)
