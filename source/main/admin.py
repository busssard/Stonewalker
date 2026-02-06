from django.contrib import admin
from .models import Stone, StoneMove, StoneScanAttempt, QRPack


@admin.register(QRPack)
class QRPackAdmin(admin.ModelAdmin):
    list_display = ['id', 'pack_type', 'status', 'FK_user', 'price_cents', 'created_at', 'paid_at']
    list_filter = ['pack_type', 'status', 'created_at']
    search_fields = ['id', 'FK_user__username', 'stripe_payment_intent_id']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('FK_user')


@admin.register(Stone)
class StoneAdmin(admin.ModelAdmin):
    list_display = ['PK_stone', 'status', 'FK_user', 'stone_type', 'created_at', 'claimed_at']
    list_filter = ['status', 'stone_type', 'created_at']
    search_fields = ['PK_stone', 'uuid', 'FK_user__username', 'description']
    readonly_fields = ['uuid', 'created_at', 'updated_at', 'qr_code_url']
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('FK_user', 'FK_pack')


@admin.register(StoneMove)
class StoneMoveAdmin(admin.ModelAdmin):
    list_display = ['FK_stone', 'FK_user', 'timestamp', 'latitude', 'longitude']
    list_filter = ['timestamp']
    search_fields = ['FK_stone__PK_stone', 'FK_user__username', 'comment']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(StoneScanAttempt)
class StoneScanAttemptAdmin(admin.ModelAdmin):
    list_display = ['FK_stone', 'FK_user', 'scan_time', 'ip_address']
    list_filter = ['scan_time']
    search_fields = ['FK_stone__PK_stone', 'FK_user__username']
    readonly_fields = ['scan_time']
    date_hierarchy = 'scan_time'
