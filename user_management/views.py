from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

class DILMLoginView(LoginView):
    redirect_authenticated_user = True
    fields = '__all__'
    
    def get_success_url(self):
        return reverse_lazy('home')
    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))