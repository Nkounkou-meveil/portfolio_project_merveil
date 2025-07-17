# portfolio/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
import json
import logging

from .models import (
    Profile, Project, Skill, News, Partner, 
    SocialGallery, Feed, Newsletter, ContactMessage,
    SocialLink, ContactInfo, SiteSettings
)

logger = logging.getLogger(__name__)


def index(request):
    """Vue principale du portfolio"""
    try:
        # Récupération du profil principal
        profile = Profile.objects.first()
        
        # Récupération des données pour chaque section
        context = {
            'profile': profile,
            'projects': Project.objects.filter(featured=True).order_by('ordre_affichage')[:6],
            'skills': Skill.objects.all().order_by('ordre_affichage'),
            'news': News.objects.all().order_by('ordre_affichage', '-date_publication')[:6],
            'partners': Partner.objects.filter(actif=True).order_by('ordre_affichage'),
            'gallery': SocialGallery.objects.all().order_by('ordre_affichage')[:6],
            'feed': Feed.objects.all().order_by('ordre_affichage')[:8],
            'social_links': SocialLink.objects.filter(actif=True).order_by('ordre_affichage'),
            'contact_info': ContactInfo.objects.first(),
            'site_settings': SiteSettings.objects.first(),
        }
        
        return render(request, 'portfolio/index.html', context)
        
    except Exception as e:
        logger.error(f"Erreur dans la vue index: {str(e)}")
        # En cas d'erreur, on renvoie un contexte minimal
        context = {
            'profile': None,
            'projects': [],
            'skills': [],
            'news': [],
            'partners': [],
            'gallery': [],
            'feed': [],
        }
        return render(request, 'portfolio/index.html', context)


def projet_detail(request, slug):
    """Vue détaillée d'un projet"""
    projet = get_object_or_404(Project, slug=slug)
    
    # Projets similaires (même statut ou technologies communes)
    projets_similaires = Project.objects.filter(
        featured=True
    ).exclude(id=projet.id).order_by('ordre_affichage')[:3]
    
    context = {
        'projet': projet,
        'projets_similaires': projets_similaires,
        'profile': Profile.objects.first(),
    }
    
    return render(request, 'portfolio/projet_detail.html', context)


def galerie_detail(request, slug):
    """Vue détaillée d'un élément de la galerie sociale"""
    galerie_item = get_object_or_404(SocialGallery, slug=slug)
    
    # Éléments similaires de la galerie
    galerie_similaire = SocialGallery.objects.exclude(
        id=galerie_item.id
    ).order_by('ordre_affichage')[:3]
    
    context = {
        'galerie_item': galerie_item,
        'galerie_similaire': galerie_similaire,
        'profile': Profile.objects.first(),
    }
    
    return render(request, 'portfolio/galerie_detail.html', context)


def tous_projets(request):
    """Vue listant tous les projets avec pagination"""
    projets_list = Project.objects.all().order_by('ordre_affichage', '-created_at')
    
    # Pagination
    paginator = Paginator(projets_list, 9)  # 9 projets par page
    page_number = request.GET.get('page')
    projets = paginator.get_page(page_number)
    
    context = {
        'projets': projets,
        'profile': Profile.objects.first(),
    }
    
    return render(request, 'portfolio/tous_projets.html', context)


def toute_galerie(request):
    """Vue listant toute la galerie sociale avec pagination"""
    galerie_list = SocialGallery.objects.all().order_by('ordre_affichage', '-created_at')
    
    # Pagination
    paginator = Paginator(galerie_list, 12)  # 12 éléments par page
    page_number = request.GET.get('page')
    galerie = paginator.get_page(page_number)
    
    context = {
        'galerie': galerie,
        'profile': Profile.objects.first(),
    }
    
    return render(request, 'portfolio/toute_galerie.html', context)


