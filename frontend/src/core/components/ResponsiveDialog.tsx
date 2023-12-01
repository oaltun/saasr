import { Dialog, useTheme } from '@mui/material';
import useMediaQuery from '@mui/material/useMediaQuery';

export function ResponsiveDialog(props: any) {
  const theme = useTheme();
  const fullScreen = useMediaQuery(theme.breakpoints.down('md'));

  return <Dialog {...props} fullScreen={fullScreen} />;
}


