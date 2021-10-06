import React from "react";
import { useHistory } from "react-router-dom";
import { useForm, ValidationError } from "@formspree/react";
import cn from "classnames";
import styles from "./Subscription.module.sass";
import Icon from "../Icon";

const Subscription = ({ className, placeholder }) => {
  let history = useHistory();
  const [state, handleSubmit] = useForm("xyylzezj");
  if (state.succeeded) {
    return <h3>Thanks for joining! We'll be in touch with our Beta link!</h3>;
  }

  // const [email, setEmail] = useState("");

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
