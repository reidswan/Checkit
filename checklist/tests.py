from django.test import TestCase
from django.utils import timezone
import datetime
from checklist.models import CheckList, CheckListItem

class CheckListTests(TestCase):
    def test_not_due_soon_on_past_due_date(self):
        """
        Checks that CheckList.due_soon() returns False on questions past due date
        """
        c = CheckList(pub_date=timezone.now(), due_date=timezone.now() - datetime.timedelta(days=2), checklist_title="Test")
        self.assertIs(c.due_soon(), False)

    def test_not_past_due_if_due_date_in_future(self):
        """
        Checks that Checklist.past_due() returns False on questions with future due dates
        """
        c = CheckList(pub_date=timezone.now(), due_date = timezone.now() + datetime.timedelta(days=2), checklist_title="Test")
        self.assertIs(c.past_due(), False)

    def test_due_soon_on_soon_due_date(self):
        """
        Checks that CheckList.due_soon() returns False on questions past due date
        """
        c = CheckList(pub_date=timezone.now(), due_date=timezone.now() + datetime.timedelta(hours=1), checklist_title="Test")
        self.assertIs(c.due_soon(), True)

    def test_not_past_due_if_due_date_in_past(self):
        """
        Checks that Checklist.past_due() returns False on questions with future due dates
        """
        c = CheckList(pub_date=timezone.now(), due_date = timezone.now() - datetime.timedelta(days=1), checklist_title="Test")
        self.assertIs(c.past_due(), True)

    def test_incomplete_checklists(self):
        """
        Checks that CheckList.due_soon() returns False on questions past due date
        """
        c = CheckList(pub_date=timezone.now(), due_date=timezone.now() + datetime.timedelta(days=10), checklist_title="Test")
        c.save()
        items = [CheckListItem(item_title="t1", item_desc="t1", complete=False), 
                CheckListItem(item_title="t2", item_desc="t2", complete=False),
                CheckListItem(item_title="t3", item_desc="t3", complete=False)]
        for i in items:
            i.checklist = c
            i.save()
        self.assertIs(c.is_complete(), False)
        items[0].complete = True
        items[1].complete = True
        self.assertIs(c.is_complete(), False)
    
    def test_complete_checklists(self):
        """
        Checks that CheckList.due_soon() returns False on questions past due date
        """
        c = CheckList(pub_date=timezone.now(), due_date=timezone.now() + datetime.timedelta(days=10), checklist_title="Test")
        c.save()
        items = [CheckListItem(item_title="t1", item_desc="t1", complete=True, checklist=c), 
                CheckListItem(item_title="t2", item_desc="t2", complete=True, checklist=c)]
        for i in items:
            i.save()
        self.assertIs(c.is_complete(), True)