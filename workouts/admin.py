from django.contrib import admin

from .models import WorkoutDay, Exercise, WorkoutLog


@admin.register(WorkoutDay)
class WorkoutDayAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'order')
    list_filter = ('user',)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'workout_day', 'exercise_type', 'order')
    list_filter = ('exercise_type', 'user')
    search_fields = ('name',)


@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    list_display = ('exercise', 'user', 'week_start', 'weight')
    list_filter = ('week_start', 'user')
    search_fields = ('exercise__name',)