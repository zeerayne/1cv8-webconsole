class AuthRequired(Exception):
    pass


class AdminAuthRequired(AuthRequired):
    pass


class ClusterAdminAuthRequired(AdminAuthRequired):
    pass
