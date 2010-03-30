from datetime import datetime

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

from groups.base import Group



class Project(Group):
    
    member_users = models.ManyToManyField(User,
        through = "ProjectMember",
        verbose_name = _("members")
    )
    
    # private means only members can see the project
    private = models.BooleanField(_("private"), default=False)
    
    def get_absolute_url(self):
        return reverse("project_detail", kwargs={"group_slug": self.slug})
    
    def member_queryset(self):
        return self.member_users.all()
    
    def user_is_member(self, user):
         return ProjectMember.objects.filter(project=self, user=user).exists()


class ProjectMember(models.Model):
    
    project = models.ForeignKey(Project,
        related_name = "members",
        verbose_name = _("project")
    )
    user = models.ForeignKey(User,
        related_name = "projects",
        verbose_name = _("user")
    )
    away = models.BooleanField(_("away"), default=False)
    away_message = models.CharField(_("away_message"), max_length=500)
    away_since = models.DateTimeField(_("away since"), default=datetime.now)
    
    class Meta:
        unique_together = [("user", "project")]
