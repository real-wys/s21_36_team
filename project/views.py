import os

from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_safe, require_http_methods

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

#from django.contrib.auth.models import User
from .models import *
from django.utils import timezone

from project.forms import LoginForm, RegisterForm  #, ChatMessageForm   #ImageMessageForm
from django.db.models import Q
from django.db.models.functions import Lower
from io import BytesIO, StringIO
from django.core.files.base import ContentFile
from PIL import Image

import json

from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger

from notifications.signals import notify
from django.views import View
from django.views.generic import ListView
# from django.contrib.auth.mixins import LoginRequiredMixin


@login_required
def blog(request):
    obj_list = get_object_by_category(request,"blog")
    if "fault_category" in obj_list:
        return render(request,'blog.html',obj_list)
    context = getblog(request,obj_list,"blog")
    context['username']  = request.user.username
    context['firstname'] = request.user.first_name
    context['lastname']  = request.user.last_name
    return render(request,'blog.html',context)    #返回page_obj对象

def get_object_by_category(request, type):
    category = request.GET.get('c')
    if type == "blog":
        if category is None or category == "all":
            obj_list = Article.objects.all().order_by('-id')
        elif category not in category_list:
            context={}
            context['fault_category']="There is no category named "+category+". Please search it as keyword"
            return context
        else:
            obj_list = Article.objects.filter(tag__contains=category)

    else:
        if category is None or category == "all":
            obj_list = Question.objects.all().order_by('-id')
        elif category not in category_list:
            context={}
            context['fault_category']="There is no category named "+category+". Please search it as keyword"
            return context
        else:
            obj_list = Question.objects.filter(category=category)
    return obj_list


def getblog(request,obj_list,type):
    user = get_object_or_404(User, username=request.user.username)
    context={}
    if user.role == 0:
        context['is_lawyer'] = False
    else:
        context['is_lawyer'] = True
    res=[]
    for j in obj_list:
        j.tag=j.tag[1]
        entry={}
        entry['article'] = j
        if user.role == 0:
            entry['collect'] = checkCollect(j,user)
            entry['like'] = checkLike(j,user)
            entry['unlike'] = checkUnlike(j,user)
        else:
            entry['collect']=False
            entry['like']=False
            entry['unlike']=False
        res.append(entry)

    if type == "blog":
        current_page = request.GET.get('p')
        paginator = Paginator(res,5)
        try:
            page_obj = paginator.page(current_page)
        except EmptyPage as e:
            page_obj = paginator.page(1)
        except PageNotAnInteger as e:
            page_obj = paginator.page(1)

    context['page_obj']=page_obj
    return context

@login_required
def searchByTag(request):
    context={}
    context['username']  = request.user.username
    context['firstname'] = request.user.first_name
    context['lastname']  = request.user.last_name

    try:
        tag =  request.GET['tag']
    except:
        context['tag_not_found']="You must enter a tag!"
        return render(request,'categories.html', context)
    if not tag:
        context['tag_not_found']="You must enter a tag!"
        return render(request,'categories.html', context)

    if tag not in tag_list:
        context['fault_tag']="There is no tag named "+tag+". Please search it as keyword!"
        return render(request,'categories.html', context)


    context['tag'] = tag
    article = Article.objects.filter(tag__contains=tag)
    context['articles']=article

    #return Question
    q = Question.objects.filter(tag=tag)
    context['questions']=q
    return render(request, 'searchByTag.html', context)


def dislike(request, id, type):
    user = get_object_or_404(User, username=request.user.username)    
    userprofile = get_object_or_404(UserProfile, profile_user=user)
    
    if type == 0:
        # answer-related
        answer =  Answer.objects.get(id=id)

        if answer not in userprofile.unliked_answer.all():
            answer.dislike_count += 1
            userprofile.unliked_answer.add(answer)
        else:
            answer.dislike_count -= 1
            userprofile.unliked_answer.remove(answer)
        answer.save()
        return  redirect(reverse('questionPage',kwargs={'question_id':answer.related_question.id}))
    else: 
        # article-related
        article = Article.objects.get(id=id)
    
        if article not in userprofile.unliked_article.all():
            article.dislike_count += 1
            userprofile.unliked_article.add(article)
        else :
            article.dislike_count -= 1
            userprofile.unliked_article.remove(article)
        article.save()
        return  redirect(reverse('articlePage',kwargs={'article_id':article.id}))



