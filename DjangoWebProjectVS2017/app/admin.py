
from django.contrib import admin
from app.models import Choice, Question, QuestionQuiz, Answers

class ChoiceInline(admin.TabularInline):
    model = Answers
    extra = 3

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    list_display = ('question_text', 'pub_date')
    inlines = [ChoiceInline]

#admin.site.register(Question,QuestionAdmin)
admin.site.register(QuestionQuiz,QuestionAdmin)