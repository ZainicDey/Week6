class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('password_change_done')

    def form_valid(self, form):
        response = super().form_valid(form)
        send_mail(
            'Password Change Notification',
            'Your password has been changed successfully.',
            'ihanik.ad@example.com',
            [self.request.user.email],
            fail_silently=False,
        )
        return response
