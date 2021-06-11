from django.db import models
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.models import AbstractUser
#from django.contrib.auth.models import User
from django_mysql.models import ListCharField
from django.db.models import UniqueConstraint
from django.conf import settings
from django.conf.urls.static import static

class User(AbstractUser):
    role = models.IntegerField(default=0)    #0 is normal user, 1 is lawyer

# Create your models here.
class LawyerProfile(models.Model):
    profile_picture = models.FileField(blank=True)
    content_type    = models.CharField(max_length=50)

    company         = models.CharField(max_length=20)
    phone           = models.CharField(max_length=20)
    address         = models.CharField(max_length=50)
    profile_user    = models.OneToOneField(User, on_delete=models.PROTECT,related_name="lawyerprofile_owner")
    introduction    = models.CharField(max_length=200)
    
    # posted_article   = models.OneToManyField(Article, blank=True)
    licence_number = models.CharField(max_length=20)
    # answered = models.OneToManyField(Answer, blank=True)
    review_score = models.FloatField(max_length=20,default=0)
    #add lawyer specialized catagories
    categories = ListCharField(
        base_field=models.CharField(max_length=50),
        size=40,
        max_length=(40*51),
        default=[],
    )

class Article(models.Model):
    img =  models.FileField(blank=True)
    big_img = models.FileField(blank=True)
    title       = models.CharField(max_length=200)
    abstract    = models.CharField(max_length=450)
    text        = models.TextField()
    article_creation_time  = models.DateTimeField(default=datetime.now())
    article_writer    = models.ForeignKey(LawyerProfile, on_delete=models.PROTECT,related_name="article_writer")
    like_count = models.IntegerField()
    dislike_count = models.IntegerField()
    collect_count = models.IntegerField()
    tag = ListCharField(
            models.CharField(max_length=50),
            size=2,
            max_length=(2*51),
          )


class Question(models.Model):
    question_title = models.CharField(max_length=200)
    question_description = models.CharField(max_length=200)
    category = models.CharField(max_length=200)
    tag = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    question_creation_time = models.DateTimeField(default=datetime.now())
    collect_count = models.IntegerField(default=0)
    answer_count = models.IntegerField(default=0)



class Answer(models.Model):
    answer_text = models.CharField(max_length=200)
    lawyer     = models.ForeignKey(User, on_delete=models.PROTECT)
    answer_creation_time  = models.DateTimeField(default=datetime.now())
    related_question      = models.ForeignKey(Question, on_delete=models.PROTECT, related_name="question")
    like_count = models.IntegerField(default=0)
    dislike_count = models.IntegerField(default=0)



class UserProfile(models.Model):
    profile_picture = models.FileField(blank=True)
    content_type    = models.CharField(max_length=50)

    company         = models.CharField(max_length=20)
    phone           = models.CharField(max_length=20)
    address         = models.CharField(max_length=20)
    introduction    = models.CharField(max_length=200)
    profile_user    = models.OneToOneField(User, on_delete=models.PROTECT,related_name="userprofile_owner")
    
    collected_article   = models.ManyToManyField(Article, blank=True, related_name="collected_article")
    liked_article   = models.ManyToManyField(Article, blank=True, related_name="liked_article")
    unliked_article = models.ManyToManyField(Article, blank=True, related_name="unliked_article")

    collected_question = models.ManyToManyField(Question, blank=True, related_name="collected_question")
    liked_answer = models.ManyToManyField(Answer, blank=True, related_name="liked_answer")
    unliked_answer = models.ManyToManyField(Answer, blank=True, related_name="unliked_answer")
    
    tags = ListCharField(
        base_field=models.CharField(max_length=50),
        size=40,
        max_length=(40*51),
        default=[],
    )




class Comment(models.Model):
    comment_input_text     = models.CharField(max_length=200)
    user                   = models.ForeignKey(User, on_delete=models.PROTECT, related_name="comment_by_user")
    comment_creation_time  = models.DateTimeField(default=datetime.now())
    related_article        =  models.ForeignKey(Article, on_delete=models.PROTECT, related_name="article")

class ChatMessage(models.Model):
    to_user                 = models.ForeignKey(User, on_delete=models.PROTECT, related_name="msg_receiver")
    from_user               = models.ForeignKey(User, on_delete=models.PROTECT, related_name="msg_sender")
    message_text            = models.CharField(max_length=2000,blank=True)
    message_creation_time   = models.DateTimeField(default=datetime.now())
    message_image           = models.FileField(blank=True)
    content_type            = models.CharField(max_length=200,blank=True)
    # message_type            = models.CharField(max_length=1,blank=True)    #t is normal text, i is image
    
    @property
    def get_image_url(self):
        if self.message_image and hasattr(self.message_image, 'url'):
            return self.message_image.url


class ChatContact(models.Model):
    client                  = models.ForeignKey(User, on_delete=models.PROTECT, related_name="client_in_contact")
    lawyer                  = models.ForeignKey(User, on_delete=models.PROTECT, related_name="lawyer_in_contact")

