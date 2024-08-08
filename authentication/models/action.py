from typing import Any
from core import models


class RootActionManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(parent=None)


class Action(models.Model):
    objects = models.Manager()
    roots = RootActionManager()
    path = models.CharField(
        max_length=255,
        unique=True,
    )
    title = models.CharField(max_length=100)
    is_loggable = models.BooleanField(default=True)
    parent = models.ForeignKey(
        to="Action",
        related_name="children",
        related_query_name="child",
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
    )
    is_visible = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title

    @staticmethod
    def register_actions(actions, print_logs=False):
        existing_actions = Action.objects.all().only("path")
        to_insert = []
        to_update = []
        no_changes = []
        for action in actions:
            obj = None
            for existing_action in existing_actions:
                if existing_action.path == action.path:
                    obj = existing_action
            if obj:
                if obj.title == action.title and obj.is_loggable == action.is_loggable:
                    no_changes.append(action)
                else:
                    obj.title = action.title
                    to_update.append(obj)
            else:
                to_insert.append(action)
        Action.objects.bulk_create(to_insert)
        for action in to_update:
            action.save()
        if print_logs:
            print(f"\t{len(to_insert)} new action created")
            print(f"\t{len(to_update)} action titles updated")
            print(f"\t{len(no_changes)} actions had no changes")
        Action.reassing_parents(print_logs)

        return actions

    @staticmethod
    def reassing_parents(print_logs=False):
        actions = Action.objects.all()
        count = 0
        for action in actions:
            parent = action.parent
            parent_changed = False
            for possible_parent in actions:
                if action.path.startswith(possible_parent.path) and len(
                    action.path
                ) > len(possible_parent.path):
                    if not parent or len(possible_parent.path) > len(parent.path):
                        parent = possible_parent
                        parent_changed = True
            if parent_changed:
                count += 1
                action.parent = parent
                action.save()
        if print_logs:
            print(f"\t{count} action parents updated")

    @staticmethod
    def register_action(action):
        actions = [action]
        Action.register_actions(actions)

    @staticmethod
    def get_longest(actions):
        longest = None
        for action in actions:
            if longest is None or len(action.path) > len(longest.path):
                longest = action
        return longest
