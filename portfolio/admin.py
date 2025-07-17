# portfolio/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Profile, Project, Skill, News, Partner, 
    SocialGallery, Feed, Newsletter, ContactMessage,
    SocialLink, ContactInfo, SiteSettings
)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['nom_complet', 'pseudo', 'titre_professionnel', 'photo_preview']
    list_editable = ['titre_professionnel']
    search_fields = ['nom', 'prenom', 'pseudo']
    readonly_fields = ['created_at', 'updated_at', 'photo_preview']
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'pseudo', 'titre_professionnel')
        }),
        ('Contenu', {
            'fields': ('bio', 'photo_profil', 'photo_preview')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def photo_preview(self, obj):
        if obj.photo_profil:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 50%;" />',
                obj.photo_profil.url
            )
        return "Aucune image"
    photo_preview.short_description = "Aperçu"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['titre', 'statut', 'featured', 'ordre_affichage', 'image_preview', 'created_at']
    list_filter = ['statut', 'featured', 'created_at']
    list_editable = ['statut', 'featured', 'ordre_affichage']
    search_fields = ['titre', 'description_courte']
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    prepopulated_fields = {'slug': ('titre',)}
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('titre', 'slug', 'statut', 'featured', 'ordre_affichage')
        }),
        ('Contenu', {
            'fields': ('description_courte', 'description_detaillee', 'image', 'image_preview')
        }),
        ('Technologies et liens', {
            'fields': ('technologies', 'url_demo', 'url_github')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 150px; height: 100px; object-fit: cover;" />',
                obj.image.url
            )
        return "Aucune image"
    image_preview.short_description = "Aperçu"
    
    actions = ['marquer_featured', 'retirer_featured']
    
    def marquer_featured(self, request, queryset):
        queryset.update(featured=True)
        self.message_user(request, f"{queryset.count()} projets marqués comme mis en avant.")
    marquer_featured.short_description = "Marquer comme mis en avant"
    
    def retirer_featured(self, request, queryset):
        queryset.update(featured=False)
        self.message_user(request, f"{queryset.count()} projets retirés des mis en avant.")
    retirer_featured.short_description = "Retirer des mis en avant"


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['nom_competence', 'icone_preview', 'ordre_affichage', 'created_at']
    list_editable = ['ordre_affichage']
    search_fields = ['nom_competence', 'description']
    ordering = ['ordre_affichage', 'nom_competence']
    
    def icone_preview(self, obj):
        return format_html(
            '<i class="{}" style="font-size: 20px; color: #e1306c;"></i>',
            obj.icone_class
        )
    icone_preview.short_description = "Icône"


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['titre', 'plateforme', 'plateforme_badge', 'ordre_affichage', 'date_publication']
    list_filter = ['plateforme', 'date_publication']
    list_editable = ['ordre_affichage']
    search_fields = ['titre', 'description']
    readonly_fields = ['date_publication', 'image_preview']
    ordering = ['ordre_affichage', '-date_publication']
    
    fieldsets = (
        ('Contenu', {
            'fields': ('titre', 'description', 'image', 'image_preview')
        }),
        ('Publication', {
            'fields': ('plateforme', 'lien_externe', 'ordre_affichage')
        }),
        ('Date', {
            'fields': ('date_publication',),
            'classes': ('collapse',)
        }),
    )
    
    def plateforme_badge(self, obj):
        color = obj.plateforme_color.replace('bg-', '')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 15px; font-size: 12px;">{}</span>',
            {'blue-600': '#2563eb', 'blue-700': '#1d4ed8', 'blue-400': '#60a5fa', 
             'pink-500': '#ec4899', 'gray-600': '#4b5563', 'red-600': '#dc2626'}.get(color, '#6b7280'),
            obj.get_plateforme_display()
        )
    plateforme_badge.short_description = "Plateforme"
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 150px; height: 100px; object-fit: cover;" />',
                obj.image.url
            )
        return "Aucune image"
    image_preview.short_description = "Aperçu"


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['nom_partenaire', 'logo_preview', 'actif', 'ordre_affichage', 'url_site']
    list_filter = ['actif', 'created_at']
    list_editable = ['actif', 'ordre_affichage']
    search_fields = ['nom_partenaire', 'description']
    readonly_fields = ['created_at', 'logo_preview']
    ordering = ['ordre_affichage', 'nom_partenaire']
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="width: 80px; height: 80px; object-fit: contain;" />',
                obj.logo.url
            )
        return "Aucun logo"
    logo_preview.short_description = "Logo"


