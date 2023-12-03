import { SxProps, Theme } from '@mui/material';
import Grid from '@mui/material/Grid/Grid';
import { ResponsiveStyleValue } from '@mui/system';
import { PropsWithChildren } from 'react'
import { DEBUG } from '../config/debug';
import { debugSx } from '../utils/debugUtils';
import { pseudoRandomIntFromInterval } from '../utils/randomUtils';

type Props = {
  mb?: number;
  mt?: number;
  sx?: SxProps<Theme>;

  xs?: number;
  sm?: number;
  md?: number;
  lg?: number;
  xl?: number;

  spacing?: number;
  justifyContent?: string;
}
// ======= //
// RENDER
// ======= //
// MUI page sizes: xs, sm, md, lg, and xl
// when you set a value for one, it is valid for larger page sizes too.
// unless that value for larger is specified too.
export const GridSection = (props: PropsWithChildren<Props>) => {


  return (
    <Grid
      item
      container
      justifyContent={props.justifyContent ?? "left"}
      sx={debugSx(props.sx)}

      xs={props.xs ?? 12}
      sm={props.sm ?? undefined}
      md={props.sm ?? undefined}
      lg={props.lg ?? 8}
      xl={props.xl ?? undefined}
      spacing={props.spacing ?? undefined}
    >
      {props.children}
    </Grid >
  )
};

