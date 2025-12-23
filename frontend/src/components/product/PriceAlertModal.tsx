import React, { useState } from 'react';
import { X, Bell } from 'lucide-react';
import toast from 'react-hot-toast';
import { usePriceAlert } from '../../hooks/usePriceAlert';
import { useAuth } from '../../hooks/useAuth';

interface PriceAlertModalProps {
  isOpen: boolean;
  onClose: () => void;
  product: {
    id: string;
    title: string;
    product_url: string;
    price: number;
  };
}

export const PriceAlertModal: React.FC<PriceAlertModalProps> = ({
  isOpen,
  onClose,
  product,
}) => {
  const { user } = useAuth();
  const { createAlert, hasExistingAlert } = usePriceAlert();

  const [targetPrice, setTargetPrice] = useState<string>('');
  const [email, setEmail] = useState<string>(user?.email || '');
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const existingAlert = hasExistingAlert(product.id);

  // Reset form when modal closes
  React.useEffect(() => {
    if (!isOpen) {
      setTargetPrice('');
      setEmail(user?.email || '');
      setAgreedToTerms(false);
      setErrors({});
    }
  }, [isOpen, user?.email]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    const price = parseFloat(targetPrice);
    if (!targetPrice || isNaN(price) || price <= 0) {
      newErrors.targetPrice = 'Please enter a valid price greater than 0';
    }

    if (price >= product.price) {
      newErrors.targetPrice = 'Target price must be lower than current price';
    }

    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!agreedToTerms) {
      newErrors.terms = 'You must agree to receive price alerts';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    createAlert.mutate(
      {
        product_id: product.id,
        product_name: product.title,
        product_url: product.product_url,
        target_price: parseFloat(targetPrice),
        current_price: product.price,
        currency: 'usd',
        email: !user ? email : undefined, // Only send email if not authenticated
      },
      {
        onSuccess: () => {
          toast.success('Price alert created! We\'ll notify you when the price drops.', {
            duration: 4000,
            position: 'top-center',
          });
          onClose();
        },
        onError: (error) => {
          const errorMessage = error instanceof Error ? error.message : 'Failed to create alert';
          
          if (errorMessage.includes('409') || errorMessage.includes('duplicate')) {
            toast.error('You already have an alert for this product', {
              duration: 4000,
              position: 'top-center',
            });
          } else {
            toast.error(errorMessage, {
              duration: 4000,
              position: 'top-center',
            });
          }
        },
      }
    );
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <Bell className="w-5 h-5 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">Price Alert</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Close modal"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Product Info */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600 mb-1">Product</p>
            <p className="font-medium text-gray-900 truncate">{product.title}</p>
            <p className="text-sm text-gray-600 mt-2">
              Current Price: <span className="font-semibold text-gray-900">${typeof product.price === 'number' ? product.price.toFixed(2) : parseFloat(product.price).toFixed(2)}</span>
            </p>
          </div>

          {/* Existing Alert Warning */}
          {existingAlert && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
              <p className="text-sm text-yellow-800">
                You already have an alert for this product. Create a new one to replace it.
              </p>
            </div>
          )}

          {/* Target Price */}
          <div>
            <label htmlFor="targetPrice" className="block text-sm font-medium text-gray-900 mb-1">
              Target Price *
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">$</span>
              <input
                id="targetPrice"
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                value={targetPrice}
                onChange={(e) => {
                  setTargetPrice(e.target.value);
                  if (errors.targetPrice) {
                    setErrors({ ...errors, targetPrice: '' });
                  }
                }}
                className={`w-full pl-7 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.targetPrice ? 'border-red-500' : 'border-gray-300'
                }`}
              />
            </div>
            {errors.targetPrice && (
              <p className="text-sm text-red-600 mt-1">{errors.targetPrice}</p>
            )}
          </div>

          {/* Email (only show if not authenticated) */}
          {!user && (
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-900 mb-1">
                Email Address *
              </label>
              <input
                id="email"
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (errors.email) {
                    setErrors({ ...errors, email: '' });
                  }
                }}
                className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.email ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.email && (
                <p className="text-sm text-red-600 mt-1">{errors.email}</p>
              )}
              <p className="text-xs text-gray-500 mt-1">
                We'll send you an email when the price drops below your target
              </p>
            </div>
          )}

          {/* Terms Agreement */}
          <div className="flex items-start gap-3 pt-2">
            <input
              id="terms"
              type="checkbox"
              checked={agreedToTerms}
              onChange={(e) => {
                setAgreedToTerms(e.target.checked);
                if (errors.terms) {
                  setErrors({ ...errors, terms: '' });
                }
              }}
              className="mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
            />
            <label htmlFor="terms" className="text-sm text-gray-600 cursor-pointer">
              I agree to receive price alert notifications via email when the price drops below my target
            </label>
          </div>
          {errors.terms && (
            <p className="text-sm text-red-600 -mt-2">{errors.terms}</p>
          )}

          {/* Helper Text */}
          <p className="text-xs text-gray-500 bg-blue-50 p-3 rounded-lg">
            💡 You'll receive an email notification when the price drops to your target amount. You can manage or cancel alerts anytime.
          </p>

          {/* Buttons */}
          <div className="flex gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors"
              disabled={createAlert.isPending}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createAlert.isPending}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:bg-blue-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {createAlert.isPending ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Bell className="w-4 h-4" />
                  Create Alert
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
