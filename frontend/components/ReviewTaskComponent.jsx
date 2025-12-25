// ReviewTaskComponent.jsx
// Ready-to-use React component for async review fetching with polling

import React, { useState, useRef, useEffect } from 'react';

const ReviewTaskComponent = () => {
  const [productName, setProductName] = useState('');
  const [brand, setBrand] = useState('');
  const [taskId, setTaskId] = useState(null);
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);
  const pollIntervalRef = useRef(null);
  const timeIntervalRef = useRef(null);
  const startTimeRef = useRef(null);

  // Poll for task status
  const pollTaskStatus = async (currentTaskId) => {
    try {
      const response = await fetch(
        `/api/v1/reviews/community/status/${currentTaskId}`
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      setStatus(data.status);

      if (data.status === 'SUCCESS') {
        setResult(data.result);
        setIsLoading(false);
        clearInterval(pollIntervalRef.current);
        clearInterval(timeIntervalRef.current);
      } else if (data.status === 'FAILURE') {
        setError(data.error || 'Task failed');
        setIsLoading(false);
        clearInterval(pollIntervalRef.current);
        clearInterval(timeIntervalRef.current);
      }
      // Otherwise continue polling
    } catch (err) {
      console.error('Polling error:', err);
      // Retry on error
      if (isLoading) {
        setTimeout(
          () => pollTaskStatus(currentTaskId),
          5000
        );
      }
    }
  };

  // Submit review task
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!productName.trim()) {
      setError('Please enter a product name');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);
    setStatus('PENDING');
    setElapsedTime(0);
    startTimeRef.current = Date.now();

    try {
      const response = await fetch('/api/v1/reviews/community', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_name: productName.trim(),
          brand: brand.trim() || undefined
        })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || `HTTP ${response.status}`);
      }

      const data = await response.json();

      if (data.task_id) {
        setTaskId(data.task_id);

        // Start time counter
        timeIntervalRef.current = setInterval(() => {
          setElapsedTime(Math.floor((Date.now() - startTimeRef.current) / 1000));
        }, 100);

        // Start polling
        pollTaskStatus(data.task_id);
        pollIntervalRef.current = setInterval(
          () => pollTaskStatus(data.task_id),
          2000
        );
      } else {
        throw new Error(data.detail || 'Failed to queue task');
      }
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearInterval(pollIntervalRef.current);
      clearInterval(timeIntervalRef.current);
    };
  }, []);

  const getStatusIcon = () => {
    switch (status) {
      case 'PENDING':
        return '⏳';
      case 'STARTED':
        return '🔄';
      case 'SUCCESS':
        return '✅';
      case 'FAILURE':
        return '❌';
      default:
        return '';
    }
  };

  const getStatusMessage = () => {
    switch (status) {
      case 'PENDING':
        return 'Waiting in queue...';
      case 'STARTED':
        return 'Processing reviews...';
      case 'SUCCESS':
        return 'Reviews loaded!';
      case 'FAILURE':
        return 'Failed to fetch reviews';
      default:
        return '';
    }
  };

  return (
    <div className="review-task-component" style={styles.container}>
      <h2 style={styles.title}>📊 Review Analyzer</h2>

      {/* Form */}
      <form onSubmit={handleSubmit} style={styles.form}>
        <div style={styles.formGroup}>
          <label style={styles.label}>Product Name *</label>
          <input
            type="text"
            value={productName}
            onChange={(e) => setProductName(e.target.value)}
            placeholder="e.g., iPhone 15 Pro, Samsung TV..."
            disabled={isLoading}
            style={styles.input}
          />
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>Brand (Optional)</label>
          <input
            type="text"
            value={brand}
            onChange={(e) => setBrand(e.target.value)}
            placeholder="e.g., Apple, Samsung..."
            disabled={isLoading}
            style={styles.input}
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          style={{
            ...styles.button,
            opacity: isLoading ? 0.6 : 1,
            cursor: isLoading ? 'not-allowed' : 'pointer'
          }}
        >
          {isLoading ? 'Loading...' : 'Get Reviews'}
        </button>
      </form>

      {/* Status */}
      {status && (
        <div style={styles.statusContainer}>
          <span style={styles.statusIcon}>{getStatusIcon()}</span>
          <span style={styles.statusMessage}>{getStatusMessage()}</span>
          {isLoading && (
            <span style={styles.elapsedTime}>
              ({elapsedTime}s)
            </span>
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={styles.error}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Task ID */}
      {taskId && (
        <div style={styles.taskInfo}>
          <small>Task ID: <code>{taskId}</code></small>
        </div>
      )}

      {/* Results */}
      {result && (
        <div style={styles.resultsContainer}>
          <h3 style={styles.resultsTitle}>{result.product_name}</h3>

          {/* Summary Stats */}
          <div style={styles.summaryStats}>
            <div style={styles.stat}>
              <span style={styles.statLabel}>Total Reviews</span>
              <span style={styles.statValue}>{result.total_found || result.reviews?.length || 0}</span>
            </div>

            {result.summary?.average_rating && (
              <div style={styles.stat}>
                <span style={styles.statLabel}>Avg Rating</span>
                <span style={styles.statValue}>
                  {result.summary.average_rating.toFixed(1)} ⭐
                </span>
              </div>
            )}

            {result.summary?.overall_sentiment && (
              <div style={styles.stat}>
                <span style={styles.statLabel}>Sentiment</span>
                <span style={styles.statValue}>{result.summary.overall_sentiment}</span>
              </div>
            )}
          </div>

          {/* Common Praises */}
          {result.summary?.common_praises && result.summary.common_praises.length > 0 && (
            <div style={styles.section}>
              <h4 style={styles.sectionTitle}>✨ Common Praises</h4>
              <ul style={styles.list}>
                {result.summary.common_praises.map((praise, i) => (
                  <li key={i} style={styles.listItem}>
                    {praise}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Common Complaints */}
          {result.summary?.common_complaints && result.summary.common_complaints.length > 0 && (
            <div style={styles.section}>
              <h4 style={styles.sectionTitle}>⚠️ Common Complaints</h4>
              <ul style={styles.list}>
                {result.summary.common_complaints.map((complaint, i) => (
                  <li key={i} style={styles.listItem}>
                    {complaint}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Individual Reviews */}
          {result.reviews && result.reviews.length > 0 && (
            <div style={styles.section}>
              <h4 style={styles.sectionTitle}>
                📝 Reviews ({result.reviews.length})
              </h4>
              <div style={styles.reviewsList}>
                {result.reviews.slice(0, 10).map((review, i) => (
                  <div key={i} style={styles.reviewItem}>
                    <div style={styles.reviewHeader}>
                      <strong>{review.reviewer_name || 'Anonymous'}</strong>
                      {review.rating && (
                        <span style={styles.reviewRating}>
                          {'⭐'.repeat(Math.round(review.rating))}
                        </span>
                      )}
                    </div>
                    <p style={styles.reviewText}>{review.text}</p>
                    {review.date && (
                      <small style={styles.reviewDate}>{review.date}</small>
                    )}
                  </div>
                ))}
              </div>
              {result.reviews.length > 10 && (
                <p style={styles.moreReviews}>
                  ... and {result.reviews.length - 10} more reviews
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '800px',
    margin: '20px auto',
    padding: '20px',
    backgroundColor: '#f9f9f9',
    borderRadius: '8px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    fontFamily: 'system-ui, -apple-system, sans-serif'
  },
  title: {
    color: '#333',
    marginBottom: '20px',
    textAlign: 'center'
  },
  form: {
    marginBottom: '20px'
  },
  formGroup: {
    marginBottom: '15px'
  },
  label: {
    display: 'block',
    marginBottom: '5px',
    fontWeight: 'bold',
    color: '#555'
  },
  input: {
    width: '100%',
    padding: '10px',
    borderRadius: '4px',
    border: '1px solid #ddd',
    fontSize: '14px',
    boxSizing: 'border-box',
    fontFamily: 'inherit'
  },
  button: {
    width: '100%',
    padding: '12px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    fontWeight: 'bold',
    cursor: 'pointer',
    transition: 'background-color 0.3s'
  },
  statusContainer: {
    padding: '12px',
    backgroundColor: '#e7f3ff',
    borderLeft: '4px solid #007bff',
    borderRadius: '4px',
    marginBottom: '15px',
    display: 'flex',
    alignItems: 'center',
    gap: '10px'
  },
  statusIcon: {
    fontSize: '20px'
  },
  statusMessage: {
    color: '#004085'
  },
  elapsedTime: {
    marginLeft: 'auto',
    color: '#666',
    fontSize: '12px'
  },
  error: {
    padding: '12px',
    backgroundColor: '#f8d7da',
    border: '1px solid #f5c6cb',
    borderRadius: '4px',
    color: '#721c24',
    marginBottom: '15px'
  },
  taskInfo: {
    padding: '10px',
    backgroundColor: '#f0f0f0',
    borderRadius: '4px',
    marginBottom: '15px',
    fontSize: '12px'
  },
  resultsContainer: {
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    border: '1px solid #e0e0e0'
  },
  resultsTitle: {
    color: '#333',
    borderBottom: '2px solid #007bff',
    paddingBottom: '10px',
    marginBottom: '20px'
  },
  summaryStats: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '15px',
    marginBottom: '20px'
  },
  stat: {
    backgroundColor: '#f5f5f5',
    padding: '15px',
    borderRadius: '4px',
    textAlign: 'center'
  },
  statLabel: {
    display: 'block',
    fontSize: '12px',
    color: '#666',
    marginBottom: '5px'
  },
  statValue: {
    display: 'block',
    fontSize: '18px',
    fontWeight: 'bold',
    color: '#007bff'
  },
  section: {
    marginBottom: '20px'
  },
  sectionTitle: {
    color: '#333',
    borderBottom: '1px solid #ddd',
    paddingBottom: '10px',
    marginBottom: '15px'
  },
  list: {
    listStyle: 'none',
    padding: 0,
    margin: 0
  },
  listItem: {
    padding: '8px 0',
    color: '#555',
    borderBottom: '1px solid #f0f0f0'
  },
  reviewsList: {
    maxHeight: '500px',
    overflowY: 'auto'
  },
  reviewItem: {
    padding: '15px',
    backgroundColor: '#f9f9f9',
    borderRadius: '4px',
    marginBottom: '10px',
    borderLeft: '4px solid #007bff'
  },
  reviewHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '10px'
  },
  reviewRating: {
    color: '#ffc107'
  },
  reviewText: {
    margin: '10px 0',
    color: '#555',
    lineHeight: '1.5'
  },
  reviewDate: {
    color: '#999'
  },
  moreReviews: {
    textAlign: 'center',
    color: '#666',
    fontStyle: 'italic',
    marginTop: '15px'
  }
};

export default ReviewTaskComponent;
