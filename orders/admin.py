from django.contrib import admin
from .models import Orders, OrderItem
import csv
import datetime
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe


# Register your models here.

def order_detail(obj):
    url = reverse('orders:admin_order_detail', args=[obj.id])
    return mark_safe(f'<a href="{url}">View</a>')


def order_pdf(obj):
    url = reverse('orders:admin_order_pdf', args=[obj.id])
    return mark_safe(f'<a href="{url}">PDF</a>')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_field = ['product']


@admin.register(Orders)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'address', 'postal_code', 'city', 'paid', 'created',
                    'updated', order_detail, order_pdf]

    list_filter = ['paid', 'created', 'updated']

    inlines = [OrderItemInline]

    def export_csv(modeladmin, request, queryset):
        opts = modeladmin.model._meta
        content_disposition = f'attachment; filename={opts.verbose_name}.csv'
        response = HttpResponse(content_type='text/csv')
        response['content_disposition'] = content_disposition
        writer = csv.writer(response)

        fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]

        # Escreve uma primeira linha com informações de cabeçalho

        writer.writerow([field.verbose_name for field in fields])

        # Escreve as linhas de dados

        for obj in queryset:
            data_row = []
            for field in fields:
                value = getattr(obj, field.name)
                if isinstance(value, datetime.datetime):
                    value = value.strftime('%d/%m/%Y')
                data_row.append(value)
            writer.writerow(data_row)
        return response

    export_csv.short_description = 'Export to csv'
    actions = [export_csv]

