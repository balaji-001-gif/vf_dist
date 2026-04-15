import frappe

def get_context(context):
    context.no_cache = 1
    
    # Supply default values for variables expected in the template
    # to prevent Jinja DebugUndefined format errors.
    context.items = []
    context.orders = []
    
    return context
