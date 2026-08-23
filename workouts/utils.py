import re

import jdatetime
import openpyxl
from openpyxl.styles import Font, Alignment
from django.http import HttpResponse

from .models import WorkoutDay


def to_jalali_str(d):
    """تبدیل تاریخ میلادی به رشته‌ی تاریخ شمسی (مثلاً 1405/03/12)."""
    return jdatetime.date.fromgregorian(date=d).strftime('%Y/%m/%d')


def get_week_start(d):
    """
    تاریخ شنبه‌ی همان هفته‌ی شمسی را برمی‌گرداند (به صورت تاریخ میلادی،
    چون در دیتابیس میلادی ذخیره می‌کنیم و فقط برای نمایش شمسی می‌کنیم).
    در تقویم jdatetime، شنبه = 0.
    """
    jd = jdatetime.date.fromgregorian(date=d)
    offset = jd.weekday()
    import datetime
    return d - datetime.timedelta(days=offset)


def _safe_sheet_name(name, day_id):
    cleaned = re.sub(r'[\\/*?:\[\]]', '', name)[:20]
    return f'{cleaned}-{day_id}' if cleaned else f'day-{day_id}'


def build_workout_excel(user):
    workbook = openpyxl.Workbook()
    workbook.remove(workbook.active)
    header_font = Font(bold=True)

    for day in WorkoutDay.objects.filter(user=user):
        sheet = workbook.create_sheet(title=_safe_sheet_name(day.name, day.id))

        headers = ['نام حرکت', 'نوع', 'تاریخ هفته (شمسی)', 'وزنه (kg)',
                    'ست ۱', 'ست ۲', 'ست ۳', 'ست ۴']
        sheet.append(headers)
        for cell in sheet[1]:
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')

        def _fmt(value, unit):
            return f'{value} {unit}' if value is not None else '-'

        for exercise in day.exercises.all():
            logs = exercise.logs.order_by('week_start')
            if not logs.exists():
                sheet.append([exercise.name, exercise.get_exercise_type_display(), '-', '-', '-', '-', '-', '-'])
                continue
            for log in logs:
                if exercise.exercise_type == 'weight':
                    sheet.append([
                        exercise.name, exercise.get_exercise_type_display(),
                        to_jalali_str(log.week_start),
                        _fmt(float(log.weight) if log.weight is not None else None, 'kg'),
                        _fmt(log.reps_set1, 'تکرار'), _fmt(log.reps_set2, 'تکرار'),
                        _fmt(log.reps_set3, 'تکرار'), _fmt(log.reps_set4, 'تکرار'),
                    ])
                else:
                    sheet.append([
                        exercise.name, exercise.get_exercise_type_display(),
                        to_jalali_str(log.week_start),
                        '-',
                        _fmt(log.duration_set1, 's'), _fmt(log.duration_set2, 's'),
                        _fmt(log.duration_set3, 's'), _fmt(log.duration_set4, 's'),
                    ])

        for column_cells in sheet.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            sheet.column_dimensions[column_cells[0].column_letter].width = length + 4

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f'workout-program-{user.username}.xlsx'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    workbook.save(response)
    return response