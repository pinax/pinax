# -*- coding: utf-8 -*-

"""
We break out workflow elements to enable us to more easily refactor in the
future.
"""

from django.contrib.auth.models import Group

TASK_MANAGER = 'coredev'

def always(task, user):
    return True

def is_assignee(task, user):
    if task.assignee == user:
        return True
    return False

def is_assignee_or_none(task, user):
    # current user is assignee or there is no assignee
    if task.assignee == user or not task.assignee:
        return True
    return False

def is_creator(task, user):
    if task.creator == user:
        return True
    return False

def is_task_manager(task, user):
    if not user or user.is_anonymous():
        return False
    if user.is_superuser:
        return True
    if Group.objects.filter(name__exact=TASK_MANAGER).filter(user=user):
        return True
    return False

def no_assignee(task, user):
    if not task.assignee:
        return True
    return False

def OR(*l):
    # lets you run multiple permissions against a single state transition
    return lambda *args: any(f(*args) for f in l)


STATE_TRANSITIONS = [
    # open
    (1, 1, always, "leave open"),
    (1, 7, is_task_manager, "accept"),
    (1, 2, is_task_manager, "resolved"),
    (1, 5, is_task_manager, "discussion needed"),
    (1, 6, is_task_manager, "blocked"),
    
    # resolved
    (2, 1, always, "re-open"),
    (2, 2, always, "leave resolved"),
    (2, 3, is_task_manager, "close"),
    (2, 7, is_task_manager, "re-open (accepted)"),
    
    # closed
    (3, 3, always, "leave closed"),
    (3, 1, is_task_manager, "re-open"),
    (3, 7, is_task_manager, "re-open (accepted)"),
    
    # in progress
    (4, 4, always, "still in progress"),
    (4, 5, is_assignee, "discussion needed"),
    (4, 6, is_task_manager, "blocked"),
    (4, 8, OR(is_assignee, is_task_manager), "fix needs review"),
    
    # discussion needed
    (5, 5, always, "discussion still needed"),
    (5, 4, OR(is_assignee, is_task_manager), "in progress"),
    (5, 1, is_task_manager, "move back to new"),
    (5, 2, is_task_manager, "resolved"),
    (5, 6, is_task_manager, "blocked"),
    
    # blocked
    (6, 6, always, "still blocked"),
    (6, 1, is_task_manager, "move back to new"),
    (6, 2, is_task_manager, "resolved"),
    (6, 4, is_task_manager, "in progress"),
    (6, 5, is_task_manager, "discussion needed"),
    
    # accepted
    (7, 7, always, "accepted"),
    (7, 4, is_assignee, "in progress"),
    (7, 2, is_task_manager, "resolved"),
    (7, 5, is_task_manager, "discussion needed"),
    (7, 6, is_task_manager, "blocked"),
    
    # fix needs review
    (8, 8, always, "fix needs review"),
    (8, 4, OR(is_assignee, is_task_manager), "move back to in progress"),
    (8, 2, is_task_manager, "resolved"),
]



STATE_CHOICES = (
    ('1', 'new'),
    ('4', 'in progress'), # the assignee is working on it
    ('5', 'discussion needed'), # discussion needed before work can proceed
    ('6', 'blocked'), # blocked on something or someone (other than discussion)
    ('2', 'resolved'), # the assignee thinks it's done
    ('3', 'closed'), # the creator has confirmed it's done
    ('7', 'accepted'), # a task_manager has accepted the task meaning it can be moved forward
    ('8', 'fix needs review') # the assignee wants the task manager to review things.
)


RESOLUTION_CHOICES = (
    ('1', 'fixed'),
    ('2', 'duplicate'),
    ('3', 'alreadydone — we have fixed this'),
    ('4', 'irrelevant — another change made this no longer an issue'),
    ('5', 'rejected — current behavior is as intended'),
    ('6', 'nonsense — bad ticket entry'),
    ('7', "worksforme — can't reproduce problem"),
)


REVERSE_STATE_CHOICES = dict((item[1], item[0]) for item in STATE_CHOICES)

STATE_CHOICES_DICT = dict((item[0], item[1]) for item in STATE_CHOICES)
RESOLUTION_CHOICES_DICT = dict((item[0], item[1]) for item in RESOLUTION_CHOICES)

STATE_ID_LIST = [x[0] for x in STATE_CHOICES]



def export_state_transitions(format='csv'):
    # ugly cowboy code that really needs refactoring
    rows = []
    for row in STATE_TRANSITIONS:
        record = ''
        current_state = STATE_CHOICES_DICT[str(row[0])]
        new_state = STATE_CHOICES_DICT[str(row[1])]
        permission = str(row[2]).split()[1]
        transition_name = row[3]
        record = """ "%s","%s","%s","%s" """ % (current_state, new_state, permission, transition_name)
        rows.append(record.strip())
    
    # ick turn this into a string.
    # TODO: to this right!
    text = ''
    for row in rows:
        text += row + '\n'
    return text

# lame hack to speed up shell scripts
ext = export_state_transitions