from django.contrib import admin
from .models import *
from django import forms
# from django.contrib.auth.models import Permission
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse_lazy

# from django.contrib.admin import AdminSite
from .models import Article


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'groups')

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password")
        if password and password2 and password != password:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'groups', 'status', 'is_staff', 'is_superuser')

    def init(self, *args, **kwargs):
        super().init(*args, **kwargs)
        self.fields['password'].help_text = (
                                                "Raw passwords are not stored, so there is no way to see "
                                                "this user's password, but you can <a href=\"%s\"> "
                                                "<strong>Change the Password</strong> using this form</a>."
                                            ) % reverse_lazy('admin:auth_user_password_change', args=[self.instance.id])

    def clean_password(self):
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('id', 'username', 'status', 'is_staff', 'is_superuser')
    list_filter = ('groups', 'is_staff', 'is_superuser',)
    search_fields = ('username', 'stir', 'first_name', 'sur_name', 'mid_name', 'full_name',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'first_name', 'sur_name', 'mid_name',
                      'phone', 'per_adr', 'company', 'status', 'password')}),
        ('Personal info', {'fields': ('groups',)}),
        ('Permissions', {'fields': ('is_superuser','is_staff')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'mid_name',
                      'phone',
                        'groups', 'status', 'password', 'is_staff'),
        }),
    )
    list_display_links = ('username',)
    ordering = ('username',)
    filter_horizontal = ('user_permissions',)


class PermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'content_type', 'codename')

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return False

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'tour_title',)
    list_display_links = ('id', 'tour_title',)

admin.site.register(User, UserAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Customer)
admin.site.register(Order)