@require_http_methods(["POST"])
def newsletter_subscribe(request):
    """Vue AJAX pour l'inscription à la newsletter"""
    try:
        # Vérification du Content-Type
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
        else:
            email = request.POST.get('email', '').strip().lower()
        
        # Validation de l'email
        if not email:
            return JsonResponse({
                'success': False, 
                'message': 'L\'adresse email est requise.'
            })
        
        # Validation format email basique
        if '@' not in email or '.' not in email.split('@')[1]:
            return JsonResponse({
                'success': False, 
                'message': 'Format d\'email invalide.'
            })
        
        # Vérification si l'email existe déjà
        newsletter, created = Newsletter.objects.get_or_create(
            email=email,
            defaults={'actif': True}
        )
        
        if created:
            # Nouvel abonnement
            logger.info(f"Nouvel abonnement newsletter: {email}")
            
            # Optionnel : Envoyer un email de confirmation
            try:
                send_mail(
                    subject='Bienvenue dans la newsletter !',
                    message=f'Merci de vous être abonné à ma newsletter. Vous recevrez régulièrement mes dernières actualités.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True
                )
            except Exception as e:
                logger.warning(f"Erreur envoi email confirmation: {str(e)}")
            
            return JsonResponse({
                'success': True, 
                'message': 'Inscription réussie ! Merci pour votre abonnement.'
            })
        else:
            # Email déjà existant
            if newsletter.actif:
                return JsonResponse({
                    'success': False, 
                    'message': 'Cette adresse email est déjà inscrite à la newsletter.'
                })
            else:
                # Réactiver l'abonnement
                newsletter.actif = True
                newsletter.save()
                logger.info(f"Réactivation abonnement newsletter: {email}")
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Votre abonnement a été réactivé avec succès !'
                })
                
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False, 
            'message': 'Données JSON invalides.'
        })
    except Exception as e:
        logger.error(f"Erreur newsletter subscription: {str(e)}")
        return JsonResponse({
            'success': False, 
            'message': 'Une erreur est survenue. Veuillez réessayer plus tard.'
        })


@require_http_methods(["POST"])
def contact_message(request):
    """Vue AJAX pour l'envoi de messages de contact"""
    try:
        # Vérification du Content-Type
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        # Récupération des données
        nom = data.get('nom', '').strip()
        email = data.get('email', '').strip().lower()
        sujet = data.get('sujet', '').strip()
        message = data.get('message', '').strip()
        
        # Validations
        if not all([nom, email, sujet, message]):
            return JsonResponse({
                'success': False, 
                'message': 'Tous les champs sont requis.'
            })
        
        # Validation format email
        if '@' not in email or '.' not in email.split('@')[1]:
            return JsonResponse({
                'success': False, 
                'message': 'Format d\'email invalide.'
            })
        
        # Limitation longueur
        if len(message) > 2000:
            return JsonResponse({
                'success': False, 
                'message': 'Le message ne peut pas dépasser 2000 caractères.'
            })
        
        # Sauvegarde en base
        contact_msg = ContactMessage.objects.create(
            nom=nom,
            email=email,
            sujet=sujet,
            message=message
        )
        
        logger.info(f"Nouveau message de contact: {nom} ({email})")
        
        # Optionnel : Envoyer notification par email
        try:
            send_mail(
                subject=f'Nouveau message de contact: {sujet}',
                message=f'''
Nouveau message reçu sur le portfolio:

Nom: {nom}
Email: {email}
Sujet: {sujet}

Message:
{message}
                ''',
                from_email=email,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=True
            )
        except Exception as e:
            logger.warning(f"Erreur envoi notification contact: {str(e)}")
        
        return JsonResponse({
            'success': True, 
            'message': 'Votre message a été envoyé avec succès ! Je vous répondrai dans les plus brefs délais.'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False, 
            'message': 'Données JSON invalides.'
        })
    except Exception as e:
        logger.error(f"Erreur contact message: {str(e)}")
        return JsonResponse({
            'success': False, 
            'message': 'Une erreur est survenue. Veuillez réessayer plus tard.'
        })


