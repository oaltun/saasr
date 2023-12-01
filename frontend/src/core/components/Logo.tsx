import { Link } from "@mui/material";
import Box, { BoxProps } from "@mui/material/Box";

export type LogoProps = {
  colored?: boolean;
  size?: number;
} & BoxProps;

export const Logo = ({
  colored = false,
  size = 40,
  ...boxProps
}: LogoProps) => {
  return (
    <Box {...boxProps}>
      <Link href="/">
        <img alt="Logo" src="saasr_logo_full_40x187.png" />
      </Link>
    </Box>
  );
};

export default Logo;
