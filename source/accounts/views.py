from django.contrib import messages
from django.contrib.auth import login, authenticate, REDIRECT_FIELD_NAME
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LogoutView as BaseLogoutView, PasswordChangeView as BasePasswordChangeView,
    PasswordResetDoneView as BasePasswordResetDoneView, PasswordResetConfirmView as BasePasswordResetConfirmView,
)
from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme as is_safe_url
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import View, FormView
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.models import User
import re

from .utils import (
    send_activation_email, send_reset_password_email, send_forgotten_username_email, send_activation_change_email,
)
from .forms import (
    SignInViaUsernameForm, SignInViaEmailForm, SignInViaEmailOrUsernameForm, SignUpForm,
    RestorePasswordForm, RestorePasswordViaEmailOrUsernameForm, RemindUsernameForm,
    ResendActivationCodeForm, ResendActivationCodeViaEmailForm, CombinedProfileForm,
)
from .models import Activation, EmailAddressState, TermsAcceptance, NotificationPreference
from .models import EmailChangeAttempt, grant_early_premium
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required


class GuestOnlyView(View):
    def dispatch(self, request, *args, **kwargs):
        # Redirect to the index page if the user already authenticated
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)

        return super().dispatch(request, *args, **kwargs)


class LogInView(GuestOnlyView, FormView):
    template_name = 'accounts/log_in.html'

    @staticmethod
    def get_form_class(**kwargs):
        if settings.DISABLE_USERNAME or settings.LOGIN_VIA_EMAIL:
            return SignInViaEmailForm

        if settings.LOGIN_VIA_EMAIL_OR_USERNAME:
            return SignInViaEmailOrUsernameForm

        return SignInViaUsernameForm

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # Sets a test cookie to make sure the user has cookies enabled
        request.session.set_test_cookie()

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        request = self.request

        # If the test cookie worked, go ahead and delete it since its no longer needed
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()

        # The default Django's "remember me" lifetime is 2 weeks and can be changed by modifying
        # the SESSION_COOKIE_AGE settings' option.
        if settings.USE_REMEMBER_ME:
            if not form.cleaned_data['remember_me']:
                request.session.set_expiry(0)

        login(request, form.user_cache)

        redirect_to = request.POST.get(REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME))
        url_is_safe = is_safe_url(redirect_to, allowed_hosts=request.get_host(), require_https=request.is_secure())

        if url_is_safe:
            return redirect(redirect_to)

        return redirect(settings.LOGIN_REDIRECT_URL)


class SignUpView(GuestOnlyView, FormView):
    template_name = 'accounts/sign_up.html'
    form_class = SignUpForm

    def form_valid(self, form):
        request = self.request
        user = form.save(commit=False)

        if settings.DISABLE_USERNAME:
            # Set a temporary username
            user.username = get_random_string()
        else:
            user.username = form.cleaned_data['username']

        if settings.ENABLE_USER_ACTIVATION:
            user.is_active = False

        # Create a user record
        user.save()
        # Add email state (unconfirmed)
        EmailAddressState.objects.create(user=user, email=user.email, is_confirmed=False)
        # Record terms acceptance
        if form.cleaned_data.get('accept_terms'):
            TermsAcceptance.objects.create(user=user)

        # Change the username to the "user_ID" form
        if settings.DISABLE_USERNAME:
            user.username = f'user_{user.id}'
            user.save()

        if settings.ENABLE_USER_ACTIVATION:
            code = get_random_string(20)

            act = Activation()
            act.code = code
            act.user = user
            act.save()

            # Try to send activation email (with user number info)
            email_sent = send_activation_email(request, user.email, code, user=user)
            
            if email_sent:
                # Mark email as sent in database
                act.email_sent = True
                act.email_sent_at = timezone.now()
                act.save()
                
                messages.success(
                    request, _('You are signed up. To activate the account, follow the link sent to the mail.'))
            else:
                # Email failed to send, delete user and activation to allow re-registration
                act.delete()
                user.delete()
                # Also delete the EmailAddressState
                EmailAddressState.objects.filter(user=user).delete()
                
                messages.error(
                    request, _('Failed to send activation email. Please try again or contact support.'))
                return redirect('accounts:sign_up')
        else:
            raw_password = form.cleaned_data['password1']

            user = authenticate(username=user.username, password=raw_password)
            login(request, user)

            messages.success(request, _('You are successfully signed up!'))

        return redirect('index')