def like(request, id, type):
    user = get_object_or_404(User, username=request.user.username)    
    userprofile = get_object_or_404(UserProfile, profile_user=user)
    
    if type == 0:
        #answer-related
        answer = Answer.objects.get(id=id)

        if answer not in userprofile.liked_answer.all():
            answer.like_count += 1
            answer.lawyer.lawyerprofile_owner.review_score += 1
            userprofile.liked_answer.add(answer)
        else:
            answer.like_count -= 1
            answer.lawyer.lawyerprofile_owner.review_score -= 1
            userprofile.liked_answer.remove(answer)
        answer.save()
        answer.lawyer.save()
        answer.lawyer.lawyerprofile_owner.save()
        return  redirect(reverse('questionPage',kwargs={'question_id':answer.related_question.id}))
    else:
        # article-related
        article = Article.objects.get(id=id)
    
        if article not in userprofile.liked_article.all():
            article.like_count += 1
            article.article_writer.review_score += 1
            userprofile.liked_article.add(article)
        else :
            article.like_count -= 1
            article.article_writer.review_score -= 1
            userprofile.liked_article.remove(article)
        article.save()
        article.article_writer.save()
        return  redirect(reverse('articlePage',kwargs={'article_id':article.id}))



def collect(request, id, type):
    user = get_object_or_404(User, username=request.user.username)    
    userprofile = get_object_or_404(UserProfile, profile_user=user)

    if type == 0:
        #question-related
        question = Question.objects.get(id=id)

        if question not in userprofile.collected_question.all():
            question.collect_count += 1
            userprofile.collected_question.add(question)
        else:
            question.collect_count -= 1
            userprofile.collected_question.remove(question)
        question.save()
        return  redirect(reverse('questionPage',kwargs={'question_id':question.id}))
    else:
        #article-related
        article = Article.objects.get(id=id)
    
        if article not in userprofile.collected_article.all():
            article.collect_count += 1
            userprofile.collected_article.add(article)
            article.article_writer.review_score += 1
            article.article_writer.save()
        else :
            article.collect_count -= 1
            userprofile.collected_article.remove(article)
            article.article_writer.review_score -= 1
        article.save()
        article.article_writer.save()
        return  redirect(reverse('articlePage',kwargs={'article_id':article.id}))




@login_required
def create_article(request):
    user = get_object_or_404(User, username=request.user.username)
    # if the user is a client, redirect to create questions
    if user.role == 0:
        return redirect(reverse(createQuestion))

    # if user has not built profile, return blog page
    try: writer =LawyerProfile.objects.get(profile_user=user)
    except:
        return redirect(reverse(blog))
    if request.method == 'GET' :
        return render(request, 'articleForm.html', {})
    res = request.POST
    if ('category'  or 'tag' or 'title'or 'abstract' or 'article') not in res or 'articleImage' not in request.FILES:
        context={}
        context['error']="Please do not change the variable name!"
        return render(request,"articleForm.html",context)

    tag = [res['category'],res['tag']]
    time = timezone.now()
    # add article to article Model
    article = Article.objects.create(title=res['title'],abstract=res['abstract'],text=res['article']
                                     ,article_creation_time=time,article_writer=writer,tag=tag
                                     ,like_count=0,dislike_count=0,collect_count=0)
    # cal reviewed_score
    writer.review_score = writer.review_score+3
    writer.save()

    p = request.FILES.get('articleImage')
    if p is not None:
        article.img =cropImg(p,0)
        article.big_img=cropImg(p,1)
    article.save()
    url = reverse('articlePage',kwargs={'article_id':article.id})
    return redirect(url)


@login_required
def delete_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    user = get_object_or_404(User, username=request.user.username)
    if article.article_writer.profile_user == user:
        article.delete()
    
    return redirect(reverse('blog'))


