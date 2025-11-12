# Fee Receipt Generation Feature - Documentation

## Overview
This document describes the enhanced fee receipt generation system for the College ERP. The system now generates comprehensive fee payment receipts with student PRN (Permanent Roll Number), admission number, and complete payment details.

## Features Implemented

### 1. **Enhanced Receipt Display**
- **Student Information Section**
  - Student Full Name
  - PRN (Permanent Roll Number) - Roll Number displayed prominently
  - Admission Number
  - Department
  - Current Class
  - Academic Year

- **Fee Details Section**
  - Fee Type (Tuition, Library, Lab, Exam, etc.)
  - Academic Year
  - Semester
  - Due Date
  - Fee Amount

- **Payment Details Section**
  - Payment Method (Online, Bank Transfer, Cheque, Cash, etc.)
  - Amount Paid
  - Payment Status (PAID/PARTIAL/PENDING)
  - Transaction ID
  - Payment Date & Time
  - Reference Number (for cheque/DD/etc.)
  - Remarks (if any)

### 2. **Receipt Generation & Download**
- **Web-based Receipt View**: Display receipt in browser with professional formatting
- **Print Functionality**: Browser print option for hard copies
- **PDF Download**: Direct PDF download capability (when weasyprint is installed)

### 3. **Automatic Receipt Creation**
- Receipt is automatically generated upon successful payment
- Receipt number format: `RCP-{fee_id:05d}-{payment_date}`
- Each receipt has unique Transaction ID and Receipt Number

## Database Structure

### Updated Models
The following models were used (no migrations needed):

```python
# Fee Model
class Fee(models.Model):
    student = ForeignKey(User)
    fee_type = CharField()  # tuition, library, lab, exam, development, other
    amount = DecimalField()
    due_date = DateField()
    payment_status = CharField()  # pending, paid, overdue, partial
    payment_date = DateField(null=True)
    payment_method = CharField()
    transaction_id = CharField()
    academic_year = CharField()
    semester = IntegerField()

# Transaction Model
class Transaction(models.Model):
    fee = ForeignKey(Fee)
    payment_method = ForeignKey(PaymentMethod)
    amount = DecimalField()
    status = CharField()  # pending, completed, failed, cancelled, refunded
    transaction_id = CharField(unique=True)
    reference_number = CharField()  # Cheque/DD number
    completed_at = DateTimeField()

# PaymentMethod Model
class PaymentMethod(models.Model):
    name = CharField()
    method_type = CharField()  # online, bank_transfer, cheque, cash, demand_draft
    bank_name = CharField()
    account_number = CharField()
    ifsc_code = CharField()
```

## File Structure

### Backend Files Modified:
1. **`students/views.py`**
   - Updated `fee_receipt()` view to include transaction details and PRN
   - Added `download_fee_receipt()` view for PDF generation

2. **`students/urls.py`**
   - Added URL route: `fees/<int:fee_id>/download/` for PDF download

### Frontend Files Modified:
1. **`templates/students/fee_receipt.html`**
   - Enhanced with PRN and admission number display
   - Improved payment details table
   - Added PDF download button
   - Better styling and print-friendly CSS

2. **`templates/students/fees.html`**
   - Updated to support HTML messages with receipt links
   - Receipt button already present for paid fees

## Usage Guide

### For Students:

#### Viewing a Receipt:
1. Navigate to **My Fees** page
2. In the **Paid Fees** section, click the **📄 Receipt** button
3. Receipt will open in a new tab with all payment details

#### Downloading Receipt as PDF:
1. Open the receipt page
2. Click **📥 Download PDF** button
3. PDF will be downloaded with filename: `Receipt_RCP-{id}-{date}.pdf`

#### Printing Receipt:
1. Open the receipt page
2. Click **🖨️ Print Receipt** button
3. Use browser print dialog to save as PDF or print