class ActivateView(View):
    @staticmethod
    def get(request, code):
        act = get_object_or_404(Activation, code=code)

        # Activate profile
        user = act.user
        user.is_active = True
        user.save()

        # Confirm email in EmailAddressState
        try:
            email_state = EmailAddressState.objects.get(user=user)
            email_state.is_confirmed = True
            email_state.save()
        except EmailAddressState.DoesNotExist:
            pass

        # Remove the activation record
        act.delete()

        # Grant lifetime premium to early users (first N registrations)
        grant_early_premium(user)

        messages.success(request, _('You have successfully activated your account!'))

        return redirect('accounts:log_in')


class ResendActivationCodeView(GuestOnlyView, FormView):
    template_name = 'accounts/resend_activation_code.html'

    @staticmethod
    def get_form_class(**kwargs):
        if settings.DISABLE_USERNAME:
            return ResendActivationCodeViaEmailForm

        return ResendActivationCodeForm

    def form_valid(self, form):
        user = form.user_cache

        activation = user.activation_set.first()
        activation.delete()

        code = get_random_string(20)

        act = Activation()
        act.code = code
        act.user = user
        act.save()

        # Try to send activation email
        email_sent = send_activation_email(self.request, user.email, code)
        
        if email_sent:
            # Mark email as sent in database
            act.email_sent = True
            act.email_sent_at = timezone.now()
            act.save()
            
            messages.success(self.request, _('A new activation code has been sent to your email address.'))
        else:
            # Email failed to send, delete activation to allow retry
            act.delete()
            messages.error(self.request, _('Failed to send activation email. Please try again or contact support.'))

        return redirect('accounts:resend_activation_code')


class RestorePasswordView(GuestOnlyView, FormView):
    template_name = 'accounts/restore_password.html'

    @staticmethod
    def get_form_class(**kwargs):
        if settings.RESTORE_PASSWORD_VIA_EMAIL_OR_USERNAME:
            return RestorePasswordViaEmailOrUsernameForm

        return RestorePasswordForm

    def form_valid(self, form):
        user = form.user_cache
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        if isinstance(uid, bytes):
            uid = uid.decode()

        send_reset_password_email(self.request, user.email, token, uid)

        return redirect('accounts:restore_password_done')


class RemindUsernameView(GuestOnlyView, FormView):
    template_name = 'accounts/remind_username.html'
    form_class = RemindUsernameForm

    def form_valid(self, form):
        user = form.user_cache
        send_forgotten_username_email(user.email, user.username)

        messages.success(self.request, _('Your username has been successfully sent to your email.'))

        return redirect('accounts:remind_username')


class RestorePasswordConfirmView(BasePasswordResetConfirmView):
    template_name = 'accounts/restore_password_confirm.html'

    def form_valid(self, form):
        # Change the password
        form.save()

        messages.success(self.request, _('Your password has been set. You may go ahead and log in now.'))

        return redirect('accounts:log_in')


class RestorePasswordDoneView(BasePasswordResetDoneView):
    template_name = 'accounts/restore_password_done.html'


class LogOutConfirmView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/log_out_confirm.html'


class LogOutView(LoginRequiredMixin, BaseLogoutView):
    template_name = 'accounts/log_out.html'


def check_username(request):
    username = request.GET.get('username', '').strip().lower()
    taken = False
    reason = None
    if not username:
        taken = True
        reason = 'empty'
    elif re.search(r'\s', username):
        taken = True
        reason = 'whitespace'
    elif User.objects.filter(username=username).exists():
        taken = True
        reason = 'taken'
    return JsonResponse({'taken': taken, 'reason': reason, 'username': username})


