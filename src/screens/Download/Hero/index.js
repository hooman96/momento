import React from "react";
import cn from "classnames";
import styles from "./Hero.module.sass";
import Subscription from "../../../components/Subscription";
import Image from "../../../components/Image";

const Hero = () => {
  return (
    <div className={styles.hero}>
      <div className={cn("container", styles.container)}>
        <div className={styles.col}>
          <div className={styles.preview}>
            <Image
              srcSet='/images/content/register.gif 2x'
              srcSetDark='/images/content/register.gif'
              src='/images/content/register.gif'
              srcDark='/images/content/register.gif'
              alt='Download bg'
            />
          </div>
        </div>
        <div className={styles.col}>
          <div className={styles.wrap}>
            <div className={cn("stage", styles.stage)}>
              A new way to explore
            </div>
            <h1 className={cn("h1", styles.title)}>
              Sign Up
            </h1>
            <div className={styles.text}>
              No spam emails. version 1.0 will be announced.
            </div>
            <Subscription
              className={styles.subscription}
              placeholder='Enter your email'
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Hero;
