import React from "react";
import cn from "classnames";
import styles from "./Steps.module.sass";
import ScrollParallax from "../../../components/ScrollParallax";

const items = [
  {
    title: "Discovery",
    // color: "#1A1B27",
    images: "/images/content/colorsearch.png",
    content:
      "Look on Momento home page for the best personalized deals",
  },
  {
    title: "Savings",
    // color: "#1A1B27",
    images: "/images/content/colorsale.png",
    content:
      "Get discount on trendy brands and influencers coupons",
  },
  {
    title: "Gift",
    // color: "#1A1B27",
    images: "/images/content/colorgift.png",
    content:
      "Purchase the gift you liked wether for someone or even yourself",
  },
  {
    title: "Repeat",
    // color: "#1A1B27",
    images: "/images/content/colorredo.png",
    content:
      "Once you try Momento, we hope that you come back for more",
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
            How it works:
            <br />
            Deals on Demand
          </h2>
          <div className={styles.info}>
            Explore and find the hidden deals from influencers
            <br /> <br />
            Momento will collect all the coupons from varity of sources like
            Instagram and TikTok in one unified place
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
