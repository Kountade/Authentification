from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from authentification import settings
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from .token import generatorToken

# Create your views here.


def home(request, *args, **kwargs):
    return render(request, 'app/index.html')


def register(request):
    if request.method == "POST":
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['password']
        passsword1 = request.POST['passsword1']
        if User.objects.filter(username=username):
            messages.error(request,"Ce nom est deja attribué")
            return redirect('register')
        if User.objects.filter(email=email):
            messages.error(request,"ce mail a deja un autre compte")
            return redirect('register')
        if not username.isalnum():
            messages.error(request,"Le nom doit etre en alphanumeric")
            return redirect("register")
        
        if password != passsword1:
            messages.error(request,"Les deux mots de pass ne corespond pas")
            return redirect('register')
            
            
        mon_utilisateur = User.objects.create_user(username, email, password)
        mon_utilisateur.first_name =firstname
        mon_utilisateur.last_name = lastname
        mon_utilisateur.is_active = False
        mon_utilisateur.save()
        messages.success(request, 'VOTRE COMPTE A ETE BIEN CREE')
        # mail de bienvenue
        subject = "Bienvenu sur mon system d'autentification"
        message = "Bienvenu" + mon_utilisateur.first_name + "" + mon_utilisateur.last_name + "\n Nous sommes heureux de votre confiance\n\n Merci" 
        from_email = settings.EMAIL_HOST_USER
        to_list = [mon_utilisateur.email]
        send_mail(subject,message, from_email,to_list, fail_silently=False)
    # mail de confirmation 
        current_site = get_current_site(request)
        email_subject = "Confirmation de votre addresse  mail sur kounta"
        messageConfirm = render_to_string("emailconfirm.html", {
            "name": mon_utilisateur.first_name,
            "domain": current_site.domain,
            "uid":urlsafe_base64_encode(force_bytes(mon_utilisateur.pk)),
            "token": generatorToken.make_token(mon_utilisateur)
        })
        
        email = EmailMessage(
            email_subject,
            messageConfirm,
            settings.EMAIL_HOST_USER,
            [mon_utilisateur.email]
        )
        
        email.fail_silently = False
        email.send()
        
        return redirect('login')
    return render(request, 'app/register.html')    


def logIn(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        my_user = User.objects.get(username=username)
        
        if user is not None:
            login(request,user)
            firstname = user.first_name
            return render(request, 'app/index.html', {"firstname":firstname})
        elif my_user.is_active == False:
            messages.error(request,"vous n'avez pas confirmer votre addresse. veiilez vérifier votre mail et le confrimer .Merci !")
        
        else:
            messages.error(request, 'Maivaise authentification')
            return redirect('login') 

    return render(request, 'app/login.html')    

def logOut(request):
    logout(request)
    messages.success(request, 'Vous ete bien deconnecter')
    return redirect('home')
    
def activate(request, uidb64, token):
    try:
        uid  = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError,User.DoesNotExist):
        user = None
    if user is not None and generatorToken.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request,"Felications ! votre compte a birn été active maintement vous pouvez vous connecter")
        return redirect('login')
    else:
        messages.error(request,"echéc de l'activation!!!!")
        return redirect('home')
        
        
   