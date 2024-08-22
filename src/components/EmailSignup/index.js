import React, { useState } from 'react';

function EmailSignup() {
  const [email, setEmail] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      const response = await fetch('https://momento-six.vercel.app/api/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit email');
      }

      setIsSubmitted(true);
    } catch (error) {
      console.error('Error submitting email:', error);
      setError('Something went wrong. Please try again.');
    }
  };

  return (
    <div>
      {isSubmitted ? (
        <h2>Thanks for signing up!</h2>
      ) : (
        <form onSubmit={handleSubmit}>
          <label htmlFor="email">Enter your email:</label>
          <input 
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required 
          />
          <button type="submit">Sign Up</button>
          {error && <p>{error}</p>}
        </form>
      )}
    </div>
  );
}

export default EmailSignup;