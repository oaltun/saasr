import { Color, SxProps, Theme } from '@mui/material';
import Grid from '@mui/material/Grid/Grid';
import { PropsWithChildren } from 'react'
import { debugSx } from '../utils/debugUtils';

type Props = {
  justifyContent?: string;
  alignItems?: string;
  xs?: number;
  md?: number;
  spacing?: number;
  gap?: number;
  mb?: number;
  sx?: SxProps<Theme>;

}

export const GridRow = (props: PropsWithChildren<Props>) => {


  return (
    <Grid item container
      spacing={props.spacing ?? 2}
      xs={props.xs ?? 12}
      justifyContent={props.justifyContent ?? "left"}
      alignItems={props.alignItems ?? "center"}
      mb={props.mb ?? 2}
      sx={debugSx(props.sx)}
    >
      {props.children}
    </Grid>
  )
};