def cropImg(field,type):
    f = field.content_type.split('/')[1]
    img=Image.open(field)
    img_io = BytesIO()
    width, height = img.size
    if type == 0:
        if width > 1.5*height:
            im = img.crop((0,0,1.5*height,height))
        else:
            im=img.crop((0,0,width,width/1.5))
    else :
        if width > 3 * height:
            im = img.crop((0,0,3*height,height))
        else:
            im=img.crop((0,0,width,width/3))
    im.save(img_io, format=f, quality=100)
    img_content = ContentFile(img_io.getvalue(),field.name)
    return img_content


@login_required
def submit_comment(request, article_id):
    context = {}

    user = get_object_or_404(User, username=request.user.username)
    article = get_object_or_404(Article, id=article_id)
    context['article'] = article

    comment_text = request.POST.get('comment')
    new_comment = Comment(comment_input_text=comment_text,
                        user=user, related_article=article)
    new_comment.save()

    return redirect(reverse('articlePage', kwargs={'article_id':article.id}))






@login_required
def articlePage(request, article_id):
    context = {}
    user = get_object_or_404(User, username=request.user.username)
    article = get_object_or_404(Article, id=article_id)
    context['article'] = article

    if article.article_writer.profile_user.id == user.id:
        context['writer'] = 1
    else:
        context['writer'] = 0

    if user.role == 0:
        context['role'] = 0
        userprofile = get_object_or_404(UserProfile, profile_user=user)
        if article in userprofile.liked_article.all():
            context['like'] = 1
        else:
            context['like'] = 0
        if article in userprofile.unliked_article.all():
            context['dislike'] = 1
        else:
            context['dislike'] = 0
        if article in userprofile.collected_article.all():
            context['collect'] = 1
        else:
            context['collect'] = 0
    else:
        context['role'] = 1

    comments = Comment.objects.filter(related_article=article)
    context['comments'] = comments

    return render(request,'articlePage.html',context)

@login_required
def getImg(request, type, id):
    article=get_object_or_404(Article,id=id)
    if type == 0:
        img=article.img
    if type==1:
        img=article.big_img
    return HttpResponse(img)


def demo(request):
    return render(request, 'demo.html', {})



def checkCollect(article, user):
    userProfile = UserProfile.objects.get(profile_user=user)
    articles = userProfile.collected_article.all()
    for a in articles:
        if a == article: return True
    return False

def checkLike(article, user):
    userProfile = UserProfile.objects.get(profile_user=user)
    articles = userProfile.liked_article.all()
    for a in articles:
        if a == article: return True
    return False

def checkUnlike(article, user):
    userProfile = UserProfile.objects.get(profile_user=user)
    articles = userProfile.unliked_article.all()
    for a in articles:
        if a == article: return True
    return False




def createQuestion(request):
    user = get_object_or_404(User, username=request.user.username)
    # if the user is a client, redirect to create questions
    if user.role == 1:
        return redirect(reverse(createQuestion))

    # if user has not built profile, return Q&A page
    writer =UserProfile.objects.get(profile_user=user)
    if request.method == 'GET' :
        return render(request, 'articleForm.html', {})
    res = request.POST
    tag = [res['category'],res['tag']]
    time = timezone.now();
    question= Question.objects.create(question_title=res['question'],question_description=res['detail']
                                      ,tag=tag, question_creation_time=time,user=writer, collect_count=0)
    question.save();
    return render(request, 'qna.html',{})



@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    user = get_object_or_404(User, username=request.user.username)
    if user == question.user:
        question.delete()
    
    return redirect(reverse('qna'))




@login_required
def questionPage(request, question_id):
    context = {}
    user = get_object_or_404(User, username=request.user.username)
    question = get_object_or_404(Question, id=question_id)
    context['question'] = question

    if question.user == user:
        context['poster'] = 1
    else:
        context['poster'] = 0

    if user.role == 0:
        context['role'] = 0
        userprofile = get_object_or_404(UserProfile, profile_user=user)
        liked_answer = userprofile.liked_answer.all()
        context['liked_answer'] = liked_answer
        disliked_answer = userprofile.unliked_answer.all()
        context['disliked_answer'] = disliked_answer
        if question not in userprofile.collected_question.all():
            context['collect'] = 0
        else:
            context['collect'] = 1
    else:
        context['role'] = 1

    answers = Answer.objects.filter(related_question=question)
    context['answers'] = answers

    return render(request,'questionPage.html',context)



