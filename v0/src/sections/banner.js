import React from 'react';
import { Box, Container, Grid, Button, Input, Heading, Text } from 'theme-ui';
import { useForm, ValidationError } from '@formspree/react';
import Image from 'components/image';

import img1 from 'assets/partner-1-1.png';
import img2 from 'assets/partner-1-2.png';
import img3 from 'assets/partner-1-3.png';

import bannerImg from 'assets/giftanim.gif';

const Banner = () => {
  const [state, handleSubmit] = useForm("xyylzezj");
  if (state.succeeded) {
      return <h1>Thanks!</h1>;
  }
  return (
    <Box sx={styles.banner} id="banner">
      <Container sx={styles.container}>
        <Grid sx={styles.grid}>
          <Box sx={styles.content}>
            <Heading as="h3">
            Weclome to Momento
            </Heading>
            <Text as="p">
            Get the best deals from influencers to buy the gifts you love
            </Text>
            <Text as="p">
            Suggest the right gifts to the people you care about without thinking about it 
            </Text>
            <form onSubmit={handleSubmit}>
            <Box as="form" sx={styles.form}>
           
              <Box as="label" htmlFor="subscribe" variant="styles.srOnly">
              
              </Box>
              <Input
                id="email"
                type="email" 
                name="email"
                htmlFor="email"
                placeholder="Sign up for Early Access"
                sx={styles.form.input}
              />
               <ValidationError 
        prefix="Email" 
        field="email"
        errors={state.errors}
      />
              <Button type="submit" disabled={state.submitting} sx={styles.form.button}>
                Sign Up
              </Button>
            
            </Box>
            </form>
            <Box sx={styles.partner}>
              {/* <Text as="span">Sponsored by:</Text>
              <Box as="div">
                <Image
                  loading="lazy"
                  src={img1}
                  width="100"
                  height="28"
                  alt=""
                />
              </Box> */}
              {/* <Box as="div">
                <Image
                  loading="lazy"
                  width="85"
                  height="28"
                  src={img2}
                  alt=""
                />
              </Box> */}
              {/* <Box as="div">
                <Image
                  loading="lazy"
                  width="123"
                  height="24"
                  src={img3}
                  alt=""
                /> */}
              {/* </Box> */}
            </Box>
          </Box>
          <Box sx={styles.image}>
            <Image src={bannerImg} width="300" height="652" alt="" />
          </Box>
        </Grid>
      </Container>
    </Box>
  );
};

export default Banner;

const styles = {
  banner: {
    pt: ['110px', null, null, null, '150px', '200px'],
    pb: ['50px', null, null, null, '60px', null, '0'],
    backgroundColor: '#F6F8FB',
    overflow: 'hidden',
  },
  container: {
    width: [null, null, null, null, null, null, '1390px'],
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: ['1fr', null, null, '3fr 1fr'],
    gridGap: '0',
  },
  content: {
    h3: {
      color: 'black',
      fontWeight: 'bold',
      lineHeight: [1.39],
      letterSpacing: ['-.7px', '-1.5px'],
      mb: ['15px', null, null, null, '20px'],
      width: ['100%'],
      maxWidth: ['100%', null, null, '90%', '100%', '650px'],
      fontSize: [6, null, null, '36px', null, '55px', 9],
    },
    p: {
      fontSize: [1, null, null, 2, null, 3],
      lineHeight: ['26px', null, null, null, 2.33],
      color: 'text_secondary',
      mb: ['20px', null, null, null, null, '30px'],
      width: ['100%'],
      maxWidth: ['100%', null, null, null, null, '650px'],
      br: {
        display: ['none', null, null, null, 'inherit'],
      },
    },
  },
  form: {
    mb: ['30px', null, null, null, null, '60px'],
    display: ['flex'],
    input: {
      borderRadius: ['4px'],
     
      backgroundColor: '#fff',
      width: ['240px', null, null, null, '315px', null, '375px'],
      height: ['45px', null, null, '55px', null, null, '65px'],
      padding: ['0 15px', null, null, '0 25px'],
      fontSize: [1, null, null, 2],
      border: 'none',
      borderRadius: '0px',
      outline: 'none',
      boxShadow: '0px 10px 50px rgba(48, 98, 145, 0.08)',
    },
    button: {
      fontSize: [1, null, null, null, 2, '20px'],
      fontFamily: "LotaGrotesque",
      borderRadius: ['4px'],
      padding: ['0 15px'],
      ml: ['10px'],
      width: ['auto', null, null, null, '180px'],
    },
  },
  image: {
    img: {
      display: 'flex',
      mixBlendMode: 'darken',
      position: 'relative',
margin: "0 auto",
      top: ['0', null, null, null, null, '-40px'],
      maxWidth: ['100%', null, null, null, null, null, 'none'],
    },
  },
  partner: {
    display: 'flex',
    flexWrap: 'wrap',
    alignItems: 'center',
    mb: ['40px'],
    '> div + div': {
      ml: ['10px', null, null, '20px', null, '30px'],
    },
    img: {
      display: 'flex',
    },
    span: {
      fontSize: [1, null, null, null, 2],
      color: '#566272',
      lineHeight: [1],
      opacity: 0.6,
      display: 'block',
      mb: ['20px', null, null, null, '0px'],
      mr: [null, null, null, null, '20px'],
      flex: ['0 0 100%', null, null, null, '0 0 auto'],
    },
  },
};
