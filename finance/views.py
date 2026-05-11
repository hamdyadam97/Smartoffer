from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

from registrations.models import Account
from .models import Payment, PaymentOut, Deposit, Withdraw, BillBuyType, BillBuy, Offer, Call
from .forms import (
    PaymentForm, PaymentOutForm, DepositForm, WithdrawForm,
    BillBuyTypeForm, BillBuyForm, OfferForm, CallForm,
)


# ============================================================
# Payment Views
# ============================================================

class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'finance/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 20

    def get_queryset(self):
        queryset = Payment.objects.select_related('account', 'last_person').all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(code__icontains=search)
        account = self.request.GET.get('account')
        if account:
            queryset = queryset.filter(account_id=account)
        payment_type = self.request.GET.get('type')
        if payment_type:
            queryset = queryset.filter(type=payment_type)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accounts'] = Account.objects.select_related('student', 'course', 'course__master').all()
        return context


class PaymentDetailView(LoginRequiredMixin, DetailView):
    model = Payment
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'finance/payment_detail.html'
    context_object_name = 'payment'

    def get_queryset(self):
        return Payment.objects.select_related('account', 'last_person')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accounts'] = Account.objects.select_related('student', 'course', 'course__master').all()
        return context


class PaymentCreateView(LoginRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'finance/payment_form.html'
    success_url = reverse_lazy('payment-list')

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class PaymentUpdateView(LoginRequiredMixin, UpdateView):
    model = Payment
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    form_class = PaymentForm
    template_name = 'finance/payment_form.html'
    success_url = reverse_lazy('payment-list')

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class PaymentDeleteView(LoginRequiredMixin, DeleteView):
    model = Payment
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'finance/payment_confirm_delete.html'
    success_url = reverse_lazy('payment-list')


@require_POST
def payment_create_ajax(request):
    form = PaymentForm(request.POST)
    if form.is_valid():
        payment = form.save(commit=False)
        payment.last_person = request.user
        payment.save()
        return JsonResponse({'success': True, 'message': 'تم إنشاء السند بنجاح', 'id': payment.id, 'slug': payment.slug})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@require_POST
def payment_update_ajax(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    form = PaymentForm(request.POST, instance=payment)
    if form.is_valid():
        payment = form.save(commit=False)
        payment.last_person = request.user
        payment.save()
        return JsonResponse({'success': True, 'message': 'تم تحديث السند بنجاح'})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


# ============================================================
# PaymentOut Views
# ============================================================

class PaymentOutListView(LoginRequiredMixin, ListView):
    model = PaymentOut
    template_name = 'finance/paymentout_list.html'
    context_object_name = 'payment_outs'
    paginate_by = 20


class PaymentOutDetailView(LoginRequiredMixin, DetailView):
    model = PaymentOut
    template_name = 'finance/paymentout_detail.html'
    context_object_name = 'payment_out'


class PaymentOutCreateView(LoginRequiredMixin, CreateView):
    model = PaymentOut
    form_class = PaymentOutForm
    template_name = 'finance/paymentout_form.html'
    success_url = reverse_lazy('paymentout-list')

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class PaymentOutUpdateView(LoginRequiredMixin, UpdateView):
    model = PaymentOut
    form_class = PaymentOutForm
    template_name = 'finance/paymentout_form.html'
    success_url = reverse_lazy('paymentout-list')

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class PaymentOutDeleteView(LoginRequiredMixin, DeleteView):
    model = PaymentOut
    template_name = 'finance/paymentout_confirm_delete.html'
    success_url = reverse_lazy('paymentout-list')


# ============================================================
# Deposit Views
# ============================================================

class DepositListView(LoginRequiredMixin, ListView):
    model = Deposit
    template_name = 'finance/deposit_list.html'
    context_object_name = 'deposits'
    paginate_by = 20

    def get_queryset(self):
        return Deposit.objects.select_related('bank', 'last_person').all()


class DepositDetailView(LoginRequiredMixin, DetailView):
    model = Deposit
    template_name = 'finance/deposit_detail.html'
    context_object_name = 'deposit'

    def get_queryset(self):
        return Deposit.objects.select_related('bank', 'last_person')


class DepositCreateView(LoginRequiredMixin, CreateView):
    model = Deposit
    form_class = DepositForm
    template_name = 'finance/deposit_form.html'
    success_url = reverse_lazy('deposit-list')

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class DepositUpdateView(LoginRequiredMixin, UpdateView):
    model = Deposit
    form_class = DepositForm
    template_name = 'finance/deposit_form.html'
    success_url = reverse_lazy('deposit-list')

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class DepositDeleteView(LoginRequiredMixin, DeleteView):
    model = Deposit
    template_name = 'finance/deposit_confirm_delete.html'
    success_url = reverse_lazy('deposit-list')


# ============================================================
# Withdraw Views
# ============================================================

class WithdrawListView(LoginRequiredMixin, ListView):
    model = Withdraw
    template_name = 'finance/withdraw_list.html'
    context_object_name = 'withdraws'
    paginate_by = 20

    def get_queryset(self):
        return Withdraw.objects.select_related('bank', 'last_person').all()


class WithdrawDetailView(LoginRequiredMixin, DetailView):
    model = Withdraw
    template_name = 'finance/withdraw_detail.html'
    context_object_name = 'withdraw'

    def get_queryset(self):
        return Withdraw.objects.select_related('bank', 'last_person')


class WithdrawCreateView(LoginRequiredMixin, CreateView):
    model = Withdraw
    form_class = WithdrawForm
    template_name = 'finance/withdraw_form.html'
    success_url = reverse_lazy('withdraw-list')

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class WithdrawUpdateView(LoginRequiredMixin, UpdateView):
    model = Withdraw
    form_class = WithdrawForm
    template_name = 'finance/withdraw_form.html'
    success_url = reverse_lazy('withdraw-list')

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class WithdrawDeleteView(LoginRequiredMixin, DeleteView):
    model = Withdraw
    template_name = 'finance/withdraw_confirm_delete.html'
    success_url = reverse_lazy('withdraw-list')


# ============================================================
# BillBuyType Views
# ============================================================

class BillBuyTypeListView(LoginRequiredMixin, ListView):
    model = BillBuyType
    template_name = 'finance/billbuytype_list.html'
    context_object_name = 'bill_buy_types'
    paginate_by = 20


class BillBuyTypeDetailView(LoginRequiredMixin, DetailView):
    model = BillBuyType
    template_name = 'finance/billbuytype_detail.html'
    context_object_name = 'bill_buy_type'


class BillBuyTypeCreateView(LoginRequiredMixin, CreateView):
    model = BillBuyType
    form_class = BillBuyTypeForm
    template_name = 'finance/billbuytype_form.html'
    success_url = reverse_lazy('billbuytype-list')


class BillBuyTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = BillBuyType
    form_class = BillBuyTypeForm
    template_name = 'finance/billbuytype_form.html'
    success_url = reverse_lazy('billbuytype-list')


class BillBuyTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = BillBuyType
    template_name = 'finance/billbuytype_confirm_delete.html'
    success_url = reverse_lazy('billbuytype-list')


# ============================================================
# BillBuy Views
# ============================================================

class BillBuyListView(LoginRequiredMixin, ListView):
    model = BillBuy
    template_name = 'finance/billbuy_list.html'
    context_object_name = 'bill_buys'
    paginate_by = 20

    def get_queryset(self):
        return BillBuy.objects.select_related('bill_buy_type', 'last_person').all()


class BillBuyDetailView(LoginRequiredMixin, DetailView):
    model = BillBuy
    template_name = 'finance/billbuy_detail.html'
    context_object_name = 'bill_buy'

    def get_queryset(self):
        return BillBuy.objects.select_related('bill_buy_type', 'last_person')


class BillBuyCreateView(LoginRequiredMixin, CreateView):
    model = BillBuy
    form_class = BillBuyForm
    template_name = 'finance/billbuy_form.html'
    success_url = reverse_lazy('billbuy-list')

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class BillBuyUpdateView(LoginRequiredMixin, UpdateView):
    model = BillBuy
    form_class = BillBuyForm
    template_name = 'finance/billbuy_form.html'
    success_url = reverse_lazy('billbuy-list')

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class BillBuyDeleteView(LoginRequiredMixin, DeleteView):
    model = BillBuy
    template_name = 'finance/billbuy_confirm_delete.html'
    success_url = reverse_lazy('billbuy-list')


# ============================================================
# Offer Views
# ============================================================

class OfferListView(LoginRequiredMixin, ListView):
    model = Offer
    template_name = 'finance/offer_list.html'
    context_object_name = 'offers'
    paginate_by = 20

    def get_queryset(self):
        queryset = Offer.objects.select_related('master', 'master__branch', 'last_person').all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(customer_name__icontains=search)
        master = self.request.GET.get('master')
        if master:
            queryset = queryset.filter(master_id=master)
        registered = self.request.GET.get('registered')
        if registered is not None:
            queryset = queryset.filter(registered=registered.lower() == 'true')
        return queryset


class OfferDetailView(LoginRequiredMixin, DetailView):
    model = Offer
    template_name = 'finance/offer_detail.html'
    context_object_name = 'offer'

    def get_queryset(self):
        return Offer.objects.select_related('master', 'master__branch', 'last_person')


class OfferCreateView(LoginRequiredMixin, CreateView):
    model = Offer
    form_class = OfferForm
    template_name = 'finance/offer_form.html'
    success_url = reverse_lazy('offer-list')

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class OfferUpdateView(LoginRequiredMixin, UpdateView):
    model = Offer
    form_class = OfferForm
    template_name = 'finance/offer_form.html'
    success_url = reverse_lazy('offer-list')

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class OfferDeleteView(LoginRequiredMixin, DeleteView):
    model = Offer
    template_name = 'finance/offer_confirm_delete.html'
    success_url = reverse_lazy('offer-list')


# ============================================================
# Call Views
# ============================================================

class CallListView(LoginRequiredMixin, ListView):
    model = Call
    template_name = 'finance/call_list.html'
    context_object_name = 'calls'
    paginate_by = 20

    def get_queryset(self):
        queryset = Call.objects.select_related('offer', 'person').all()
        offer = self.request.GET.get('offer')
        if offer:
            queryset = queryset.filter(offer_id=offer)
        person = self.request.GET.get('person')
        if person:
            queryset = queryset.filter(person_id=person)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offers'] = Offer.objects.select_related('master').all()
        return context


class CallDetailView(LoginRequiredMixin, DetailView):
    model = Call
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'finance/call_detail.html'
    context_object_name = 'call'

    def get_queryset(self):
        return Call.objects.select_related('offer', 'person')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offers'] = Offer.objects.select_related('master').all()
        return context


class CallCreateView(LoginRequiredMixin, CreateView):
    model = Call
    form_class = CallForm
    template_name = 'finance/call_form.html'
    success_url = reverse_lazy('call-list')

    def form_valid(self, form):
        form.instance.person = self.request.user
        return super().form_valid(form)


class CallUpdateView(LoginRequiredMixin, UpdateView):
    model = Call
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    form_class = CallForm
    template_name = 'finance/call_form.html'
    success_url = reverse_lazy('call-list')

    def form_valid(self, form):
        form.instance.person = self.request.user
        return super().form_valid(form)


class CallDeleteView(LoginRequiredMixin, DeleteView):
    model = Call
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'finance/call_confirm_delete.html'
    success_url = reverse_lazy('call-list')


@require_POST
def call_create_ajax(request):
    form = CallForm(request.POST)
    if form.is_valid():
        call = form.save(commit=False)
        call.person = request.user
        call.save()
        return JsonResponse({'success': True, 'message': 'تم إنشاء المكالمة بنجاح', 'id': call.id, 'slug': call.slug})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@require_POST
def call_update_ajax(request, pk):
    call = get_object_or_404(Call, pk=pk)
    form = CallForm(request.POST, instance=call)
    if form.is_valid():
        call = form.save(commit=False)
        call.save()
        return JsonResponse({'success': True, 'message': 'تم تحديث المكالمة بنجاح'})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)
