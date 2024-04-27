import React from "react";
import cn from "classnames";
import { Link } from "react-router-dom";
import styles from "./Workouts.module.sass";
import Image from "../Image";
import ScrollParallax from "../ScrollParallax";

const items = [
  "Custom GPT with 24/7 support",
  "Choose from personalized plans",
  "No hidden fees, simple discounts",
  "Advanced security features",
  "Intuitive and clean design",
];

const Workouts = () => {
  return (
    <div className={styles.section}>
      <div className={cn("container", styles.container)}>
        <div className={styles.gallery}>
          <div className={styles.preview}>
            <Image
              srcSet='/images/content/cloud.jpg 2x'
              srcSetDark='/images/content/cloud.jpg 2x'
              src='/images/content/cloud.jpg'
              srcDark='/images/content/cloud.jpg'
              alt='Phones'
              style={{ height: "55%" }}
            />
          </div>
          {/* <ScrollParallax className={styles.preview} animateIn='fadeInUp'>
            <img
              srcSet='/images/content/jellybear.png 2x'
              src='/images/content/jellybear.png'
              alt='Bear'
            />
          </ScrollParallax>
          <ScrollParallax className={styles.preview} animateIn='fadeInUp'>
            <img
              srcSet='/images/content/lollipop.png 2x'
              src='/images/content/lollipop.png'
              alt='LoliPop'
            />
          </ScrollParallax>
        */}
        </div>
        <div className={styles.wrap}>
          <h2
            className={cn("h2", styles.title)}
            style={{
              fontFamily: "New Spirit",
              letterSpacing: "-0.5px",
            }}
          >
            View tiers. Get cost reduction. As easy as few clicks.
            <br />
          </h2>
          <div className={styles.info}>
            Less time managing, productive building, more savings & extra money for the business.
            <br />
          </div>
          <ul className={styles.list}>
            {items.map((x, index) => (
              <li className={styles.item} key={index}>
                {x}
              </li>
            ))}
          </ul>
          {/* <div className={styles.btns}>
            <Link className={cn("button", styles.button)} to='/pricing'>
              Choose Plan
            </Link>
            <button className={cn("button-stroke", styles.button)}>
              Request a demo
            </button>
          </div> */}
        </div>
      </div>
    </div>
  );
};

export default Workouts;
