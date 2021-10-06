import React from "react";
import cn from "classnames";
import { Link } from "react-router-dom";
import styles from "./Hero.module.sass";
import Image from "../../../components/Image";

import ScrollButton from "../../../components/ScrollButton";

import Subscription from "../../../components/Subscription";

import ScrollParallax from "../../../components/ScrollParallax";

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
            Seamless Gift Suggestions
          </div>
          <h1 className={cn("h1", styles.title)}>
            <span className={styles.gradient2}> Momento</span> influencers <br />
            <span className={styles.gradient}> coupons </span> <br />
          </h1>
          <div className={styles.text}>
            Get the best discouns from influencers to buy the gifts you love without thinking about it

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
        <div className={styles.gallery}>
          <ScrollParallax className={styles.preview} animateIn='fadeInUp'>
            <Image
              srcSet='/images/content/giftanim.gif 2x'
              srcSetDark='/images/content/giftanim.gif 2x'
              src='/images/content/giftanim.gif'
              srcDark='/images/content/giftanim.gif'
              alt='Bach'
            />
          </ScrollParallax>
          
          {/*
          	<ScrollParallax
            className={styles.preview}
            animateIn='fadeInUp'
            delay={900}
          >
            <img
              srcSet='/images/content/ball@2x.png 2x'
              src='/images/content/ball@2x.png'
              alt='Ball'
            />
          </ScrollParallax>
          <ScrollParallax
            className={styles.preview}
            animateIn='fadeInUp'
            delay={600}
          >
            <img
              srcSet='/images/content/bottle@2x.png 2x'
              src='/images/content/bottle@2x.png'
              alt='confetti'
            />
          </ScrollParallax>
          <ScrollParallax
            className={styles.preview}
            animateIn='fadeInUp'
            delay={1200}
          >
            <img
              srcSet='/images/content/wine.png 2x'
              src='/images/content/wine.png'
              alt='hand'
            />
          </ScrollParallax>
        */}
        </div>
      </div>
    </div>
  );
};

export default Hero;
