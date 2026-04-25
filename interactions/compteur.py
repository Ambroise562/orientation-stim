# ton_app/context_processors.py

def notifications_count(request):
    if request.user.is_authenticated:
        # On compte les notifications non lues une seule fois ici
        count = request.user.notifications.filter(est_lu=False , est_archivee=False).count()
        return {'unread_notifications_count': count}
    return {'unread_notifications_count': 0}