@admin.register(SocialGallery)
class SocialGalleryAdmin(admin.ModelAdmin):
    list_display = ['titre', 'image_preview', 'ordre_affichage', 'created_at']
    list_editable = ['ordre_affichage']
    search_fields = ['titre', 'description_courte']
    readonly_fields = ['created_at', 'image_preview']
    prepopulated_fields = {'slug': ('titre',)}
    ordering = ['ordre_affichage', '-created_at']
    
    fieldsets = (
        ('Contenu principal', {
            'fields': ('titre', 'slug', 'description_courte', 'ordre_affichage')
        }),
        ('Image et détails', {
            'fields': ('image', 'image_preview', 'contenu_detaille')
        }),
        ('Date', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; object-fit: cover;" />',
                obj.image.url
            )
        return "Aucune image"
    image_preview.short_description = "Aperçu"


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ['id', 'image_preview', 'alt_text', 'ordre_affichage', 'created_at']
    list_editable = ['ordre_affichage', 'alt_text']
    readonly_fields = ['created_at', 'image_preview']
    ordering = ['ordre_affichage', '-created_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; object-fit: cover;" />',
                obj.image.url
            )
        return "Aucune image"
    image_preview.short_description = "Aperçu"


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'actif', 'date_inscription']
    list_filter = ['actif', 'date_inscription']
    list_editable = ['actif']
    search_fields = ['email']
    readonly_fields = ['date_inscription', 'token_desabonnement']
    ordering = ['-date_inscription']
    
    actions = ['activer_emails', 'desactiver_emails']
    
    def activer_emails(self, request, queryset):
        queryset.update(actif=True)
        self.message_user(request, f"{queryset.count()} emails activés.")
    activer_emails.short_description = "Activer les emails sélectionnés"
    
    def desactiver_emails(self, request, queryset):
        queryset.update(actif=False)
        self.message_user(request, f"{queryset.count()} emails désactivés.")
    desactiver_emails.short_description = "Désactiver les emails sélectionnés"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['nom', 'email', 'sujet', 'lu', 'date_envoi']
    list_filter = ['lu', 'date_envoi']
    list_editable = ['lu']
    search_fields = ['nom', 'email', 'sujet', 'message']
    readonly_fields = ['date_envoi']
    ordering = ['-date_envoi']
    
    fieldsets = (
        ('Expéditeur', {
            'fields': ('nom', 'email')
        }),
        ('Message', {
            'fields': ('sujet', 'message', 'lu')
        }),
        ('Date', {
            'fields': ('date_envoi',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['marquer_lu', 'marquer_non_lu']
    
    def marquer_lu(self, request, queryset):
        queryset.update(lu=True)
        self.message_user(request, f"{queryset.count()} messages marqués comme lus.")
    marquer_lu.short_description = "Marquer comme lu"
    
    def marquer_non_lu(self, request, queryset):
        queryset.update(lu=False)
        self.message_user(request, f"{queryset.count()} messages marqués comme non lus.")
    marquer_non_lu.short_description = "Marquer comme non lu"


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ['plateforme', 'nom_affichage', 'icone_preview', 'actif', 'sidebar_contact', 'ordre_affichage']
    list_filter = ['plateforme', 'actif', 'sidebar_contact']
    list_editable = ['actif', 'sidebar_contact', 'ordre_affichage']
    search_fields = ['nom_affichage', 'url']
    ordering = ['ordre_affichage', 'plateforme']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('plateforme', 'url', 'nom_affichage')
        }),
        ('Affichage', {
            'fields': ('ordre_affichage', 'actif', 'sidebar_contact')
        }),
    )
    
    def icone_preview(self, obj):
        return format_html(
            '<i class="{} text-xl" style="color: {};"></i>',
            obj.icone_class,
            '#1f2937' if obj.plateforme in ['github'] else '#3b82f6'
        )
    icone_preview.short_description = "Icône"


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ['telephone', 'email', 'whatsapp', 'afficher_sidebar', 'updated_at']
    list_editable = ['afficher_sidebar']
    
    fieldsets = (
        ('Contact principal', {
            'fields': ('telephone', 'email', 'whatsapp')
        }),
        ('Adresse', {
            'fields': ('adresse',)
        }),
        ('Réseaux sociaux', {
            'fields': ('linkedin_url',)
        }),
        ('Affichage', {
            'fields': ('afficher_sidebar',)
        }),
    )
    
    def has_add_permission(self, request):
        # Permettre seulement un seul objet ContactInfo
        return not ContactInfo.objects.exists()


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['nom_site', 'description_site', 'logo_preview', 'favicon_preview', 'updated_at']
    readonly_fields = ['created_at', 'updated_at', 'logo_preview', 'favicon_preview']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom_site', 'description_site')
        }),
        ('Visuels', {
            'fields': ('logo', 'logo_preview', 'favicon', 'favicon_preview')
        }),
        ('Personnalisation', {
            'fields': ('couleur_primaire',)
        }),
        ('Analytics', {
            'fields': ('google_analytics',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="width: 100px; height: auto; object-fit: contain;" />',
                obj.logo.url
            )
        return "Aucun logo"
    logo_preview.short_description = "Aperçu du logo"
    
    def favicon_preview(self, obj):
        if obj.favicon:
            return format_html(
                '<img src="{}" style="width: 32px; height: 32px; object-fit: contain;" />',
                obj.favicon.url
            )
        return "Aucun favicon"
    favicon_preview.short_description = "Aperçu du favicon"
    

# Configuration générale de l'admin
admin.site.site_header = "Portfolio Admin"
admin.site.site_title = "Portfolio"
admin.site.index_title = "Administration du Portfolio"