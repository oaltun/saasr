import { SxProps, Theme } from "@mui/material";
import Grid from "@mui/material/Grid/Grid";
import { debugSx } from "../utils/debugUtils";

export type GridBrProps = {
  sx?: SxProps<Theme>;
}

export const GridBr = (props: GridBrProps) => {
  return (
    <Grid item xs={12}
      sx={debugSx(props.sx)}
    >
    </Grid>
  );
};
