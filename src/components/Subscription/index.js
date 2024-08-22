import React, { useState } from 'react';
// import { useHistory } from "react-router-dom";
import { useForm, ValidationError } from "@formspree/react";
import cn from "classnames";
import styles from "./Subscription.module.sass";
import Icon from "../Icon";

const Subscription = ({ className, placeholder }) => {
  // let history = useHistory();

  const [email, setEmail] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState(null);

  const [state, _] = useForm("xyylzezj");
  if (state.succeeded) {
    return <h3>Thanks for joining! We'll be in touch with our Beta link!</h3>;
  }
  
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
    <form className={cn(styles.form, className)} onSubmit={handleSubmit}>
      <input
        className={styles.input}
        id='email'
        type='email'
        name='email'
        placeholder={placeholder}
        required
      />
      <ValidationError prefix='Email' field='email' errors={state.errors} />

      <ValidationError prefix='Message' field='message' errors={state.errors} />
      <button type='submit' className={styles.btn} disabled={state.submitting}>
        <Icon name='arrow-right' size='16' />
      </button>
    </form>
  );
};

export default Subscription;