class ChangeProfileView(LoginRequiredMixin, FormView):
    template_name = 'accounts/profile/change_profile.html'
    form_class = CombinedProfileForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        from accounts.models import Profile
        profile, created = Profile.objects.get_or_create(user=user)
        initial['profile_picture'] = profile.profile_picture
        initial['username'] = user.username
        # Ensure EmailAddressState exists for this user
        from .models import EmailAddressState
        if not hasattr(user, 'email_state'):
            EmailAddressState.objects.create(user=user, email=user.email, is_confirmed=True)
        # If there is a pending email change, use the pending email in the form
        email_state = user.email_state
        if not email_state.is_confirmed:
            initial['email'] = email_state.email
        else:
            initial['email'] = user.email
        initial['user_id'] = user.id
        return initial

    def get_template_names(self):
        if self.request.GET.get('modal') == '1':
            return ['accounts/profile/change_profile_form.html']
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal'] = self.request.GET.get('modal') == '1'
        return context

    def form_valid(self, form):
        user = self.request.user
        from accounts.models import Profile
        profile, created = Profile.objects.get_or_create(user=user)
        # Username
        user.username = form.cleaned_data['username']
        # Email
        new_email = form.cleaned_data['email']
        if new_email != user.email:
            # Check if new email is already in use in EmailAddressState or User
            print("Checking for existing email in auth_user:", User.objects.filter(email__iexact=new_email).exclude(pk=user.pk).exists())
            from .models import EmailAddressState, EmailChangeAttempt
            if EmailAddressState.objects.filter(email__iexact=new_email).exclude(user=user).exists() or \
               User.objects.filter(email__iexact=new_email).exclude(pk=user.pk).exists():
                # Log the attempt
                EmailChangeAttempt.objects.create(user=user, email=new_email)
                messages.error(self.request, _('This email address is already in use by another account.'))
                return self.form_invalid(form)
            # Rate limit: max 3 attempts per 15 minutes
            recent_attempts = EmailChangeAttempt.objects.filter(user=user, attempted_at__gte=timezone.now()-timedelta(minutes=15)).count()
            if recent_attempts >= 3:
                messages.error(self.request, _('You have reached the maximum number of email change attempts. Please try again later.'))
                return self.form_invalid(form)
            # Log this attempt
            EmailChangeAttempt.objects.create(user=user, email=new_email)
            if getattr(settings, 'ENABLE_ACTIVATION_AFTER_EMAIL_CHANGE', False):
                code = get_random_string(20)
                act = Activation()
                act.code = code
                act.user = user
                act.email = new_email
                act.save()
                # Update or create EmailAddressState for new email, store old_email for rollback
                EmailAddressState.objects.update_or_create(
                    user=user,
                    defaults={'email': new_email, 'is_confirmed': False, 'old_email': user.email}
                )
                # Try to send activation email
                email_sent = send_activation_change_email(self.request, new_email, code)
                
                if email_sent:
                    # Mark email as sent in database
                    act.email_sent = True
                    act.email_sent_at = timezone.now()
                    act.save()
                    
                    messages.success(self.request, _('To complete the change of email address, click on the link sent to it.'))
                else:
                    # Email failed to send, rollback changes
                    act.delete()
                    EmailAddressState.objects.filter(user=user).delete()
                    
                    messages.error(self.request, _('Failed to send activation email. Please try again or contact support.'))
            else:
                # Immediate change (should not happen if activation is required)
                user.email = new_email
                user.save()
                EmailAddressState.objects.update_or_create(user=user, defaults={'email': new_email, 'is_confirmed': True, 'old_email': None})
                messages.success(self.request, _('Email successfully changed.'))
        else:
            user.save()
        # Social media fields
        profile.facebook_url = form.cleaned_data.get('facebook_url', '')
        profile.instagram_handle = form.cleaned_data.get('instagram_handle', '')
        profile.twitter_handle = form.cleaned_data.get('twitter_handle', '')
        profile.mastodon_handle = form.cleaned_data.get('mastodon_handle', '')
        profile.tiktok_handle = form.cleaned_data.get('tiktok_handle', '')
        # Notification preferences
        prefs, _created = NotificationPreference.objects.get_or_create(user=user)
        prefs.stone_scanned = form.cleaned_data.get('notify_stone_scanned', True)
        prefs.stone_moved = form.cleaned_data.get('notify_stone_moved', True)
        prefs.weekly_digest = form.cleaned_data.get('notify_weekly_digest', False)
        prefs.save()
        # Profile picture
        if self.request.POST.get('profile_picture-clear') == 'on':
            profile.profile_picture = None
        elif self.request.FILES.get('profile_picture'):
            uploaded = self.request.FILES['profile_picture']
            # Server-side image resize to max 800x800
            try:
                from PIL import Image
                from io import BytesIO
                from django.core.files.uploadedfile import InMemoryUploadedFile
                img = Image.open(uploaded)
                max_dim = 800
                if img.width > max_dim or img.height > max_dim:
                    img.thumbnail((max_dim, max_dim), Image.LANCZOS)
                    buf = BytesIO()
                    fmt = 'JPEG' if img.mode == 'RGB' else 'PNG'
                    if img.mode == 'RGBA':
                        fmt = 'PNG'
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                        fmt = 'JPEG'
                    img.save(buf, format=fmt, quality=85)
                    buf.seek(0)
                    ext = 'jpg' if fmt == 'JPEG' else 'png'
                    name = uploaded.name.rsplit('.', 1)[0] + '.' + ext
                    content_type = 'image/jpeg' if fmt == 'JPEG' else 'image/png'
                    uploaded = InMemoryUploadedFile(buf, 'profile_picture', name, content_type, buf.getbuffer().nbytes, None)
            except Exception:
                pass  # If resize fails, use original
            profile.profile_picture = uploaded
        profile.save()
        # Password
        password1 = form.cleaned_data.get('password1')
        if password1:
            user.set_password(password1)
            user.save()
            login(self.request, user)
            messages.success(self.request, _('Your password was changed.'))
        if not (new_email != user.email and getattr(settings, 'ENABLE_ACTIVATION_AFTER_EMAIL_CHANGE', False)):
            messages.success(self.request, _('Profile data has been successfully updated.'))
        return self.form_valid_redirect()

    def form_valid_redirect(self):
        from django.shortcuts import redirect
        return redirect('accounts:change_profile')