@login_required
def submit_answer(request, question_id):

    lawyer = get_object_or_404(User, username=request.user.username)
    question = get_object_or_404(Question, id=question_id)
    question.answer_count += 1
    answer_text = request.POST.get('answer_text')
    new_answer = Answer(answer_text=answer_text, lawyer=lawyer, related_question=question)
    new_answer.save()
    question.save()

    return redirect(reverse('questionPage', kwargs={'question_id':question.id}))



@login_required
def categories(request):
    context = {}

    user = get_object_or_404(User, username=request.user.username)
    context['user'] = user
    return render(request, 'categories.html', context)



def loginAction(request):
    context = {}

    # Just display the login form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'login.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = LoginForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
    login(request, new_user)

    return redirect(reverse('homepage'))

def logoutAction(request):
    logout(request)
    return redirect(reverse('login'))

def register(request):
    context = {}
    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'register.html', context)
    
    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegisterForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'register.html', context)
    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['firstname'],
                                        last_name=form.cleaned_data['lastname'],
                                        role=int(form.cleaned_data['role']))
    new_user.save()
    if new_user.role == 0:
        new_profile = UserProfile(profile_user=new_user)
    else:
        new_profile = LawyerProfile(profile_user=new_user)
    new_profile.save()

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])


    
    login(request, new_user)
    return redirect(reverse('homepage'))



@ensure_csrf_cookie
@login_required
def home(request):
    context = {}
    context['username']  = request.user.username
    context['firstname'] = request.user.first_name
    context['lastname']  = request.user.last_name

    return render(request, 'base.html', context)



def get_myprofile(request):
    context = {}

    user = get_object_or_404(User, username=request.user.username)
    context['user'] = user

    if user.role == 0:
        # user: Collection of Articles; Asked Questions; Follow-up Questions
        myprofile = get_object_or_404(UserProfile, profile_user=user)
        collections = myprofile.collected_article.all()
        context['collections'] = collections
        questions = Question.objects.filter(user=user)
        context['questions'] = questions
        follows = myprofile.collected_question.all()
        context['follows'] = follows

    else:
        myprofile = get_object_or_404(LawyerProfile, profile_user=user)
        posted = Article.objects.filter(article_writer=myprofile)
        context['posted'] = posted
        answers = Answer.objects.filter(lawyer=user)
        questions = []
        for answer in answers:
            questions.append(answer.related_question)
        context['questions'] = questions

    context['profile'] = myprofile

    if user.role == 0:
        # userpage
        return render(request, 'userprofile.html', context)
    else:
        # lawyerpage
        return render(request, 'lawyerprofile.html', context)

def other_profile_action(request,id):
    if id == request.user.id:
        return redirect(reverse('myprofile'))
    else:
        context = {}
        user = get_object_or_404(User, id=id)
        if user.role == 0:
            myprofile = get_object_or_404(UserProfile, profile_user=user)
            collections = myprofile.collected_article.all()
            context['collections'] = collections
            questions = Question.objects.filter(user=user)
            context['questions'] = questions
            follows = myprofile.collected_question.all()
            context['follows'] = follows
        else:
            myprofile = get_object_or_404(LawyerProfile, profile_user=user)
            posted = Article.objects.filter(article_writer=myprofile)
            context['posted'] = posted
            answers = Answer.objects.filter(lawyer=user)
            questions = []
            for answer in answers:
                questions.append(answer.related_question)
            context['questions'] = questions

        context['profile'] = myprofile
        context['user'] =  user
        
        if user.role == 0:
            # userpage
            return render(request, 'userprofile.html', context)
        else:
            # lawyerpage
            return render(request, 'lawyerprofile.html', context)



