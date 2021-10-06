import React, { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import cn from "classnames";
import styles from "./Header.module.sass";
import DropdownMenu from "./DropdownMenu";
import Icon from "../Icon";

const navLinks = [
  {
    title: "Features",
    url: "/features",
  },
  // {
  //   title: "Pricing",
  //   url: "/pricing",
  // },
  {
    title: "Download",
    url: "/download",
  },
  {
    title: "Dates",
    content: {
      menu: [
        {
          title: "Program Videos",
          url: "/class01",
          image: "/images/menu-video.svg",
        },
        {
          title: "Premium Class",
          url: "/class02",
          image: "/images/menu-class.svg",
        },
      ],
      links: [
        {
          title: "Sweet and Tone",
          url: "/class01-details",
          image: "/images/content/header-pic-1.png",
          image2x: "/images/content/header-pic-1@2x.png",
          category: "black",
          categoryText: "featured class",
          avatar: "/images/content/avatar-1.png",
          trainer: "Zack Beier",
          content:
            "Sweet and Tone is a seven-day bodyweight training program designed to boost your strength and endurance over the course of a week.",
          level: "green",
          levelText: "beginner",
        },
        {
          title: "Sweet and Tone",
          url: "/class01-details",
          image: "/images/content/header-pic-2.png",
          image2x: "/images/content/header-pic-2@2x.png",
          category: "green",
          categoryText: "yoga",
          avatar: "/images/content/avatar-2.png",
          trainer: "Zack Beier",
        },
        {
          title: "Sweet and Tone",
          url: "/class01-details",
          image: "/images/content/header-pic-3.png",
          image2x: "/images/content/header-pic-3@2x.png",
          category: "purple",
          categoryText: "mindfulness",
          avatar: "/images/content/avatar-3.png",
          trainer: "Zack Beier",
        },
        {
          title: "Sweet and Tone",
          url: "/class01-details",
          image: "/images/content/header-pic-4.png",
          image2x: "/images/content/header-pic-4@2x.png",
          category: "red",
          categoryText: "fitness",
          avatar: "/images/content/avatar-4.png",
          trainer: "Zack Beier",
        },
      ],
      trainer: [
        {
          title: "Boyd Reinger",
          avatar: "/images/content/avatar-1.png",
          type: "Personal trainer",
        },
        {
          title: "Randal Jacobson",
          avatar: "/images/content/avatar-2.png",
          type: "Personal trainer",
        },
        {
          title: "Dwight Schamberger",
          avatar: "/images/content/avatar-3.png",
          type: "Personal trainer",
        },
        {
          title: "Omari Gulgowski",
          avatar: "/images/content/avatar-4.png",
          type: "Personal trainer",
        },
      ],
    },
  },
  // {
  //   title: "Lifestyle",
  //   url: "/lifestyle",
  // },
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

const contact = [
  {
    title: "Montanachester",
    content: "06787 Block Estates",
  },
  {
    title: "Lake Gene",
    content: "167 Emard River",
  },
  {
    title: "North Hassiefort",
    content: "032 Leonora Spurs",
  },
];

const Headers = () => {
  const [visibleNav, setVisibleNav] = useState(false);

  return (
    <header
      style={{
        position: "relative",
        zIndex: "10",
        // background: "#17181F",
        padding: "32px 0",
      }}
    >
      <div className={cn("container", styles.container)}>
        <Link
          className={styles.logo}
          to='/'
          onClick={() => setVisibleNav(false)}
        >
          <img
            style={{ height: "28px", width: "88px" }}
            src='/images/Logo.svg'
            alt='Logo'
          />
        </Link>
        <div className={cn(styles.wrap)}>
          {/* <nav className={styles.nav}>
            {navLinks.map((x, index) =>
              x.content ? (
                <DropdownMenu
                  className={styles.group}
                  item={x}
                  key={index}
                  setValue={setVisibleNav}
                />
              ) : (
                <NavLink
                  className={styles.link}
                  activeClassName={styles.active}
                  to={x.url}
                  key={index}
                  onClick={() => setVisibleNav(false)}
                >
                  {x.title}
                </NavLink>
              )
            )}
          </nav> */}
          <div className={styles.details}>
            {/* <div className={styles.contact}>
              {contact.map((x, index) => (
                <div className={styles.element} key={index}>
                  <div className={styles.category}>{x.title}</div>
                  <div className={styles.text}>{x.content}</div>
                </div>
              ))}
            </div> */}
            {/* <div className={styles.socials}>
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
            </div> */}
            <Link
              style={{
                fontFamily: "TT Norms Bold",
                letterSpacing: "0.5px",
              }}
              className={cn("button-stroke button-small", styles.button)}
              to='/'
            >
              Join our waitlist!
            </Link>
          </div>
        </div>
        <Link
          style={{
            fontFamily: "TT Norms Bold",
            letterSpacing: "0.5px",
          }}
          className={cn("button-stroke button-small", styles.button)}
          to='/'
        >
          Join our waitlist!
        </Link>
        {/* <button
          className={cn(styles.burger, { [styles.active]: visibleNav })}
          onClick={() => setVisibleNav(!visibleNav)}
        ></button> */}
      </div>
    </header>
  );
};

export default Headers;
