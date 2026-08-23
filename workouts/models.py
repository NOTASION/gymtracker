from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models

EXERCISE_TYPE_CHOICES = [
    ('weight', 'وزنه‌ای'),
    ('time', 'زمانی (ثانیه)'),
]


class WorkoutDay(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_days')
    name = models.CharField('نام روز', max_length=100)
    order = models.PositiveIntegerField('ترتیب', default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.user.username} - {self.name}'


class Exercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercises')
    workout_day = models.ForeignKey(WorkoutDay, on_delete=models.CASCADE, related_name='exercises')
    name = models.CharField('نام حرکت', max_length=150)
    exercise_type = models.CharField(
        'نوع حرکت', max_length=10, choices=EXERCISE_TYPE_CHOICES, default='weight'
    )
    order = models.PositiveIntegerField('ترتیب', default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.workout_day.name} - {self.name}'


class WorkoutLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_logs')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='logs')

    week_start = models.DateField('تاریخ هفته (میلادی - داخلی)')

    weight = models.DecimalField(
        'وزنه (کیلوگرم)', max_digits=6, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)],
    )
    reps_set1 = models.PositiveSmallIntegerField('تکرار ست ۱', null=True, blank=True)
    reps_set2 = models.PositiveSmallIntegerField('تکرار ست ۲', null=True, blank=True)
    reps_set3 = models.PositiveSmallIntegerField('تکرار ست ۳', null=True, blank=True)
    reps_set4 = models.PositiveSmallIntegerField('تکرار ست ۴', null=True, blank=True)

    duration_set1 = models.PositiveIntegerField('مدت ست ۱ (ثانیه)', null=True, blank=True)
    duration_set2 = models.PositiveIntegerField('مدت ست ۲ (ثانیه)', null=True, blank=True)
    duration_set3 = models.PositiveIntegerField('مدت ست ۳ (ثانیه)', null=True, blank=True)
    duration_set4 = models.PositiveIntegerField('مدت ست ۴ (ثانیه)', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('exercise', 'week_start')
        ordering = ['week_start']

    def __str__(self):
        return f'{self.exercise.name} | {self.week_start}'