@login_required
def get_picture(request, id):
    user = get_object_or_404(User, id=id)
    if user.role == 0:
        profile = get_object_or_404(UserProfile, profile_user=user)
    else:
        profile = get_object_or_404(LawyerProfile, profile_user=user)

    # Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
    if not profile.profile_picture:
        raise Http404

    return HttpResponse(profile.profile_picture, content_type=profile.content_type)


@login_required
def edituser(request):
    return render(request, 'edituser.html', {})

@login_required
def editlawyer(request):
    return render(request, 'editlawyer.html', {})


@ensure_csrf_cookie
@login_required
def change_edit(request):
    context = {}
    
    user = get_object_or_404(User, username=request.user.username)
    if user.role == 0:
        myprofile = get_object_or_404(UserProfile, profile_user=user)
    else:
        myprofile = get_object_or_404(LawyerProfile, profile_user=user)
    
    pic = request.FILES.get('picture')
    if pic is not None:
        myprofile.profile_picture = pic
        myprofile.content_type = pic.content_type
        
    if request.POST.get("phone"):
        myprofile.phone = request.POST.get("phone")
    if request.POST.get("address"):
        myprofile.address = request.POST.get("address")
    if request.POST.get("company"):
        myprofile.company = request.POST.get("company")
    if request.POST.get("introduction"):
        myprofile.introduction = request.POST.get("introduction")
    if request.POST.getlist("tags"):
        if user.role == 0:
            myprofile.tags = request.POST.getlist("tags")
        else:
            myprofile.categories = request.POST.getlist("tags")
    myprofile.save()
    return redirect(reverse('myprofile'))

def getRecommend(questions):
    qnas = []
    for question in questions:
        answer = Answer.objects.filter(related_question=question).order_by('-like_count').first()
        qnas.append([question, answer])
    return qnas


# has 3 articles in the database
@login_required
def homepage(request):
    context = {}
    context['username']  = request.user.username
    context['firstname'] = request.user.first_name
    context['lastname']  = request.user.last_name

    try:
        articles=Article.objects.all()[:3]
        context['a1']=articles[0]
        context['a2']=articles[1]
        context['a3']=articles[2]
        context['has_article']=True
    except:
        context['has_article']=False
        context['error']="should have 3 articles in databases"

    questions=Question.objects.filter(answer_count__gt=0).order_by('-collect_count')

    if len(questions) < 6:
        context['top_questions']=getRecommend(questions)
    else:
        context['top_questions']=getRecommend(questions[:5])

    questions_no_answer=Question.objects.filter(answer_count=0).order_by('-question_creation_time')
    if len(questions) < 6:
        context['questions']=questions_no_answer
    else:
        context['questions']=questions_no_answer[:5]

    # ranklist of lawyer
    lawyers = LawyerProfile.objects.all().order_by('-review_score')
    if len(lawyers)  < 6:
        context['lawyers']=lawyers
    else:
        context['lawyers']=lawyers[:5]
    return render(request,'homepage.html',context)




@login_required
def lawyer_list(request):
    lawyers = sort_object_by_condition(request)
    # context = getlawyers(request,lawyers)
    context = {'lawyers': lawyers}
    return render(request,'lawyer_list.html',context)

def sort_object_by_condition(request):
    condition = request.GET.get('sort')
    lawyers = []
    if condition is None:
        # lawyers = User.objects.filter(role = 1)
        lawyers = LawyerProfile.objects.all().order_by('-review_score')
    elif condition == 'review_score':
        # lawyers = User.objects.filter(role = 1).order_by(condition)
        lawyers = LawyerProfile.objects.all().order_by('-{}'.format(condition))
    else:
        user = User.objects.filter(role = 1).order_by(condition)
        for u in user:
            lawyer = LawyerProfile.objects.get(profile_user = u)
            lawyers.append(lawyer)
    return lawyers




@ensure_csrf_cookie
@login_required
def qna_stream(request):
    context = {}

    user = get_object_or_404(User, username=request.user.username)
    context['user'] = user
    questions = get_object_by_category(request,"question")
    if "fault_category" in questions:
        return render(request,'blog.html',questions)
    qnas = []
    for question in questions:
        answer = Answer.objects.filter(related_question=question).order_by('-like_count').first()
        qnas.append([question, answer])
    context['qnas'] = qnas

    return render(request, 'qna.html', context)