class ChangeEmailActivateView(View):
    @staticmethod
    def get(request, code):
        act = get_object_or_404(Activation, code=code)
        # Change the email
        user = act.user
        # Confirm new email in EmailAddressState and update user model
        from .models import EmailAddressState
        try:
            email_state = EmailAddressState.objects.get(user=user)
            user.email = email_state.email
            user.save()
            email_state.is_confirmed = True
            email_state.old_email = None
            email_state.save()
        except EmailAddressState.DoesNotExist:
            pass
        # Remove the activation record
        act.delete()
        messages.success(request, _('You have successfully changed your email!'))
        from django.shortcuts import redirect
        return redirect('accounts:change_profile')


class ResendEmailActivationView(View):
    @method_decorator(login_required)
    def post(self, request):
        user = request.user
        from .models import EmailAddressState, Activation
        email_state = getattr(user, 'email_state', None)
        if not email_state or email_state.is_confirmed:
            messages.error(request, _('No pending email confirmation to resend.'))
            return redirect('accounts:change_profile')
        # Find or create activation
        act = Activation.objects.filter(user=user, email=email_state.email).first()
        if not act:
            from django.utils.crypto import get_random_string
            code = get_random_string(20)
            act = Activation.objects.create(user=user, email=email_state.email, code=code)
        
        # Try to send activation email
        email_sent = send_activation_change_email(request, email_state.email, act.code)
        
        if email_sent:
            # Mark email as sent in database
            act.email_sent = True
            act.email_sent_at = timezone.now()
            act.save()
            
            messages.success(request, _('A new activation link has been sent to your email address.'))
        else:
            # Email failed to send, delete activation to allow retry
            act.delete()
            messages.error(request, _('Failed to send activation email. Please try again or contact support.'))
            
        return redirect('accounts:change_profile')


