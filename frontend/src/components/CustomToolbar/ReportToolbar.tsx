import { GridToolbarColumnsButton, GridToolbarContainer, GridToolbarFilterButton } from "@mui/x-data-grid";
import GridExcelExportMenuItem from "../ExportToExcel/ExportToExcel";
import { Box } from "@mui/material";
function ReportToolbar(props) {
    
    return (
        <GridToolbarContainer>
            <GridToolbarColumnsButton />
            <GridToolbarFilterButton />
            <Box flex={1}/>
            <GridExcelExportMenuItem columns={props.columns} filename={props.filename}/>
        </GridToolbarContainer>
    );
}

export default ReportToolbar;
