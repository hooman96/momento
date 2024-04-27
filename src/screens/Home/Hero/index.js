import React from "react";
import cn from "classnames";
import { Link } from "react-router-dom";
import styles from "./Hero.module.sass";
import Image from "../../../components/Image";

import ScrollButton from "../../../components/ScrollButton";

import Subscription from "../../../components/Subscription";

import ScrollParallax from "../../../components/ScrollParallax";

import EmailSignup from '../../../components/EmailSignup'; // Import  the email signup

const Hero = ({ scrollToRef }) => {
  return (
    <div className={styles.hero}>
      <div className={cn("container", styles.container)}>
        <ScrollParallax className={styles.wrap}>
          <div
            style={{
              fontFamily: "TT Norms Bold",
              fontSize: "14px",

              marginBottom: "16px",
              opacity: "0.8",
              textTransform: "uppercase",
              letterSpacing: "0.5px",
            }}
          >
            Seamless Migration Platform
          </div>
          <h1 className={cn("h1", styles.title)}>
            <span className={styles.gradient2}> Momento AI</span> Cloud Mapping <br />
            <span className={styles.gradient}> Interoperability </span> <br />
          </h1>
          <div className={styles.text}>
            Get the connectivity among AWS, GCP and Azure without any hassles. Sign up to get the latest info

            {/* We are an{" "} 
            <strong>
              invite-only community for dating and making friends{" "}
            </strong>
            through shared experiences you schedule.
          	*/}
          </div>
          <Subscription
            className={styles.subscription}
            placeholder='Enter your email'
          />

          {/* <ScrollParallax className={styles.subscription}>
            <div className={styles.signup}>
                <EmailSignup />
            </div>
         </ScrollParallax> */}
          <div className={styles.btns}>
            {/* <Link
              style={{ backgroundColor: "black" }}
              className={cn("button", styles.button)}
              to='/download'
            >
              Sign up for Access
            </Link> */}

            {/* <Link
              className={cn("button-stroke", styles.button)}
              to='/class02-details'
            >
              Learn more
            </Link> */}
          </div>
        </ScrollParallax>
        <ScrollButton
          onScroll={() =>
            scrollToRef.current.scrollIntoView({ behavior: "smooth" })
          }
          className={styles.scroll}
        />
      </div>
    </div>
  );
};

export default Hero;
