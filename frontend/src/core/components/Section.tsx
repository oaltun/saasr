import { CardActionArea, CardActions, Grid, Paper, SxProps, Theme } from "@mui/material";
import Card from "@mui/material/Card/Card";
import CardContent from "@mui/material/CardContent/CardContent";
import CardHeader from "@mui/material/CardHeader/CardHeader";
import { PropsWithChildren } from 'react'
import { GridPage } from "./GridPage";

type Props = {
  title?: string | React.ReactNode;
  sx?: SxProps<Theme>;
  onClick?: React.MouseEventHandler<HTMLDivElement>;
  actions?: string | React.ReactNode;
}

export const Section = (props: PropsWithChildren<Props>) => {
  const sx = { border: 1, width: '100%', ...props.sx }
  return (
    <Card sx={sx} onClick={props.onClick}>
      {props.title && <CardHeader title={props.title} />}
      <CardContent >
        <Grid container xs={12} justifyContent="center">
          <Grid item xs={12}>
            {props.children}
          </Grid>
        </Grid>

      </CardContent>
      {props.actions && <CardActions>
        {props.actions}
      </CardActions>}


    </Card >
  )
};

export default Section;
