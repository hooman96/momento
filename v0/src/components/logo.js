import { jsx, Image } from 'theme-ui';
import { Link } from 'components/link';
import logo from 'assets/logo.svg';

export default function Logo() {
  return (
    <Link
      path="/"
      sx={{
        variant: 'links.logo',
      }}
    >
      <Image
        src={logo}
        width="100"
        height="15"
        sx={{ display: 'flex' }}
        alt="batch logo"
      />
    </Link>
  );
}
