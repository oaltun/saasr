import { SxProps, Theme } from '@mui/material';
import Grid from '@mui/material/Grid/Grid';
import { ResponsiveStyleValue } from '@mui/system';
import { PropsWithChildren } from 'react'
import { debugSx } from '../utils/debugUtils';

type Props = {
  sx?: SxProps<Theme>;
  justifyContent?: string;
}

export const GridPage = (props: PropsWithChildren<Props>) => {
  return (
    <Grid
      container
      spacing={2}
      pt={6}
      margin="auto"
      justifyContent={props.justifyContent ?? "flex-start"}

      sx={debugSx(props.sx)}

      xs={12}

    >
      {props.children}
    </Grid>
  )
};

