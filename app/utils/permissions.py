"""Permission Checking"""
def has_permission(user, permission):
    """Check if user has specific permission"""
    if user.role == 'admin':
        return True
    # Add more sophisticated permission checking here
    return False

def can_edit(user, resource):
    """Check if user can edit resource"""
    if user.role == 'admin':
        return True
    if hasattr(resource, 'created_by') and resource.created_by == user.id:
        return True
    return False

def can_delete(user, resource):
    """Check if user can delete resource"""
    if user.role == 'admin':
        return True
    return False
