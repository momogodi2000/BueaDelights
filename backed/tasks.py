from celery import shared_task
from django.utils import timezone
from .models import Transaction
import logging

logger = logging.getLogger('payment')

@shared_task
def check_pending_transactions():
    """Check and update status of pending transactions"""
    pending_transactions = Transaction.objects.filter(status='pending')
    
    for transaction in pending_transactions:
        try:
            # Check if transaction is older than 30 minutes
            if timezone.now() - transaction.created_at > timezone.timedelta(minutes=30):
                transaction.status = 'failed'
                transaction.save()
                logger.warning(f"Transaction {transaction.id} timed out")
                continue
                
            # Implement your payment status check logic here
            # This would call your payment provider's API
            status = check_payment_status_with_provider(transaction)
            
            if status != transaction.status:
                transaction.status = status
                transaction.save()
                logger.info(f"Updated transaction {transaction.id} to {status}")
                
        except Exception as e:
            logger.error(f"Error checking transaction {transaction.id}: {str(e)}")

def check_payment_status_with_provider(transaction):
    """Implement your actual payment provider status check here"""
    # This would call your payment provider's API
    # Return 'completed', 'failed', or 'pending'
    return 'completed'  # Example