class CancelEmailChangeView(View):
    @method_decorator(login_required)
    def post(self, request):
        user = request.user
        from .models import EmailAddressState
        email_state = getattr(user, 'email_state', None)
        if email_state and not email_state.is_confirmed and email_state.old_email:
            # Rollback to old email
            email_state.email = email_state.old_email
            email_state.is_confirmed = True
            user.email = email_state.old_email
            user.save()
            email_state.old_email = None
            email_state.save()
            messages.success(request, _('Email change cancelled and reverted.'))
        else:
            messages.error(request, _('No pending email change to cancel.'))
        from django.shortcuts import redirect
        return redirect('accounts:change_profile')


class DiscourseSSOView(View):
    """
    Handle Discourse SSO (DiscourseConnect) authentication.

    When a user tries to access Discourse, Discourse redirects them here with
    a signed payload. If the user is logged in, we return their user data.
    If not, we redirect them to log in first.
    """

    def get(self, request):
        from .discourse_sso import (
            validate_discourse_payload,
            parse_discourse_payload,
            generate_discourse_payload,
        )

        # Check if Discourse SSO is enabled
        if not getattr(settings, 'DISCOURSE_SSO_ENABLED', False):
            return HttpResponseBadRequest('Discourse SSO is not enabled')

        discourse_url = getattr(settings, 'DISCOURSE_URL', '')
        sso_secret = getattr(settings, 'DISCOURSE_SSO_SECRET', '')

        if not discourse_url or not sso_secret:
            return HttpResponseBadRequest('Discourse SSO is not configured')

        # Get SSO params - either from query string or from session (after login redirect)
        sso = request.GET.get('sso') or request.session.get('discourse_sso')
        sig = request.GET.get('sig') or request.session.get('discourse_sig')

        if not sso or not sig:
            return HttpResponseBadRequest('Missing SSO parameters')

        # Validate the payload signature
        if not validate_discourse_payload(sso, sig, sso_secret):
            return HttpResponseBadRequest('Invalid SSO signature')

        # Check if user is logged in
        if not request.user.is_authenticated:
            # Store SSO params in session and redirect to login
            request.session['discourse_sso'] = sso
            request.session['discourse_sig'] = sig
            login_url = reverse('accounts:log_in')
            next_url = reverse('accounts:discourse_sso')
            return redirect(f'{login_url}?next={next_url}')

        # User is logged in - generate response payload
        try:
            nonce = parse_discourse_payload(sso)
        except ValueError as e:
            return HttpResponseBadRequest(f'Invalid payload: {e}')

        # Clear session SSO params
        request.session.pop('discourse_sso', None)
        request.session.pop('discourse_sig', None)

        # Generate signed payload with user data
        response_payload = generate_discourse_payload(
            request.user, nonce, sso_secret, request
        )

        # Redirect back to Discourse
        return redirect(f'{discourse_url}/session/sso_login?{response_payload}')


class TermsView(View):
    template_name = 'accounts/terms.html'

    def get(self, request):
        from django.shortcuts import render
        needs_acceptance = (
            request.user.is_authenticated
            and not hasattr(request.user, 'terms_acceptance')
        )
        return render(request, self.template_name, {
            'needs_acceptance': needs_acceptance,
            'next': request.GET.get('next', ''),
        })

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('accounts:log_in')
        if not hasattr(request.user, 'terms_acceptance'):
            TermsAcceptance.objects.create(user=request.user)
            messages.success(request, _('Thank you for accepting the Terms of Use.'))
        next_url = request.POST.get('next', '')
        if next_url and is_safe_url(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect('stonewalker_start')
