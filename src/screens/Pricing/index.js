import React from "react";
import styles from "./Pricing.module.sass";
import Plan from "./Plan";
import Comment from "./Comment";
import Faq from "./Faq";
import Testimonials from "../../components/Testimonials";
import Hero from "./Hero";
import Hero2 from "./Hero2";

const Pricing = () => {
  return (
    <>
    <Hero/>
      <Plan />
      {/* <Comment />
      <Faq />
      <Testimonials className="section-bg" /> */}
      <Hero2/>
    </>
  );
};

export default Pricing;



