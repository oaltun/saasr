import { SxProps, Theme } from '@mui/material';
import Grid from '@mui/material/Grid/Grid';
import { ResponsiveStyleValue } from '@mui/system';
import { PropsWithChildren } from 'react'
import { debugSx } from '../utils/debugUtils';

type Props = {
  justifyContent?: string;
  alignItems?: string;
  xs?: number;
  md?: number;
  sx?: SxProps<Theme>;
}

export const GridCol = (props: PropsWithChildren<Props>) => {
  return (
    <Grid
      item
      container
      spacing={2}
      xs={props.xs ?? 12}
      md={props.md ?? undefined}
      justifyContent={props.justifyContent ?? "left"}
      alignItems={props.alignItems ?? undefined}
      sx={debugSx(props.sx)}
    >
      {props.children}
    </Grid>
  )
};

