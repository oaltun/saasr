import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { PropsWithChildren } from 'react'

type Props = {
  title: string;
}

export const SubSection = (props: PropsWithChildren<Props>) => {



  return (
    <Box sx={{ mt: 1 }}>
      <Typography variant="h3" gutterBottom>{props.title}</Typography>
      {props.children}
    </Box>
  )

};

export default SubSection;
