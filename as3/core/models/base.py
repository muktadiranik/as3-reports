from config.celery import celery_app
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .managers.user import UserManager


class Countries(models.Model):
    name = models.CharField(max_length=100, unique=True)
    units = models.CharField(max_length=100)
    active = models.BooleanField(default = True)
    class Meta:
        db_table = 'api_basic_countries'
        verbose_name = _('country')
        verbose_name_plural = _('countries')
    
class Users(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()
    profile = models.CharField(max_length = 63, choices=(
        ("Admin", "Admin"),
        ("Superadmin", "Superadmin"),
        ("Company", "Company"),
        ("Student", "Student"),
        ("Group", "Group"),
        ("Team", "Team"),
    ), null = True, db_column='profile', db_index = True)
    email = models.EmailField(_('Email Address'), db_index=True, unique=True)
    active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    name = models.CharField(max_length=150, null = True, blank = True)
    
    emailVerified = models.BooleanField(default = False)
    tokenExpired = models.BooleanField(default = False)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True, null = True, blank = True)
    idCountry = models.ForeignKey(Countries, on_delete=models.PROTECT, null = True, db_column='idCountry')
    phone = models.CharField(max_length=100, null = True, blank = True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = []

    class Meta:
        app_label = "core"
        db_table = 'api_basic_users'
        verbose_name = _('Users')
        verbose_name_plural = _('Users')

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.profile = "Superadmin"
        if self.profile == "Company":
            pass
        super(Users, self).save(*args, **kwargs)

    @celery_app.task(bind = True)
    def send_email(self, to_emails, subject, html_content, **kwargs):
        message = Mail(
            from_email='no-reply@as3international.com',
            to_emails= to_emails,
            subject=subject,
            html_content= html_content
        )
        try:
            sg = SendGridAPIClient(settings.SENDGRID_APIKEY)
            response = sg.send(message)
            print(response.status_code)
        except Exception as e:
            raise AssertionError('Invalid header found. {}'.format(e))

    @property
    def is_superadmin_profile(self):
        if self.profile == "Superadmin":
            return True
        return False
    
    @property
    def is_admin_profile(self):
        if self.profile == "Admin":
            return True
        return False

    @property
    def is_company_profile(self):
        if self.profile == "Company":
            return True
        return False

    @property
    def is_superadmin_or_admin(self):
        return self.is_superadmin_profile or self.is_admin_profile
                    
class Locations(models.Model):
    """
    This table is used to link the Team names.
    NOTE: Do not confuse Location table with Venue (for exercise venue)
    """
    address1 = models.CharField(max_length=120, null = True, blank = True)
    address2 = models.CharField(max_length=120, null = True, blank = True)
    city = models.CharField(max_length=100, null = True, blank = True)
    state = models.CharField(max_length=100, null = True, blank = True)
    idCountry = models.ForeignKey(Countries, on_delete=models.PROTECT, db_column='idCountry')
    active = models.BooleanField(default=True)
    
    @property
    def full_address(self):
        return self.address1 + " " + self.address2 + ' ' + self.city \
            + " " + self.state
    
    class Meta:
        db_table = 'api_basic_locations'
        verbose_name = _('location')
        verbose_name_plural = _('locations')

class Companies(models.Model):    
    name = models.CharField(max_length=180, unique=True)
    contact = models.CharField(max_length=100, null = True, blank = True)
    # idUser = models.OneToOneField(
        # Users, on_delete=models.PROTECT, null = True, db_column='idUser',
        # db_index=True, related_name="company")
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    class Meta:
        db_table = 'api_basic_companies'
        verbose_name = _('company')
        verbose_name_plural = _('companies')
    
    def get_absolute_url(self):
        return reverse("core:index")
    
    def get_students_absolute_url(self):
        return reverse("core:students")


class CompanyUsers(models.Model):
    idCompany = models.ForeignKey(Companies, on_delete = models.PROTECT, db_index=True, db_column='idCompany')
    idUser = models.OneToOneField(Users, on_delete = models.PROTECT, db_index=True, db_column='idUser')
    class Meta:
        db_table = 'api_basic_company_users'
        verbose_name = _('company_users')

class Groups(models.Model):
    name = models.CharField(max_length=180, unique=True)
    description = models.TextField(null = True, blank = True)
    idCountry = models.ForeignKey(Countries, on_delete=models.PROTECT, null = True, db_column='idCountry')
    # idUser = models.OneToOneField(Users, on_delete=models.PROTECT, null = True, db_column='idUser', related_name="user_group")
    active = models.BooleanField(default=True)
    class Meta:
        db_table = 'api_basic_groups'
        verbose_name = _('group')
        verbose_name_plural = _('groups')

class GroupUsers(models.Model):
    idGroup = models.ForeignKey(Groups, on_delete = models.PROTECT, db_index=True)
    idUser = models.OneToOneField(Users, on_delete = models.PROTECT, db_index=True)
    class Meta:
        db_table = 'api_basic_group_users'
        verbose_name = _('group_users')
class Teams(models.Model):
    name = models.CharField(max_length=180, db_index=True, unique=True)
    idLocation = models.ForeignKey(Locations, on_delete=models.PROTECT, null = True, db_column='idCLocation')
    # idUser = models.OneToOneField(Users, on_delete=models.PROTECT, null = True, db_column='idUser')
    idCompany = models.ForeignKey(Companies, on_delete=models.PROTECT, null = True, db_column='idCompany')
    description = models.TextField(null = True, blank = True)
    active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'api_basic_teams'
        verbose_name = _('team')
        verbose_name_plural = _('teams')

class TeamUsers(models.Model):
    idTeam = models.ForeignKey(Teams, on_delete = models.PROTECT, db_index=True)
    idUser = models.OneToOneField(Users, on_delete = models.PROTECT, db_index=True)
    class Meta:
        db_table = 'api_basic_team_users'
        verbose_name = _('team_users')
  
class Students(models.Model):
    studentId = models.CharField(max_length=63, unique=True, db_index=True, blank = True)
    idUser = models.OneToOneField(Users, on_delete=models.PROTECT, null = True, db_column='idUser')
    email = models.EmailField(_('Email Address'),  null = True, blank = True)
    phone = models.CharField(max_length=100, null = True, blank = True)
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    gender = models.CharField(max_length=100, choices = (
        ("M", "Male"),
        ("F","Female"),
        ("NA", "Rather not say")
    ))
    birthday = models.DateField(null = True, blank = True)
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    
    class Meta:
        db_table = 'api_basic_students'
        verbose_name = _('student')
        verbose_name_plural = _('students')
        unique_together = (
            ("firstName", "lastName", "birthday")
        )
    def fullName(self):
        return f"{self.firstName} {self.lastName}"
    
class Programs(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index = True)
    durationDays = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)

    class Meta:
        db_table = 'api_basic_programs'
        verbose_name = _('program')
        verbose_name_plural = _('programs') 