### Making a Payment:
1. Go to **My Fees** page
2. Click **💳 Pay Now** button on pending fee
3. Enter payment amount (can be full or partial)
4. Select payment method
5. If payment method is cheque/DD, enter reference number
6. Click **Process Payment**
7. Success message will show with **Download Receipt** link
8. Click link to view/download receipt immediately

## API Response Examples

### Receipt Data Structure:
```python
{
    'student': {
        'name': 'John Doe',
        'roll_number': 'PRN123456',
        'admission_number': 'ADM2023001',
        'department': 'Computer Science',
        'class': 'B.Tech CS - 2nd Sem - A'
    },
    'fee': {
        'fee_type': 'Tuition Fee',
        'amount': '50000.00',
        'academic_year': '2023-2024',
        'semester': 2,
        'due_date': '2023-08-31',
        'payment_date': '2023-08-25',
        'payment_status': 'paid'
    },
    'transaction': {
        'transaction_id': 'TXN-ABC123DEF456',
        'payment_method': 'Online Payment',
        'amount': '50000.00',
        'reference_number': 'UPI-TXN123',
        'completed_at': '2023-08-25 14:30:00'
    },
    'receipt_number': 'RCP-00001-25082023'
}
```

## Installation & Setup

### Basic Setup (No PDF Support):
The system works out of the box. No additional installation required.

### Enhanced Setup (With PDF Support):
To enable PDF download functionality:

```bash
pip install weasyprint
```

On Ubuntu/Debian:
```bash
sudo apt-get install libffi-dev libcairo2 libcairo2-dev libpango-1.0-0 libpango-cairo-1.0-0 libgdk-pixbuf2.0-0
pip install weasyprint
```

On macOS:
```bash
brew install cairo libffi
pip install weasyprint
```

## Security Features

1. **Authentication**: Only logged-in students can access receipts
2. **Authorization**: Students can only view their own receipts
3. **Data Validation**: All inputs are validated before processing
4. **Transaction Safety**: Transactions are marked as completed only after validation

## Customization

### Customize Receipt Header:
Edit `templates/students/fee_receipt.html` line 24-32:
```html
<h2 class="mb-1">
    <i class="bi bi-mortarboard-fill text-primary"></i>
    College Name
</h2>
<p class="text-muted mb-1">Address: Your College Address</p>
<p class="text-muted mb-1">Phone: +91-XXXXXXXXXX | Email: college@example.com</p>
```

### Customize Receipt Footer:
Edit lines 138-148 for footer information

### Change Receipt Format:
To create custom receipt templates, duplicate `fee_receipt.html` and modify as needed.

## Troubleshooting

### Issue: Receipt Not Loading
**Solution**: Ensure fee payment_date is set. Check database for null payment_date values.

### Issue: PDF Download Not Working
**Solution**: Install weasyprint: `pip install weasyprint`

### Issue: Transaction ID Not Showing
**Solution**: Verify transaction record exists in database with status='completed'

### Issue: PRN Not Displaying
**Solution**: Check student profile has roll_number set in database

## Future Enhancements

1. **Receipt Templates**: Multiple receipt styles/themes
2. **Bulk Receipts**: Download multiple receipts at once
3. **Email Receipts**: Auto-send receipt via email after payment
4. **Receipt History**: Archive and search past receipts
5. **Receipt Verification**: QR code for verification
6. **Multi-language**: Receipts in multiple languages
7. **Custom Watermarks**: Add institution watermarks to PDFs

## Testing

### Manual Testing Steps:

1. **Create Test Student**: Add student with roll_number and admission_number
2. **Create Test Fee**: Add fee record for student
3. **Process Payment**: Submit payment through fees page
4. **View Receipt**: Check receipt displays all correct information
5. **Download PDF**: Test PDF generation (if weasyprint installed)
6. **Print Test**: Test print functionality

## Support

For issues or feature requests, contact the system administrator or file a bug report with:
- Student ID
- Fee ID
- Payment Date
- Error message (if any)

---

**Last Updated**: November 12, 2025
**Version**: 1.0