@ensure_csrf_cookie
@login_required
def create_question(request):
    if request.method == "GET":
        return render(request, 'questionForm.html', {})

    res = request.POST
    if 'category' not in res or 'tag' not in res or 'title'not in res or 'description' not in res:
        context={}
        context['error']="Please do not change the variable name!"
        return render(request,"questionForm.html",context)
    
    user = get_object_or_404(User, username=request.user.username)
    question = Question(
        question_title=request.POST.get('title'),
        question_description=request.POST.get('description'),
        category=request.POST.get('category'),
        tag=request.POST.get('tag'),
        user=user
    )

    question.save()

    return redirect(reverse('qna'))


def get_qna_action(request):
    response_data = {}
    questions = []
    answers = []
    for q in Question.objects.all().order_by('-question_creation_time'):
        q_details = {
            'q_id': q.id,
            'q_title': q.question_title,
            'q_desc': q.question_description,
            'related_area': q.related_area,
            'related_tag': q.related_tag,
            'created_by': q.user.username,
            'author_id': q.user.id,
            'creation_time': q.question_creation_time.isoformat(),
            'collect_count': q.collect_count
        }
        questions.append(q_details)

    for a in Comment.objects.all():
        a_details = {
            'a_id': a.id,
            'answer_text': a.answer_text,
            'answered_by_username': a.answered_by_lawyer.username,
            'answered_by_userid': a.answered_by_lawyer.id,
            'answer_creation_time': a.answer_creation_time.isoformat(),
            'related_question': a.related_question.id,     
            'like_count': a.like_count,
            'dislike_count': a.dislike_count,
        }
        answers.append(a)
    response_data['questions'] = questions
    response_data['answers'] = answers

    response_json = json.dumps(response_data)

    # To make quiz11 work, we need to allow cross-origin access
    # Otherwise, just return the HTTPResponse
    response = HttpResponse(response_json, content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response



def add_answer_action(request):

    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=404)

    if not 'q_id' in request.POST or not request.POST['q_id']:   #no such thing here in the request
        return _my_json_error_response("You must enter a question id to add.")

    try:
        q_id = int(request.POST['q_id'])
    except:
        return _my_json_error_response("You must enter a valid question id")

    if not 'answer_text' in request.POST or not request.POST['answer_text']:
        return _my_json_error_response("You must enter an answer to add.")

    #like_count and dislike_count initially 0
    new_answer = Answer(answer_text=request.POST['answer_text'], answered_by_lawyer=request.user.LawyerProfile,
                          answer_creation_time=timezone.now(), related_question=Question.objects.get(id=q_id), like_count=0,dislike_count=0)
    new_answer.save()

    # set a default value to page if it does not exist
    page = request.POST.get('page', 'qna')
    return get_qna_action(request)
    # if page == "follower":
    #     return get_follower_action(request)
    # else:
    #     return get_global_action(request)

@login_required
def start_chat(request,pk:int):

    #no use, already type checked in the URL
    # try:
    #     int(pk)
    # except:
    #     html = "<html><h2>Please input a valid id to chat</h2></html>"
    #     return HttpResponse(html)

    try:
        other_user = User.objects.get(pk=pk)
    except:
        html = "<html><h2>Please input a valid id to chat</h2></html>"
        return HttpResponse(html)

    #cannot chat with oneself
    if pk == request.user.id:
        html = "<html><h2>You are not allowed to chat with yourself</h2></html>"
        return HttpResponse(html)

    #cannot contact between same type of users
    if request.user.role == other_user.role:
        html = "<html><h2>You are not allowed to chat with the same types of users</h2></html>"
        return HttpResponse(html)
        # return redirect(reverse('myprofile'))

    try:
        if request.user.role == 0 and other_user.role == 1:
            exiting_contact = ChatContact.objects.get(client=request.user,lawyer=other_user)
        elif request.user.role == 1 and other_user.role == 0:
            exiting_contact = ChatContact.objects.get(client=other_user,lawyer=request.user)
    except ChatContact.DoesNotExist:
        if request.user.role == 0 and other_user.role == 1:
            chatcontact = ChatContact(client=request.user,lawyer=other_user)
        elif request.user.role == 1 and other_user.role == 0:
            exiting_contact = ChatContact(client=other_user,lawyer=request.user)
        chatcontact.save()

    return chat_action(request, pk)

