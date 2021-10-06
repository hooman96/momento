import React, { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import cn from "classnames";
import styles from "./Footer.module.sass";
import Subscription from "../Subscription";
import Theme from "../Theme";
import Icon from "../Icon";
import Image from "../Image";


const menu = [
  {
    title: "About",
    url: "/",
  },
  // {
  //   title: "Pricing",
  //   url: "/pricing",
  // },
  // {
  //   title: "Class",
  //   url: "/class01",
  // },
  // {
  //   title: "Features",
  //   url: "/",
  // },
  {
    title: "Download",
    url: "/download",
  },
];

const socials = [
  {
    title: "facebook",
    size: "16",
    url: "https://www.facebook.com/",
  },
  {
    title: "twitter",
    size: "18",
    url: "https://twitter.com/",
  },
  {
    title: "instagram",
    size: "16",
    url: "https://www.instagram.com/",
  },
];

const Footer = () => {
  const [visible, setVisible] = useState(false);

  return (
    <footer className={styles.footer}>
      <div className={styles.body}>
        <div className={cn("container", styles.container)}>
          <div className={styles.col}>
            <div className={styles.box}>
              <Link className={styles.logo} to='/'>
                {/* <Image
                  className={styles.pic}
                  src="/images/logo-dark.svg"
                  srcDark="/images/logo-light.svg"
                  alt="Bach App"
                /> */}
                {/*<h1 style={{ fontFamily: "New Spirit", color: "#787983" }}>
                  M
                </h1>*/}
              </Link>
              <Theme className={styles.theme} />
            </div>
            <div className={cn(styles.item, { [styles.active]: visible })}>
              <div
                className={styles.category}
                onClick={() => setVisible(!visible)}
              >
                Pages
                <Icon name='arrow-bottom' size='9' />
              </div>
              <div className={styles.menu}>
                {menu.map((x, index) => (
                  <NavLink
                    className={styles.link}
                    activeClassName={styles.active}
                    to={x.url}
                    key={index}
                  >
                    {x.title}
                  </NavLink>
                ))}
              </div>
            </div>
          </div>
          <div className={styles.col}>
            <div className={styles.category}>contact</div>
            <div className={styles.info}>
              <p>hooistheman@gmail.com</p>
              <p>+1 (407) - 984 - 4745</p>
            </div>
          </div>
          <div className={styles.col}>
            <div className={styles.category}>our launch</div>
            <div className={styles.info}>
              Subscribe our email list to get free access to our app and launch
              parties!
            </div>
            <Subscription
              className={styles.subscription}
              placeholder='Enter your email'
            />
          </div>
        </div>
      </div>
      <div className={styles.foot}>
        <div className={cn("container", styles.container)}>
          <div className={styles.copyright}>
            Copyright © 2021 Momento LLC. All rights reserved
          </div>
          <div className={styles.socials}>
            {socials.map((x, index) => (
              <a
                className={styles.social}
                href={x.url}
                target='_blank'
                rel='noopener noreferrer'
                key={index}
              >
                <Icon name={x.title} size={x.size} />
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
