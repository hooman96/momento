import React from "react";
import cn from "classnames";
import { Link } from "react-router-dom";
import styles from "./Offer.module.sass";

const Offer = ({ className }) => {
  const backgroundImage = "/images/pic.png";
  return (
    <div
      style={{
        backgroundImage: `url(${backgroundImage})`,
        backgroundPosition: "right 0px bottom -225px",
        backgroundSize: "50%",
        bottom: "0",
        boxShadow: "inset 0 0 0 2000px rgba(23, 24, 31, 0.5",

        backgroundRepeat: "repeat-x",
      }}
    >
      {/* <div className={cn(className, styles.section)}>
        <div className={cn("container", styles.container)}>
          <div
            style={{
              fontFamily: "TT Norms Bold",
              fontSize: "14px",
              color: "white",

              marginBottom: "16px",
              opacity: "0.8",
              textTransform: "uppercase",
              letterSpacing: "0.5px",
            }}
          >
            new Adventure
          </div>
          <h2
            className={cn("h2", styles.title)}
            style={{ fontFamily: "New Spirit", letterSpacing: "0.5px" }}
          >
            For a modern, busy, <br />&{" "}
            <span class={styles.gradient}>on-demand </span>world.
          </h2>
          <div className={styles.text}>
            Sign up with your email. We're a{" "}
            <span style={{ fontFamily: "TT Norms Bold" }}>
              private, members-only{" "}
            </span>
            community. 
            Beta version is coming soon.
          </div>
          {/*<Link className={cn("button", styles.button)} to='/download'>
            Start my adventure
          </Link>*/}
        {/* </div> */}
      {/* </div> */}
    </div>
  );
};

export default Offer;
