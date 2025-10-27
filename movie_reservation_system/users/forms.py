"""
users/forms.py

Registration form for CustomUser model with email as username field.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model, authenticate
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

CustomUser = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """
    Form for registering new users with email, name, phone, and terms agreement.
    """
    
    # Phone validator (optional field, but if provided must be valid)
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address',
            'autocomplete': 'email',
        }),
        help_text='Required. Enter a valid email address.',
    )
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name',
            'autocomplete': 'given-name',
        }),
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name',
            'autocomplete': 'family-name',
        }),
    )
    
    phone = forms.CharField(
        max_length=17,
        required=False,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+380501234567',
            'autocomplete': 'tel',
        }),
        help_text='Optional. Format: +999999999',
    )
    
    password1 = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'new-password',
        }),
        help_text='Your password must contain at least 8 characters and cannot be entirely numeric.',
    )
    
    password2 = forms.CharField(
        label='Password confirmation',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'autocomplete': 'new-password',
        }),
        help_text='Enter the same password as before, for verification.',
    )
    
    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        label='I agree to the Terms and Conditions',
        error_messages={
            'required': 'You must agree to the terms and conditions.'
        },
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone', 'password1', 'password2', 'agree_terms']

    def clean_email(self):
        """
        Validate that the email is unique (case-insensitive).
        """
        email = self.cleaned_data.get('email')
        if email:
            # Normalize email to lowercase for case-insensitive comparison
            email = email.lower()
            
            # Check if user with this email already exists
            if CustomUser.objects.filter(email__iexact=email).exists():
                raise ValidationError('A user with that email already exists.')
        
        return email

    def clean_phone(self):
        """
        Clean and validate phone number if provided.
        """
        phone = self.cleaned_data.get('phone')
        
        # If phone is provided, remove spaces and validate format
        if phone:
            phone = phone.strip()
            # Additional cleaning if needed
            # e.g., remove spaces, dashes, etc.
            phone = phone.replace(' ', '').replace('-', '')
        
        return phone

    def save(self, commit=True):
        """
        Save the user instance with normalized email.
        """
        user = super().save(commit=False)
        
        # Normalize email to lowercase
        user.email = self.cleaned_data['email'].lower()
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        # Save phone if provided
        if self.cleaned_data.get('phone'):
            user.phone = self.cleaned_data['phone']
        
        if commit:
            user.save()
        
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address',
            'autocomplete': 'email',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        }),
        label="Password"
    )

    def __init__(self, *args, **kwargs):
        self.user = None
        self.request = kwargs.pop('request', None)  # Pop request from kwargs
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise forms.ValidationError("Invalid email or password.")
            if not user.is_active:
                raise forms.ValidationError("This account is inactive.")
            self.user = user

        return cleaned_data

    def get_user(self):
        """Returns the authenticated user if login was successful."""
        return self.user
