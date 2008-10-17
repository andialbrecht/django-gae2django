from django.contrib import admin

from codereview import models


class PatchSetInlineAdmin(admin.StackedInline):
    model = models.PatchSet


class PatchSetAdmin(admin.ModelAdmin):
    pass

class IssueAdmin(admin.ModelAdmin):

    list_display = ('id', 'subject', 'owner', 'modified', 'n_comments')
    list_display_links = ('id', 'subject')
    inlines = [PatchSetInlineAdmin]

admin.site.register(models.Issue, IssueAdmin)
admin.site.register(models.PatchSet, PatchSetAdmin)
