import Box from "@mui/material/Box";
import { useTheme } from "@mui/material/styles";
import React from "react";

type SvgContainerProps = {
  children: React.ReactNode;
};

const SvgContainer = ({ children }: SvgContainerProps) => {
  const theme = useTheme();
  return (
    <Box
      sx={{
        svg: { height: "100%", width: "100%" },
        ".fill-primary": { fill: theme.palette.primary.light },
        ".fill-secondary": { fill: theme.palette.secondary.light },
        ".fill-error": { fill: theme.palette.error.light },
        ".fill-success": { fill: theme.palette.success.light },
        ".fill-warning": { fill: theme.palette.warning.light },
        ".fill-paper": { fill: theme.palette.background.paper },
      }}
    >
      {children}
    </Box>
  );
};

export default SvgContainer;
