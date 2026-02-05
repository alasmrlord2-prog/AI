# شرح نظام Billing (الفوترة)

## كيف يعمل نظام Billing:

### 1. **Subscriptions (الاشتراكات)**
- كل Tenant لديه subscription plan (Basic, Professional, Enterprise)
- الاشتراك يتم تجديده تلقائياً كل شهر
- يتم حساب المبلغ حسب الخطة:
  - **Basic**: $29/شهر
  - **Professional**: $99/شهر  
  - **Enterprise**: $299/شهر

### 2. **Invoices (الفواتير)**
- يتم إنشاء فاتورة تلقائياً في بداية كل دورة اشتراك
- الفاتورة تحتوي على:
  - Subscription fee (رسوم الاشتراك)
  - Usage-based charges (رسوم حسب الاستخدام):
    - API calls فوق الحد المسموح
    - Storage فوق الحد المسموح
    - Additional users فوق الحد المسموح
- حالة الفاتورة:
  - **Pending**: في انتظار الدفع
  - **Paid**: تم الدفع
  - **Overdue**: متأخرة
  - **Cancelled**: ملغاة

### 3. **Payment Methods (طرق الدفع)**
- دعم عدة طرق دفع:
  - Credit/Debit Cards
  - Bank Transfer
  - PayPal
- يمكن إضافة عدة طرق دفع
- تعيين طريقة دفع افتراضية

### 4. **Billing Cycle (دورة الفوترة)**
```
1. بداية الدورة → إنشاء Invoice تلقائياً
2. إرسال Invoice للـ Tenant عبر Email
3. Tenant يدفع الفاتورة
4. تحديث حالة Invoice إلى "Paid"
5. تجديد Subscription للدورة القادمة
```

### 5. **Usage Tracking (تتبع الاستخدام)**
- يتم تتبع:
  - عدد API calls
  - Storage المستخدم
  - عدد Users
- إذا تجاوز Tenant الحدود → يتم فرض رسوم إضافية

### 6. **Revenue Tracking (تتبع الإيرادات)**
- عرض Total Revenue من جميع الفواتير المدفوعة
- عرض Pending Amount من الفواتير المعلقة
- رسوم بيانية للإيرادات والاتجاهات

## مثال على دورة فوترة:

```
Tenant: "Company ABC"
Plan: Professional ($99/month)
Start Date: 2024-01-01
End Date: 2024-01-31

Invoice #001:
- Subscription: $99
- Extra API calls (10,000): $50
- Extra Storage (100GB): $20
Total: $169

Status: Paid on 2024-01-05
```

## APIs المطلوبة في Backend:

```python
# إنشاء Invoice تلقائياً
POST /api/billing/invoices/generate
# دفع Invoice
POST /api/billing/invoices/{id}/pay
# تحديث Subscription
PUT /api/billing/subscriptions/{id}
# إضافة Payment Method
POST /api/billing/payment-methods
```

