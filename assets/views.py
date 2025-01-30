# assets/views.py

import json
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from django.contrib.auth import update_session_auth_hash, authenticate
from django.views.generic import ListView, CreateView, DetailView, TemplateView, UpdateView
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django import forms

from .models import Asset, AssetPrice, PriceTunnel, Frequency
from .forms import AssetForm, PriceTunnelForm, FrequencyForm

class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'assets/asset_list.html'
    context_object_name = 'assets'

    def get_queryset(self):
        queryset = Asset.objects.filter(user=self.request.user).select_related(
            'price_tunnel', 
            'frequency',
            'available_asset'
        )

        # Handle search
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(available_asset__ticker__icontains=search_query) |
                Q(available_asset__name__icontains=search_query)
            )

        # Handle sorting
        sort_by = self.request.GET.get('sort', 'ticker')
        if sort_by == 'ticker':
            queryset = queryset.order_by('available_asset__ticker')
        elif sort_by == '-ticker':
            queryset = queryset.order_by('-available_asset__ticker')
        elif sort_by == 'name':
            queryset = queryset.order_by('available_asset__name')
        elif sort_by == '-name':
            queryset = queryset.order_by('-available_asset__name')
        elif sort_by == 'frequency':
            queryset = queryset.order_by('frequency__interval_minutes')
        elif sort_by == '-frequency':
            queryset = queryset.order_by('-frequency__interval_minutes')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['sort_by'] = self.request.GET.get('sort', 'ticker')
        return context


class AssetCreateView(LoginRequiredMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = 'assets/asset_create.html'
    success_url = reverse_lazy('asset_list')

    def form_valid(self, form):
        form.instance.user = self.request.user  # Associate the asset with the current user
        response = super().form_valid(form)
        messages.success(self.request, "Asset created successfully.")
        return response

class AssetDetailView(LoginRequiredMixin, DetailView):
    model = Asset
    template_name = 'assets/asset_detail.html'
    context_object_name = 'asset'
    paginate_by = 20

    def get_queryset(self):
        return Asset.objects.filter(user=self.request.user).select_related(
            'price_tunnel', 
            'frequency',
            'available_asset'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all prices for the chart
        prices = self.object.prices.order_by('-timestamp')
        
        # Prepare price data for the chart
        price_data = [
            {
                'timestamp': price.timestamp.isoformat(),
                'price': float(price.price)
            }
            for price in prices
        ]
        
        # Reverse the data so it's chronological for the chart
        price_data.reverse()
        
        # Add price data to context
        context['price_data'] = json.dumps(price_data)
        
        # Paginate the table view
        paginator = Paginator(prices, self.paginate_by)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        context.update({
            'page_obj': page_obj,
            'prices': page_obj.object_list,
            'tunnel_form': PriceTunnelForm(instance=getattr(self.object, 'price_tunnel', None)),
            'frequency_form': FrequencyForm(instance=getattr(self.object, 'frequency', None)),
        })
        
        return context

class AssetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Asset
    success_url = reverse_lazy('asset_list')
    template_name = 'assets/asset_confirm_delete.html'

    def test_func(self):
        """Ensure users can only delete their own assets"""
        asset = self.get_object()
        return self.request.user == asset.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, f"Asset {self.get_object().available_asset.ticker} has been removed.")
        return super().delete(request, *args, **kwargs)

    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to delete this asset.")
        return super().handle_no_permission()

class LandingPageView(TemplateView):
    template_name = 'landing_page.html'

    def get(self, request, *args, **kwargs):
        # If user is already authenticated, redirect to asset list
        if request.user.is_authenticated:
            return redirect('asset_list')
        return super().get(request, *args, **kwargs)

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'registration/profile.html'
    fields = ['email']
    success_url = reverse_lazy('profile')
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = kwargs
        if 'form' not in context:
            context['form'] = self.get_form()
        if 'password_form' not in context:
            context['password_form'] = PasswordChangeForm(self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        if 'password_change' in request.POST:
            # Handle password change form
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')
                return self.render_to_response(self.get_context_data(form=self.get_form()))
            else:
                # If password form is invalid, show errors
                return self.render_to_response(
                    self.get_context_data(
                        form=self.get_form(),
                        password_form=password_form
                    )
                )
        else:
            # Handle email update form
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, 'Your profile was successfully updated!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return self.render_to_response(self.get_context_data(form=form))

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            'Username or password is incorrect.'
        )
        return super().form_invalid(form)

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove help_text from all fields
        for field in self.fields.values():
            field.help_text = None

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created successfully! You can now login.')
        return response
    
@login_required
def update_tunnel_and_frequency(request, pk):
    asset = get_object_or_404(Asset.objects.filter(pk=pk, user=request.user), pk=pk)

    # Get or create price tunnel and frequency if they don't exist
    price_tunnel, _ = PriceTunnel.objects.get_or_create(
        asset=asset,
        defaults={'lower_limit': 0.00, 'upper_limit': 0.00}
    )
    
    frequency, _ = Frequency.objects.get_or_create(
        asset=asset,
        defaults={'interval_minutes': 5}
    )

    if request.method == 'POST':
        t_form = PriceTunnelForm(request.POST, instance=price_tunnel)
        f_form = FrequencyForm(request.POST, instance=frequency)
        if t_form.is_valid() and f_form.is_valid():
            t_form.save()
            f_form.save()
            messages.success(request, "Configuration updated successfully.")
            return redirect('asset_detail', pk=asset.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        t_form = PriceTunnelForm(instance=price_tunnel)
        f_form = FrequencyForm(instance=frequency)

    return render(request, 'assets/asset_detail.html', {
        'asset': asset,
        'tunnel_form': t_form,
        'frequency_form': f_form,
        'prices': asset.prices.all().order_by('-timestamp'),
    })