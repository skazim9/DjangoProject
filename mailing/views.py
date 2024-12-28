import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import UpdateView, DeleteView, CreateView

from config.settings import EMAIL_HOST_USER
from mailing.forms import RecipientForm, MessageForm, MailingForm
from mailing.models import Recipient, Message, Mailing, AttemptSending
from users.models import User


class HomeView(TemplateView):
    template_name = "mailing/home.html"


class MainPageView(LoginRequiredMixin, TemplateView):
    template_name = "mailing/main_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["user"] = User.objects.get(pk=self.request.user.pk)
        context["total_mailing"] = Mailing.objects.count()
        context["active_mailing"] = Mailing.objects.filter(status="created").count()
        context["unique_recipients"] = Recipient.objects.distinct().count()

        return context


class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient


class RecipientDetailsView(LoginRequiredMixin, DetailView):
    model = Recipient


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailing:recipient_list")

    def form_valid(self, form):
        recipient = form.save()
        user = self.request.user
        recipient.owner = user
        recipient.save()
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailing:recipient_list")


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipient
    success_url = reverse_lazy("mailing:recipient_list")


class MessageListView(LoginRequiredMixin, ListView):
    model = Message


class MessageDetailsView(LoginRequiredMixin, DetailView):
    model = Message


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:message_list")


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:message_list")


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    success_url = reverse_lazy("mailing:message_list")


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing


class MailingDetailsView(LoginRequiredMixin, DetailView):
    model = Mailing


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailing:mailing_list")

    def form_valid(self, form):
        mailing = form.save()
        user = self.request.user
        mailing.owner = user
        mailing.save()
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailing:mailing_list")


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    success_url = reverse_lazy("mailing:mailing_list")


class MailingSendView(LoginRequiredMixin, View):
    def get(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        return render(request, 'mailing/mailing_send.html', {'mailing': mailing})

    def post(self, request, pk, *args, **kwargs):
        mailing = get_object_or_404(Mailing, pk=pk)

        if mailing and mailing.status == "created" and mailing.enabled is True:
            recipients = mailing.recipients.all()

            for recipient in recipients:
                try:
                    send_mail(mailing.message.topic, mailing.message.text, EMAIL_HOST_USER, [recipient.email])

                    AttemptSending.objects.create(mailing=mailing, status="success",
                                              response="Сообщение отправлено успешно")

                except Exception as e:
                    AttemptSending.objects.create(mailing=mailing, status="not_success", response=str(e))

        mailing.status = "launched"
        mailing.save()

        return redirect("mailing:mailing_list")


class MailingReportView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["successful_attempts"] = self.object.attempts.filter(status="success").count()
        context["failed_attempts"] = self.object.attempts.filter(status="not_success").count()
        context["total_attempts"] = self.object.attempts.count()

        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        return super().get(request, *args, **kwargs)


class DisabledMailingView(LoginRequiredMixin, View):

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, id=pk)

        if not request.user.has_perm('mailing.can_disabling_mailing'):
            return HttpResponseForbidden("У вас недостаточно прав для отключения рассылки")

        mailing.status = "completed"
        mailing.save()

        return redirect('mailing:mailing', pk=mailing.id)