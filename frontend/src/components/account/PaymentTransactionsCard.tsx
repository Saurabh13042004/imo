import { usePaymentTransactions, useTransactionStatus } from '@/hooks/usePaymentTransactions';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CreditCard, Download, Filter, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useState } from 'react';
import { format } from 'date-fns';

const statusColors = {
  success: 'bg-green-100 text-green-700 border-green-200',
  pending: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  failed: 'bg-red-100 text-red-700 border-red-200',
  refunded: 'bg-blue-100 text-blue-700 border-blue-200',
};

const typeLabels = {
  subscription: 'Subscription',
  one_time: 'One-time',
  refund: 'Refund',
};

function TransactionRow({ transaction }: { transaction: any }) {
  // For pending transactions, poll status in real-time
  const paymentIntentId = transaction.stripe_payment_intent_id;
  const sessionId = transaction.stripe_session_id;
  
  const { data: statusData, isLoading: isCheckingStatus } = useTransactionStatus(
    paymentIntentId || undefined,
    sessionId || undefined
  );
  
  // Use live status if checking, otherwise use local status
  const displayStatus = statusData?.status || transaction.status;
  const isLiveUpdating = transaction.status === 'pending' && isCheckingStatus;

  return (
    <div className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors relative">
      {/* Live update indicator */}
      {isLiveUpdating && (
        <div className="absolute top-2 right-2 flex items-center gap-1">
          <RefreshCw className="h-3 w-3 animate-spin text-blue-500" />
          <span className="text-xs text-blue-600">Checking status...</span>
        </div>
      )}
      
      <div className="flex-1 space-y-1">
        <div className="flex items-center gap-2">
          <p className="font-medium">
            {typeLabels[transaction.type as keyof typeof typeLabels]}
          </p>
          <Badge className={statusColors[displayStatus as keyof typeof statusColors]}>
            {displayStatus.charAt(0).toUpperCase() + displayStatus.slice(1)}
          </Badge>
          {statusData && statusData.status !== transaction.status && (
            <span className="text-xs text-green-600 font-medium">✓ Updated</span>
          )}
        </div>
        <p className="text-sm text-muted-foreground">
          {transaction.transaction_id}
        </p>
        <p className="text-xs text-muted-foreground">
          {format(new Date(transaction.created_at), 'PPpp')}
        </p>
        
        {/* Show error if payment failed */}
        {statusData?.error && (
          <p className="text-xs text-red-600 font-medium mt-1">
            Error: {statusData.error}
          </p>
        )}
      </div>

      <div className="text-right space-y-1">
        <p className="font-semibold">
          {transaction.currency.toUpperCase()} ${parseFloat(transaction.amount).toFixed(2)}
        </p>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => {
            // Download receipt/details
            const dataStr = JSON.stringify(transaction, null, 2);
            const dataUri =
              'data:application/json;charset=utf-8,' +
              encodeURIComponent(dataStr);
            const exportFileDefaultName = `transaction-${transaction.transaction_id}.json`;
            const linkElement = document.createElement('a');
            linkElement.setAttribute('href', dataUri);
            linkElement.setAttribute('download', exportFileDefaultName);
            linkElement.click();
          }}
        >
          <Download className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}

export function PaymentTransactionsCard() {
  const { data: transactions = [], isLoading, error } = usePaymentTransactions();
  const [filterStatus, setFilterStatus] = useState<string | null>(null);

  const filteredTransactions = filterStatus
    ? transactions.filter((t) => t.status === filterStatus)
    : transactions;

  const totalSpent = transactions
    .filter((t) => t.status === 'success')
    .reduce((sum, t) => sum + parseFloat(t.amount), 0);

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Payment History</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-red-500">Failed to load payment transactions</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            <CardTitle>Payment History</CardTitle>
          </div>
          {transactions.length > 0 && (
            <div className="text-right">
              <p className="text-sm text-muted-foreground">Total Spent</p>
              <p className="text-lg font-semibold">${totalSpent.toFixed(2)}</p>
            </div>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Filters */}
        {transactions.length > 0 && (
          <div className="flex flex-wrap gap-2 border-b pb-4">
            <Button
              variant={filterStatus === null ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilterStatus(null)}
            >
              All ({transactions.length})
            </Button>
            {['success', 'pending', 'failed', 'refunded'].map((status) => {
              const count = transactions.filter((t) => t.status === status).length;
              if (count === 0) return null;
              return (
                <Button
                  key={status}
                  variant={filterStatus === status ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilterStatus(status)}
                >
                  {status.charAt(0).toUpperCase() + status.slice(1)} ({count})
                </Button>
              );
            })}
          </div>
        )}

        {/* Transactions List */}
        {isLoading ? (
          <div className="text-center py-8 text-muted-foreground">
            Loading transactions...
          </div>
        ) : filteredTransactions.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            {filterStatus
              ? `No ${filterStatus} transactions`
              : 'No payment transactions yet'}
          </div>
        ) : (
          <div className="space-y-3">
            {filteredTransactions.map((transaction) => (
              <TransactionRow key={transaction.id} transaction={transaction} />
            ))}
          </div>
        )}

        {/* Summary Stats */}
        {transactions.length > 0 && (
          <div className="mt-6 pt-4 border-t grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-muted-foreground uppercase">Total Transactions</p>
              <p className="text-2xl font-bold">{transactions.length}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground uppercase">Successful</p>
              <p className="text-2xl font-bold text-green-600">
                {transactions.filter((t) => t.status === 'success').length}
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
