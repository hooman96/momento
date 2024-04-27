import React from "react";
import cn from "classnames";
import styles from "./Steps.module.sass";
import ScrollParallax from "../../../components/ScrollParallax";

const items = [
  {
    title: "Discovery Plan",
    // color: "#1A1B27",
    images: "/images/content/colorsearch.png",
    content:
      "Look on the personalized email for instruction",
  },
  {
    title: "Savings",
    // color: "#1A1B27",
    images: "/images/content/colorsale.png",
    content:
      "Get discount on our tiers based on the infrastructure need",
  },
  {
    title: "Promotion",
    // color: "#1A1B27",
    images: "/images/content/colorgift.png",
    content:
      "Promotions will be given to customers with on going subscription",
  },
  {
    title: "Repeat",
    // color: "#1A1B27",
    images: "/images/content/colorredo.png",
    content:
      "Stay on the plan where most benefits make sense to you",
  },
];

const Steps = ({ scrollToRef }) => {
  return (
    <div className={cn("section", styles.section)} ref={scrollToRef}>
      <div className={cn("container", styles.container)}>
        <div className={styles.head}>
          <h2
            className={cn("h2", styles.title)}
            style={{ fontFamily: "New Spirit" }}
          >
            How it is done:
            <br />
            Momento CLI
          </h2>
          <div className={styles.info}>
            Explore to find the right infrastructure based on the system design
            <br /> <br />
            Momento will collect all cloud accounts and give the best personalized suggestions
          </div>
        </div>
        <div className={styles.list}>
          {items.map((x, index) => (
            <ScrollParallax className={styles.item} key={index}>
              <div
                className={styles.preview}
                style={{ backgroundColor: x.color }}
              >
                <img src={x.images} alt={`Step ${index}`} />
              </div>
              <div className={styles.number}>Step {index + 1}</div>
              <div className={styles.subtitle}>{x.title}</div>
              <div className={styles.content}>{x.content}</div>
            </ScrollParallax>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Steps;
