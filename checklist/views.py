from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse, HttpResponseRedirect, HttpResponseForbidden
from checklist.models import CheckList, CheckListItem
from checklist.utils import parse_datetime
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User, AnonymousUser
import datetime
import re


recent_filter_delta = datetime.timedelta(days=1)
emailregex = re.compile(r"^([a-zA-Z0-9\+\-_]+[\.]?)+@([a-zA-Z0-9\+\-_]+[\.]?)+\.[a-z]{2,}$")

def index(request):
    if request.user.is_authenticated():
        u = request.user
        recent_checklists = [checklist for checklist in u.checklist_set.order_by('due_date') if not checklist.is_complete()]
        context = {
            'checklists' : recent_checklists,
            'empty_list_string' : 'You have no incomplete checklists!',
            'redirect_link' : reverse('checklist:complete'),
            'redirect_string' : 'See completed checklists',
            'page_title' : 'Checklists',
        }
        return render(request, 'checklist/index.html', context)
    new_user_checklist = User.objects.get(username="anon").checklist_set.first()
    new_user_checklist.due_date = timezone.now() + recent_filter_delta
    return render(request, 'checklist/new_user.html', { "checklist" : new_user_checklist })

def complete(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse("checklist:login"))
    u = request.user
    recent_checklists = [checklist for checklist in u.checklist_set.order_by('due_date') if checklist.is_complete()]
    context = {
        'checklists' : recent_checklists,
        'empty_list_string' : 'You have no completed checklists!',
        'redirect_link' : reverse('checklist:index'),
        'redirect_string' : 'See incomplete checklists',
        'page_title' : 'Completed Checklists',
    }
    return render(request, 'checklist/index.html', context)

def all(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse("checklist:login"))
    context = {
        'checklists' : request.user.checklist_set.order_by('due_date'),
        'empty_list_string' : 'You have no checklists yet!',
        'redirect_link' : '#',
        'redirect_string' : 'Make one!',
        'page_title' : 'All Checklists',
    }
    return render(request, 'checklist/index.html', context)

def checklist_view(request, checklist_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse("checklist:login"))
    checklist = get_object_or_404(CheckList, pk=checklist_id)
    if request.user.pk != checklist.owner.pk:
        return make_error(request, "Access error", "You do not have permission to view this checklist")
    return render(request, 'checklist/view.html', {'checklist' : checklist})

def post_edit(request):
    '''Handle edit POST before redirecting'''
    if not request.user.is_authenticated:
        raise Http404("")
    if request.method != "POST": # only handle POSTed edits
        raise Http404("")
    if 'checklist_id' not in request.POST.keys() or request.POST['checklist_id'] in ["None", None, '']: # from /new
        print("NEW! :D") # debug
        checklist = CheckList(pub_date=timezone.now(), due_date = timezone.now() + datetime.timedelta(days=1))
        checklist.owner = request.user
    else: # from /edit
        checklist_id = int(request.POST['checklist_id'])
        checklist = get_object_or_404(CheckList, pk=checklist_id)
    if checklist.owner.pk != request.user.pk:
        raise Http404("")
    if "title" in request.POST.keys():
        checklist.checklist_title = request.POST["title"]
    if "duedate_date" in request.POST.keys() and "duedate_time" in request.POST.keys():
        dt = parse_datetime(request.POST["duedate_date"], request.POST["duedate_time"])
        checklist.due_date = dt
    checklist.save() # ensure the checklist has a primary key, and commit title and due_date change (if made)
    for item in checklist.checklistitem_set.all(): # first check for edits and deletes of existing items
        title_key = "item" + str(item.id) + "_title"
        desc_key = "item" + str(item.id) + "_desc"
        if title_key in request.POST.keys() and request.POST[title_key] != "":
            print("modifying") # debug
            item.item_title = request.POST[title_key] 
            item.item_desc = request.POST[desc_key]
            item.save()
        else:
            print("deleting") #debug
            item.delete()
    handled = [] # ensure items aren't added twice 
    for key in request.POST.keys(): # check for added items
        # print(key) #debugging 
        if key.startswith("itemnew") and key not in handled:
            title_k, desc_k = "", ""
            if key.endswith("desc"):
                desc_k = key
                title_k = key.replace("desc", "title")
            else:
                title_k = key
                desc_k = key.replace("title", "desc")
            handled += [title_k, desc_k] # prevent double add (on encountering e.g. newitem3_title and newitem3_desc)
            title, desc = request.POST[title_k], request.POST[desc_k]
            new_item = CheckListItem(item_title=title, item_desc=desc, complete=False)
            new_item.checklist = checklist
            new_item.save() # commit changes 
    return HttpResponseRedirect(reverse('checklist:view', args=[checklist.pk]))