@login_required
def get_chatcontact(request):
    context = {}

    try:
        contacts = ChatContact.objects.filter(Q(client=request.user)|Q(lawyer=request.user))  #test if have contacts
        has_contacts = True
    except ChatContact.DoesNotExist:
        has_contacts = False
    context['has_contacts'] = has_contacts

    contact_list = []

    if request.user.role == 0:    # if I am normal user client, all my contacts are lawywers
        exiting_contacts = ChatContact.objects.filter(client=request.user)
        for contact in exiting_contacts:
            contact_list.append(contact.lawyer)
        context['contacts'] = contact_list

    elif request.user.role == 1:   # if I am lawyer, all my contacts are clients
        exiting_contacts = ChatContact.objects.filter(lawyer=request.user)
        for contact in exiting_contacts:
            contact_list.append(contact.client)
        context['contacts'] = contact_list


    # if len(contact_list)>0:
    #     has_contacts = True
    # else:
    #     has_contacts = False
    
    
    return render(request, 'view_all_contacts.html', context)

@ensure_csrf_cookie
@login_required
def chat_action(request,pk:int):
    
    other_user = get_object_or_404(User,pk=pk)

    #if user.role == 0       #user
    #if user.role == 1       #lawyer
    if request.method == 'GET':
        context = {
            # 'form': ChatMessageForm(),
            'other_user': other_user,
            'chatmessages': ChatMessage.objects.filter(Q(from_user= other_user, to_user= request.user
                                                        ) | Q(from_user= request.user, to_user= other_user)
                                                        ).order_by('message_creation_time'),
        }
        notify.send(
            request.user,
            recipient=other_user,
            verb='wants to chat',
            target=request.user,
            )

    if request.method == 'POST':
       context = create_chatmessage_action(request, pk)
        
    return render(request, 'chat.html', context)

@login_required
def create_chatmessage_action(request, pk:int):
    other_user = get_object_or_404(User,pk=pk)
    # if request.method == 'GET':
    #     c = ChatMessageForm()
    #     context = { 'form' : c ,'other_user': other_user, 'chatmessages': ChatMessage.objects.filter(Q(from_user= other_user, to_user= request.user
    #                                                 ) | Q(from_user= request.user, to_user= other_user)
    #                                                 ).order_by('message_creation_time')}
        # return render(request, 'chat.html', context)

    res = request.POST
    new_message = ChatMessage.objects.create(from_user=request.user,to_user = other_user,
                                             message_creation_time = timezone.now())
    
    # charField can be saved as '' anyway
    try:
        text = res['msg']
    except:
        text = None

    image = request.FILES.get('message_image')

    if text is not None:
        new_message.message_text = text

    if image is not None:
        new_message.message_image = image
        new_message.content_type = image.content_type

    # if not message_form.is_valid():
    #     context = { 'form': message_form, "error": "not valid"}
    #     return context

    new_message.save()
    context = {
        # 'form': ChatMessageForm(),
        'other_user': other_user,
        'chatmessages': ChatMessage.objects.filter(Q(from_user= other_user, to_user= request.user
                                            ) | Q(from_user= request.user, to_user= other_user)
                                            ).order_by('message_creation_time'),
    }
    # return render(request, 'chat.html', context)
    return context

