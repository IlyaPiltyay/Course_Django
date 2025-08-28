from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404

from mailings.models import Newsletter


class DisableNewsletterMixin(PermissionRequiredMixin):
    permission_required = 'mailings.disable_newsletter'
    raise_exception = True

    def disable_newsletter(self, newsletter_id):
        newsletter = get_object_or_404(Newsletter, id=newsletter_id)
        newsletter.is_active = False
        newsletter.save()

    def enable_newsletter(self, newsletter_id):
        newsletter = get_object_or_404(Newsletter, id=newsletter_id)
        newsletter.is_active = True
        newsletter.save()