def new_checklist(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse("checklist:login"))
    return render(request, 'checklist/edit.html', {'checklist' : CheckList(), 'page_title' : 'New Checklist'})

def checklist_edit(request, checklist_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse("checklist:login"))
    checklist = get_object_or_404(CheckList, pk=checklist_id)
    if request.user.pk != checklist.owner.pk:
        return make_error(request, "Access error", "You do not have permission to view this checklist")
    return render(request, 'checklist/edit.html', {'checklist' : checklist, 'page_title' : 'Edit Checklist'})

def item_check(request):
    if not request.user.is_authenticated():
        return
    if 'checklist' in request.POST.keys() and 'checklist_item' in request.POST.keys():
        checklist = CheckList.objects.get(pk=request.POST['checklist'])
        citem = CheckListItem.objects.get(pk=request.POST['checklist_item'])
        if not citem.checklist == checklist:
            return HttpResponseForbidden()
        elif not checklist.owner.pk == request.user.pk:
            return HttpResponseForbidden()
        a = request.POST["value"]
        if a == 'true':
           a = True
        else:
            a = False 
        citem.complete = a
        citem.save()
    return JsonResponse({})

def emailvalidate(request):
    if request.method != "POST":
        raise Http404("Cannot find resource")
    result = {
        'user_exists' : User.objects.filter(username=request.POST["email"]).count() > 0,
    }
    return JsonResponse(result)

def register(request, email_errors = "", pwd_errors = ""):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("checklist:index"))
    return render(request, 'checklist/register.html', context={ "email_errors" : email_errors, "pwd_errors" : pwd_errors })

def register_result(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("checklist:index"))
    if request.method != "POST":
        return HttpResponseRedirect(reverse("checklist:index"))
    keys = ["inputEmail", "inputPassword", "inputConfirm"]
    for key in keys:
        if not key in request.POST.keys():
            raise Http404("an expected key was not supplied")
    email_addr = request.POST["inputEmail"]
    pwd = request.POST["inputPassword"]
    pwdConfirm = request.POST["inputConfirm"]
    email_errors= []
    password_errors = []
    if pwd != pwdConfirm:
        password_errors.append("Passwords must match")
    if len(pwd) < 8:
        password_errors.append("Password must be at least 8 characters long")
    if User.objects.filter(username=email_addr).count() > 0:
        email_errors.append("That email is taken")
    if emailregex.match(email_addr) is None:
        email_errors.append("Email not in an acceptable format")
    if email_errors != [] or password_errors != []:
        return register(request, "; ".join(email_errors), "; ".join(password_errors))
    else:
        u = User.objects.create_user(username=email_addr, password=pwd)
        if u is not None:
            login(request, u)
        return HttpResponseRedirect(reverse('checklist:index'))

def logout_view(request):
    if request.user.is_authenticated():
        logout(request)
    return HttpResponseRedirect(reverse("checklist:index"))

def login_view(request, errors=""):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("checklist:index"))
    return render(request, 'checklist/login.html', context={'errors' : errors=="_err"})

def login_result(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("checklist:index"))
    for key in ["inputEmail", "inputPassword"]:
        if not key in request.POST.keys():
            raise Http404("an expected key was not supplied")
    email_addr = request.POST["inputEmail"]
    pwd = request.POST["inputPassword"]
    user = authenticate(username=email_addr, password=pwd)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse("checklist:index"))
    return HttpResponseRedirect(reverse("checklist:login_error", kwargs={"errors":"_err"}))
    
def error(request):
    if "e_title" not in request.GET.keys() or "e_msg" not in request.GET.keys():
        context={
            "error_title" : "Badly specified error message",
            "error_text" : "Error message is missing one or more fields"
        }
    else:
        context = {
            "error_title" : request.GET["e_title"],
            "error_text" : request.GET["e_msg"]
        }
    return render(request, "checklist/error.html", context)

def make_error(request, title, desc):
    return render(request, "checklist/error.html", {"error_title" : title, "error_text" : desc})