class GroupStudents(models.Model):
    idGroup = models.ForeignKey(Groups, on_delete=models.PROTECT, db_column='idGroup', db_index = True)
    idStudent = models.ForeignKey(Students, on_delete=models.PROTECT, db_column='idStudent', db_index = True)
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)

    class Meta:
        db_table = 'api_basic_groupstudents'
        verbose_name = _('GroupStudent')
        verbose_name_plural = _('GroupStudents') 

class TeamStudents(models.Model):
    idTeam = models.ForeignKey(Teams, on_delete=models.PROTECT, db_column='idTeam')
    idStudent = models.ForeignKey(Students, on_delete=models.PROTECT, db_column='idStudent')
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    
    class Meta:
        db_table = 'api_basic_teamstudents'
        verbose_name = _('TeamStudent')
        verbose_name_plural = _('TeamStudents') 

class GroupTeams(models.Model):
    idGroup = models.ForeignKey(Groups, on_delete=models.PROTECT, db_column='idGroup', db_index = True)
    idTeam = models.ForeignKey(Teams, on_delete=models.PROTECT, db_column='idTeam, db_index = True')
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    
    class Meta:
        db_table = 'api_basic_groupteams'
        verbose_name = _('GroupTeam')
        verbose_name_plural = _('GroupTeams') 

