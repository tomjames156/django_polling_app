from django.contrib import admin
from .models import Question, Choice
# Register your models here.

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2

class QuestionAdminModel(admin.ModelAdmin):
    fieldsets = [
        ('Question information', {'fields': ['question_text', 'pub_date'], 'classes': ['collapse']}),
    ]
    list_filter = ['pub_date']
    search_fields = ['question_text', 'choice__choice_text']
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    inlines = [ChoiceInline]

admin.site.register(Question, QuestionAdminModel)
# admin.site.register(Choice)