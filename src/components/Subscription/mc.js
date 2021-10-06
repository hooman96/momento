import React, { useState, useEffect } from "react";
import MailchimpSubscribe from "react-mailchimp-subscribe";
import cn from "classnames";
import styles from "./Subscription.module.sass";
import Icon from "../Icon";

const Subscription = ({
  className,
  placeholder,
  status,
  message,
  onValidated,
}) => {
  const [email, setEmail] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    email &&
      email.indexOf("@") > -1 &&
      onValidated({
        MERGE1: email,
      });
  };

  useEffect(() => {
    if (status === "success") clearFields();
  }, [status]);

  const clearFields = () => {
    setEmail("");
  };

  return (
    <>
      <form
        className={cn(styles.form, className)}
        action=''
        onSubmit={(e) => handleSubmit(e)}
      >
        {status === "sending" && (
          <div className='mc__alert mc__alert--sending'>sending...</div>
        )}
        {status === "error" && (
          <div
            className='mc__alert mc__alert--error'
            dangerouslySetInnerHTML={{ __html: message }}
          />
        )}
        {status === "success" && (
          <div
            className='mc__alert mc__alert--success'
            dangerouslySetInnerHTML={{ __html: message }}
          />
        )}
        {/* {status !== "success" ? (
  handleClick={() => alert()} */}
        <input
          className={styles.input}
          type='email'
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          name='email'
          placeholder={placeholder}
          required
        />

        <button className={styles.btn}>
          <Icon name='arrow-right' size='14' />
        </button>
      </form>
    </>
  );
};

export default Subscription;
