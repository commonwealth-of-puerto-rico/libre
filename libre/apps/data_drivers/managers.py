from django.db import models


class SourceAccessManager(models.Manager):
    def for_user(self, user):
        if user.is_superuser or user.is_staff:
            return self.get_query_set()
        else:
            # Typecast as list to avoid unresolved "'NoneType' object has no attribute '_meta'" error = "Marronazo!"
            return self.get_query_set().filter(allowed_groups__in=list(user.groups.all()))