def newsletter_unsubscribe(request, token):
    """Vue pour le désabonnement de la newsletter"""
    try:
        newsletter = get_object_or_404(Newsletter, token_desabonnement=token)
        
        if request.method == 'POST':
            newsletter.actif = False
            newsletter.save()
            
            logger.info(f"Désabonnement newsletter: {newsletter.email}")
            
            messages.success(request, 'Vous avez été désabonné avec succès de la newsletter.')
            return render(request, 'portfolio/newsletter_unsubscribe_success.html')
        
        context = {
            'newsletter': newsletter,
            'profile': Profile.objects.first(),
        }
        
        return render(request, 'portfolio/newsletter_unsubscribe.html', context)
        
    except Exception as e:
        logger.error(f"Erreur désabonnement newsletter: {str(e)}")
        messages.error(request, 'Lien de désabonnement invalide.')
        return render(request, 'portfolio/newsletter_unsubscribe_error.html')


def search(request):
    """Vue de recherche globale"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return render(request, 'portfolio/search_results.html', {
            'query': '',
            'projets': [],
            'galerie': [],
            'news': [],
            'profile': Profile.objects.first(),
        })
    
    # Recherche dans les projets
    projets = Project.objects.filter(
        titre__icontains=query
    ).order_by('ordre_affichage')[:6]
    
    # Recherche dans la galerie
    galerie = SocialGallery.objects.filter(
        titre__icontains=query
    ).order_by('ordre_affichage')[:6]
    
    # Recherche dans les actualités
    news = News.objects.filter(
        titre__icontains=query
    ).order_by('ordre_affichage', '-date_publication')[:6]
    
    context = {
        'query': query,
        'projets': projets,
        'galerie': galerie,
        'news': news,
        'profile': Profile.objects.first(),
        'total_results': len(projets) + len(galerie) + len(news),
    }
    
    return render(request, 'portfolio/search_results.html', context)


def api_projects(request):
    """API JSON pour récupérer les projets (pour AJAX)"""
    try:
        projects = Project.objects.filter(featured=True).order_by('ordre_affichage')
        
        projects_data = []
        for project in projects:
            projects_data.append({
                'id': project.id,
                'titre': project.titre,
                'description_courte': project.description_courte,
                'image': project.image.url if project.image else None,
                'statut': project.get_statut_display(),
                'status_color': project.status_color,
                'technologies': project.technologies,
                'url': project.get_absolute_url(),
                'url_demo': project.url_demo,
                'url_github': project.url_github,
            })
        
        return JsonResponse({
            'success': True,
            'projects': projects_data
        })
        
    except Exception as e:
        logger.error(f"Erreur API projects: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Erreur lors du chargement des projets.'
        })


def api_gallery(request):
    """API JSON pour récupérer la galerie (pour AJAX)"""
    try:
        gallery = SocialGallery.objects.all().order_by('ordre_affichage')
        
        gallery_data = []
        for item in gallery:
            gallery_data.append({
                'id': item.id,
                'titre': item.titre,
                'description_courte': item.description_courte,
                'image': item.image.url if item.image else None,
                'url': item.get_absolute_url(),
            })
        
        return JsonResponse({
            'success': True,
            'gallery': gallery_data
        })
        
    except Exception as e:
        logger.error(f"Erreur API gallery: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Erreur lors du chargement de la galerie.'
        })


def api_feed(request):
    """API JSON pour récupérer le feed (pour AJAX)"""
    try:
        feed = Feed.objects.all().order_by('ordre_affichage')
        
        feed_data = []
        for item in feed:
            feed_data.append({
                'id': item.id,
                'image': item.image.url if item.image else None,
                'alt_text': item.alt_text,
            })
        
        return JsonResponse({
            'success': True,
            'feed': feed_data
        })
        
    except Exception as e:
        logger.error(f"Erreur API feed: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Erreur lors du chargement du feed.'
        })


def handler404(request, exception):
    """Vue personnalisée pour les erreurs 404"""
    context = {
        'profile': Profile.objects.first(),
    }
    return render(request, 'portfolio/404.html', context, status=404)


def handler500(request):
    """Vue personnalisée pour les erreurs 500"""
    context = {
        'profile': Profile.objects.first(),
    }
    return render(request, 'portfolio/500.html', context, status=500)