class Venues(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index = True)
    idCountry = models.ForeignKey(Countries, on_delete=models.PROTECT, null = True, db_column='idCountry')
    state = models.CharField(max_length=100, null = True, blank = True)
    address1 = models.CharField(max_length=100, null = True, blank = True)
    address2 = models.CharField(max_length=100, null = True, blank = True)
    city = models.CharField(max_length=100, null = True, blank = True)
    phone = models.CharField(max_length=100, null = True, blank = True)
    email = models.EmailField(null = True, blank = True)
    active = models.BooleanField(_('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        )
    )
    
    def venue_str(self):
        return f"{self.address1} {self.address2} {self.city} {self.idCountry.name}"
    
    class Meta:
        db_table = 'api_basic_venues'
        verbose_name = _('venue')
        verbose_name_plural = _('venues')
        
class Courses(models.Model):
    idVenue = models.ForeignKey(Venues, on_delete=models.PROTECT, db_column='idVenue', db_index = True)
    idProgram = models.ForeignKey(Programs, on_delete=models.PROTECT, db_column='idProgram', db_index = True)
    eventDate = models.DateField(db_index = True)
    idealTime = models.FloatField()
    conePenalty = models.IntegerField()
    gatePenalty = models.IntegerField()
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    isOpenEnrollment = models.BooleanField(default = False) # ok
    class Meta:
        db_table = 'api_basic_courses'
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')  
        unique_together = [("idVenue", "idProgram", "eventDate")]
     
class Participations(models.Model):
    idCourse = models.ForeignKey(Courses, on_delete=models.PROTECT, db_column='idCourse', db_index=True)
    idStudent = models.ForeignKey(Students, on_delete=models.PROTECT, db_column='idStudent', db_index=True)
    idCompany = models.ForeignKey(Companies, on_delete=models.PROTECT, null = True, db_column='idCompany', db_index=True)
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)

    class Meta:
        db_table = 'api_basic_participations'
        verbose_name = _('Participation')
        verbose_name_plural = _('Participations')
        unique_together = [("idCourse", "idStudent")]

        
class Vehicles(models.Model):
    name = models.CharField(max_length=100, unique = True, db_index = True)
    latAcc = models.FloatField()
    type = models.CharField(max_length=100, null = True, blank = True)
    make = models.FloatField(default = 0)
    model = models.CharField(max_length=100, null = True, blank = True)
    active = models.BooleanField(default = True)
    image = models.ImageField(upload_to="vehicles", blank=True, null = True)
    
    class Meta:
        db_table = 'api_basic_vehicles'
        verbose_name = _('vehicle')
        verbose_name_plural = _('vehicles')
        # unique_together = [("name", "latAcc")]
        
class Comments(models.Model):
    idParticipation = models.ForeignKey(Participations, on_delete=models.PROTECT, db_column='idParticipation', db_index = True) 
    # idStudent =  models.ForeignKey(Students, on_delete=models.PROTECT, db_column='idStudent', db_index = True)
    # idCourse = models.ForeignKey(Courses, on_delete=models.PROTECT, db_column='idCourse', db_index = True)
    comment = models.TextField()
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)

    class Meta:
        db_table = 'api_basic_comments'
        verbose_name = _('comment')
        verbose_name_plural = _('comments')
        # unique_together = [("idStudent", "idCourse")]

class Exercises(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index = True)
    active = models.BooleanField(default = True)
    class Meta:
        db_table = 'api_basic_exercises'
        verbose_name = _('Exercise')
        verbose_name_plural = _('Exercises')
        
class Feedback(models.Model):
    idCompany = models.ForeignKey(Companies, on_delete=models.PROTECT, null = True, db_column='idCompany', db_index = True)
    idUser = models.ForeignKey(Users, on_delete=models.PROTECT, null = True, db_column='idUser', db_index = True)
    timestamp = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=150, null = True, blank=True)
    likeMost = models.TextField()
    didntLike = models.TextField()
    futureSuggestion = models.TextField()
    overallFeedback = models.TextField()
    rating = models.IntegerField()
    
    resolved = models.BooleanField(default = False)
    resolve_comment = models.TextField(null = True, blank = True)
    class Meta:
        db_table = 'api_basic_feedback'
        verbose_name = _('Feedback')
        verbose_name_plural = _('Feedbacks')