@login_required
def get_chat_action(request,pk:int):
    # if not request.user.id:
    #     return _my_json_error_response("You must be logged in to do this operation", status=403)

    other_user = get_object_or_404(User,pk=pk)
    response_data = {}
    chatmessages = []
    for msg in ChatMessage.objects.filter(Q(from_user= other_user, to_user= request.user
                                                    ) | Q(from_user= request.user, to_user= other_user)
                                                    ).order_by('message_creation_time'):
        
        if msg.message_image is not None:
            message_image = msg.get_image_url
            # message_image = msg.message_image.url
        else:
            message_image = ""

        msg_details = {
            'id': msg.id,
            'message_text': msg.message_text,
            'message_image': message_image,
            'content_type': msg.content_type,
            'receiver_id': msg.to_user.id,
            'to_username': msg.to_user.username,
            'author_id': msg.from_user.id,
            'from_username': msg.from_user.username,
            'message_creation_time': msg.message_creation_time.isoformat(),
        }
        chatmessages.append(msg_details)

    response_data['chatmessages'] = chatmessages

    response_json = json.dumps(response_data)

    response = HttpResponse(response_json, content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response


def get_msg_image(request, id):
    context ={}
    f = ChatMessage.objects.get(id = id).message_image
    # f_type = f.content_type.split('/')[1]
    f_type = ChatMessage.objects.get(id = id).content_type

    return HttpResponse(f, content_type=f_type)

def _my_json_error_response(message, status=200):
    # You can create your JSON by constructing the string representation yourself (or just use json.dumps)
    response_json = '{ "error": "' + message + '" }'
    return HttpResponse(response_json, content_type='application/json', status=status)



@login_required
def search_keyword(request):
    if request.method == 'GET':
        return
    context = {}
    keyword = request.POST.get('keyword')
    context['keyword'] = keyword

    articles = []
    for article in Article.objects.all():
        lawyer = article.article_writer.profile_user
        if keyword in article.title or keyword in article.abstract or keyword in article.text or keyword in lawyer.first_name or keyword in lawyer.last_name or keyword in lawyer.first_name + ' ' + lawyer.last_name:
            articles.append(article)
    context['articles'] = articles

    questions = []
    for question in Question.objects.all():
        user = question.user
        if keyword in question.question_title or keyword in question.question_description or keyword in user.first_name or keyword in user.last_name or keyword in user.first_name + ' ' + user.last_name :
            questions.append(question)
    context['questions'] = questions

    return render(request, 'keyword.html', context)



class ChatNoticeListView(ListView):
    """notice list"""
    
    context_object_name = 'notices'
    
    template_name = 'notice_list.html'
    # # login
    # login_url = '/userprofile/login/'

    #query unread notifications
    def get_queryset(self):
        return self.request.user.notifications.unread()

class ChatNoticeUpdateView(View):
    """update the state of notifications"""
    # handle get request
    def get(self, request):
        # get notice id
        notice_id = request.GET.get('notice_id')

        # udpate single notice
        if notice_id:
            user_id=request.GET.get('chat_id')
            request.user.notifications.get(id=notice_id).mark_as_read()

            # return render(request,'chat/{}'.format(user_id))
            # return redirect('chat/{}'.format(user_id))
            return chat_action(request, user_id)
            
        # update all notice
        else:
            request.user.notifications.mark_all_as_read()
            return redirect('notice_list')

tag_list={
    'Contracts', 'Legislative compliance','Liability matters',
    'Defense for victim','Defense for criminal','Victimless crime',
    'Student residency', 'Personnel issues',
    'Student discipline','Special Education','Tuition Fraud',
    'Wage disputes', 'Sexual harassment', 'Child labor','Unlawful terminations'
    ,'Race, gender, sexual orientation, age, and disability discrimination'
    ,'The right to unionize','Workplace safety',
    'Adoptions','Child support','Domestic abuse'
    ,'Divorce','Prenuptial agreements',
    'Medicare policy and compliance','Public health policy','Biomedicine and telemedicine'
    ,'Mergers and acquisitions','Risk management','Bioethics and clinical ethics',
    'Asylum/refugee law','Business immigration law','International trade negotiations',
    'Patent law','Copyright law','Land and building ownership','Rights to possess and use land or buildings',
    'Sale and purchase of real property','Landlord-tenant issues','Development of real property',
    'Stocks','Mergers','Acquisitions','Corporate takeovers',
    'Income taxes','Mergers','Capital gains taxes','Tax evasion'
}
category_list={
    'Corporate','Crime','Education','Labor','Family','Health','Immigration','Intellectual Property'
    ,'Real Estate','Securities','Tax'
}