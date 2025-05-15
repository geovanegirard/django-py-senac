from django.shortcuts import redirect

def validate_login(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            return redirect('login')  
        return view_func(request, *args, **kwargs)
    return wrapper
