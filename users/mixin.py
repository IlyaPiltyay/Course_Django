from django.contrib.auth.mixins import PermissionRequiredMixin


class ViewAllClientsMixin(PermissionRequiredMixin):
    permission_required = 'mailings.view_all_clients'
    raise_exception = True


class BlockUserMixin(PermissionRequiredMixin):
    permission_required = 'mailings.block_user'
    raise_exception = True  # Будет выбрасывать 403 статус, если нет прав
