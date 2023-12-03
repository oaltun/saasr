import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import { PropsWithChildren } from 'react'

type Props = {
  // title: string;
}

export const Important = (props: PropsWithChildren<Props>) => {
  return (
    <Typography variant="h5" component="span">{props.children}</Typography>
  )
};

export default Important;
