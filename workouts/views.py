import datetime
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import ExerciseForm, SignUpForm, WorkoutDayForm
from .models import Exercise, WorkoutDay, WorkoutLog
from .utils import build_workout_excel, get_week_start, to_jalali_str


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'ثبت‌نام با موفقیت انجام شد.')
            return redirect('day_select')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def day_select(request):
    days = WorkoutDay.objects.filter(user=request.user)
    days_data = [{'obj': d, 'exercise_count': d.exercises.count()} for d in days]
    return render(request, 'workouts/day_select.html', {'days': days_data})


@login_required
def create_day(request):
    if request.method == 'POST':
        form = WorkoutDayForm(request.POST)
        if form.is_valid():
            day = form.save(commit=False)
            day.user = request.user
            day.order = WorkoutDay.objects.filter(user=request.user).count()
            day.save()
            messages.success(request, f'«{day.name}» اضافه شد.')
        else:
            messages.error(request, 'نام روز نامعتبر است.')
    return redirect('day_select')


@login_required
@require_POST
def delete_day(request, day_id):
    day = get_object_or_404(WorkoutDay, id=day_id, user=request.user)
    day.delete()
    messages.success(request, 'روز تمرینی حذف شد.')
    return redirect('day_select')


@login_required
def manage_exercises(request, day_id):
    day = get_object_or_404(WorkoutDay, id=day_id, user=request.user)
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.user = request.user
            exercise.workout_day = day
            exercise.order = day.exercises.count()
            exercise.save()
            messages.success(request, f'حرکت «{exercise.name}» اضافه شد.')
            return redirect('manage_exercises', day_id=day.id)
    else:
        form = ExerciseForm()
    exercises = day.exercises.all()
    return render(request, 'workouts/manage_exercises.html', {'form': form, 'exercises': exercises, 'day': day})


@login_required
@require_POST
def delete_exercise(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id, user=request.user)
    day_id = exercise.workout_day_id
    exercise.delete()
    messages.success(request, 'حرکت حذف شد.')
    return redirect('manage_exercises', day_id=day_id)


@login_required
def day_program(request, day_id):
    day = get_object_or_404(WorkoutDay, id=day_id, user=request.user)

    week_param = request.GET.get('week') or request.POST.get('week_start')
    if week_param:
        try:
            selected_week = datetime.datetime.strptime(week_param, '%Y-%m-%d').date()
        except ValueError:
            selected_week = get_week_start(datetime.date.today())
    else:
        selected_week = get_week_start(datetime.date.today())

    exercises = day.exercises.all()
    if not exercises.exists():
        messages.info(request, 'ابتدا حرکات این روز را اضافه کنید.')
        return redirect('manage_exercises', day_id=day.id)

    if request.method == 'POST':
        has_error = False
        for exercise in exercises:
            if exercise.exercise_type == 'weight':
                weight_raw = request.POST.get(f'weight_{exercise.id}', '').strip()
                if weight_raw == '':
                    continue
                reps_raw = [request.POST.get(f'reps{i}_{exercise.id}', '0').strip() or '0' for i in range(1, 5)]
                try:
                    weight_value = Decimal(weight_raw)
                    reps = [int(x) for x in reps_raw]
                except (InvalidOperation, ValueError):
                    has_error = True
                    messages.error(request, f'مقدار وارد شده برای «{exercise.name}» نامعتبر است.')
                    continue
                WorkoutLog.objects.update_or_create(
                    exercise=exercise, week_start=selected_week,
                    defaults={
                        'user': request.user,
                        'weight': weight_value,
                        'reps_set1': reps[0], 'reps_set2': reps[1], 'reps_set3': reps[2], 'reps_set4': reps[3],
                        'duration_set1': None, 'duration_set2': None, 'duration_set3': None, 'duration_set4': None,
                    },
                )
            else:
                durations_raw = [request.POST.get(f'dur{i}_{exercise.id}', '').strip() for i in range(1, 5)]
                if all(d == '' for d in durations_raw):
                    continue
                try:
                    durations = [int(d) if d != '' else None for d in durations_raw]
                except ValueError:
                    has_error = True
                    messages.error(request, f'مقدار وارد شده برای «{exercise.name}» نامعتبر است.')
                    continue
                WorkoutLog.objects.update_or_create(
                    exercise=exercise, week_start=selected_week,
                    defaults={
                        'user': request.user,
                        'weight': None,
                        'reps_set1': None, 'reps_set2': None, 'reps_set3': None, 'reps_set4': None,
                        'duration_set1': durations[0], 'duration_set2': durations[1],
                        'duration_set3': durations[2], 'duration_set4': durations[3],
                    },
                )

        if not has_error:
            messages.success(request, f'برنامه‌ی هفته‌ی {to_jalali_str(selected_week)} ذخیره شد.')
            return redirect(f"{reverse('day_program', args=[day.id])}?week={selected_week}")

    rows = []
    for exercise in exercises:
        log = WorkoutLog.objects.filter(exercise=exercise, week_start=selected_week).first()
        rows.append({'exercise': exercise, 'log': log})

    context = {
        'day': day,
        'rows': rows,
        'selected_week': selected_week,
        'selected_week_jalali': to_jalali_str(selected_week),
        'selected_week_end_jalali': to_jalali_str(selected_week + datetime.timedelta(days=6)),
        'prev_week': selected_week - datetime.timedelta(days=7),
        'next_week': selected_week + datetime.timedelta(days=7),
    }
    return render(request, 'workouts/day_program.html', context)


@login_required
def progress_list(request):
    exercises = Exercise.objects.filter(user=request.user)
    return render(request, 'workouts/progress_list.html', {'exercises': exercises})


@login_required
def progress_chart(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id, user=request.user)
    return render(request, 'workouts/progress_chart.html', {'exercise': exercise})


@login_required
def progress_data(request, exercise_id):
    """
    خروجی JSON برای نمودار.
    برای حرکات وزنه‌ای: یک سری داده (وزنه).
    برای حرکات زمانی: یک سری جدا برای هر ستی که حداقل یک بار برایش
    مقدار ثبت شده (مثلاً اگر همیشه فقط ۳ ست پر شده، ست ۴ اصلاً نمایش داده نمی‌شود).
    """
    exercise = get_object_or_404(Exercise, id=exercise_id, user=request.user)
    logs = list(exercise.logs.order_by('week_start'))
    labels = [to_jalali_str(log.week_start) for log in logs]

    if exercise.exercise_type == 'weight':
        series = [{
            'name': 'وزنه',
            'values': [float(log.weight) if log.weight is not None else None for log in logs],
        }]
        unit = 'وزنه (kg)'
    else:
        unit = 'مدت (ثانیه)'
        series = []
        set_fields = [
            ('duration_set1', 'ست ۱'),
            ('duration_set2', 'ست ۲'),
            ('duration_set3', 'ست ۳'),
            ('duration_set4', 'ست ۴'),
        ]
        for field, label in set_fields:
            values = [getattr(log, field) for log in logs]
            # فقط ستی که حداقل یک بار مقدار داشته را نشان بده
            if any(v is not None for v in values):
                series.append({'name': label, 'values': values})

    return JsonResponse({
        'labels': labels,
        'series': series,
        'exercise_name': exercise.name,
        'unit': unit,
    })

@login_required
def export_excel(request):
    return build_workout_excel(request.user)