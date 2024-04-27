import React, { useState } from 'react';

function EmailSignup() {
    const [email, setEmail] = useState('');
    const [isSubmitted, setIsSubmitted] = useState(false);
  
    const handleSubmit = (event) => {
      event.preventDefault(); 
      // Handle email submission logic here (e.g., send to a server)
      console.log('Email submitted:', email); 
      setIsSubmitted(true);
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
          </form>
        )}
      </div>
    );
  }
  
  export default EmailSignup;