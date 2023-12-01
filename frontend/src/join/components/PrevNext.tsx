import { Button, Grid } from '@mui/material';
import { PropsWithChildren } from 'react'
import { GridCol } from '../../core/components/GridCol';
import { GridRow } from '../../core/components/GridRow';
import { GridSection } from '../../core/components/GridSection';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';


type Props = {
  activeStep: number;
  handleBack: any;
  handleNext: any;
  makePayment: any;
  steps: any[]
}

export const PrevNext = (
  props: PropsWithChildren<Props>
) => {

  console.log(["props.activeStep:", props.activeStep])
  return <Grid item container
    xs={12}
    justifyContent="center"
    component="form"
    onSubmit={(event) => {
      console.log("submitted");
      if (props.activeStep === props.steps.length - 1)
        props.makePayment();
      else
        props.handleNext();
      event.preventDefault();
    }}
  >
    {props.children}

    <GridRow xs={12} >
      <GridCol xs={12} justifyContent="center">
        <Grid item>
          <Button
            color="inherit"
            disabled={
              props.activeStep === 0
            }
            onClick={() =>
              props.handleBack()
            }
            sx={{ mr: 1 }}
          >
            <ChevronLeftIcon />
            Back
          </Button>

          {props.activeStep
            === props.steps.length - 1
            ? (
              <Button
                type="submit"
              >
                Make Payment
              </Button>)
            : (
              <Button
                type="submit"
              >
                Next
                <ChevronRightIcon />
              </Button>
            )
          }
        </Grid>

      </GridCol>

    </GridRow>
  </Grid>;


};

