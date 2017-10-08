from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse, HttpResponseRedirect
from checklist.models import CheckList, CheckListItem
from checklist.utils import parse_datetime
from django.utils import timezone
from django.urls import reverse
import datetime

recent_filter_delta = datetime.timedelta(days=1)

def index(request):
    recent_checklists = [checklist for checklist in CheckList.objects.order_by('due_date') if not checklist.is_complete()]
    context = {
        'checklists' : recent_checklists,
        'empty_list_string' : 'You have no incomplete checklists!',
        'redirect_link' : reverse('checklist:complete'),
        'redirect_string' : 'See completed checklists',
        'page_title' : 'Checklists',
    }
    return render(request, 'checklist/index.html', context)

def complete(request):
    recent_checklists = [checklist for checklist in CheckList.objects.order_by('due_date') if checklist.is_complete()]
    context = {
        'checklists' : recent_checklists,
        'empty_list_string' : 'You have no completed checklists!',
        'redirect_link' : reverse('checklist:index'),
        'redirect_string' : 'See incomplete checklists',
        'page_title' : 'Completed Checklists',
    }
    return render(request, 'checklist/index.html', context)

def all(request):
    context = {
        'checklists' : CheckList.objects.order_by('due_date'),
        'empty_list_string' : 'You have no checklists yet!',
        'redirect_link' : '#',
        'redirect_string' : 'Make one!',
        'page_title' : 'All Checklists',
    }
    return render(request, 'checklist/index.html', context)

def checklist_view(request, checklist_id):
    checklist = get_object_or_404(CheckList, pk=checklist_id)
    return render(request, 'checklist/view.html', {'checklist' : checklist})

def post_edit(request):
    '''Handle edit POST before redirecting'''
    if request.method != "POST": # only handle POSTed edits
        return
    if 'checklist_id' not in request.POST.keys() or request.POST['checklist_id'] == '': # from /new
        print("NEW! :D") # debug
        checklist = CheckList(pub_date=timezone.now(), due_date = timezone.now() + datetime.timedelta(days=1))
    else: # from /edit
        checklist_id = int(request.POST['checklist_id'])
        checklist = get_object_or_404(CheckList, pk=checklist_id)
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
    return render(request, 'checklist/edit.html', {'checklist' : CheckList(), 'page_title' : 'New Checklist'})

def checklist_edit(request, checklist_id):
    checklist = get_object_or_404(CheckList, pk=checklist_id)
    return render(request, 'checklist/edit.html', {'checklist' : checklist, 'page_title' : 'Edit Checklist'})

def item_check(request):
    if 'checklist' in request.POST.keys() and 'checklist_item' in request.POST.keys():
        checklist = CheckList.objects.get(pk=request.POST['checklist'])
        citem = CheckListItem.objects.get(pk=request.POST['checklist_item'])
        if not citem.checklist == checklist:
            return
        a = request.POST["value"]
        if a == 'true':
           a = True
        else:
            a = False 
        citem.complete = a
        citem.save()
    return JsonResponse({})