from django.db import models
import datetime
from django.utils import timezone
from django.contrib.auth.models import User

class CheckList(models.Model):
    checklist_title = models.CharField(max_length=100)
    pub_date = models.DateTimeField('date published')
    due_date = models.DateTimeField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    def __repr__(self):
        return "Checklist %s" % self.checklist_title
    def __str__(self):
        return self.__repr__()
    def due_soon(self):
        return timezone.now()  <= self.due_date <= timezone.now() + datetime.timedelta(days=1)
    def past_due(self):
        return timezone.now() >= self.due_date
    def is_complete(self):
        for item in self.checklistitem_set.all():
            if not item.complete:
                return False
        return True

class CheckListItem(models.Model):
    item_title = models.CharField(max_length=100)
    item_desc = models.CharField('description', max_length=350)
    complete = models.BooleanField(default=False)
    checklist = models.ForeignKey(CheckList, on_delete=models.CASCADE)
    def __repr__(self):
        return "Item %s (%s); complete = %s" %(self.item_title, self.checklist.__str__(), str(self.complete))
    def __str__(self):
        return self.__repr__()